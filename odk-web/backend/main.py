from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import sys
import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware


BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from catalog import get_categories_payload, get_category_by_id, get_tool_by_id, get_tools_payload
from config import get_tools_dir
from os_detect import CURRENT_OS

class JobManager:
    def __init__(self):
        self.jobs = {} # job_id -> { process, buffer, status, info }
        self.active_job_id = None

    async def create_job(self, tool_id=None, action=None, option_index=None, category_id=None, target=None):
        job_id = str(int(asyncio.get_event_loop().time() * 1000))
        
        args = [sys.executable, str(BACKEND_DIR / "runner.py")]
        title = "Action"
        if tool_id:
            args.extend(["--tool-id", str(tool_id)])
            if action:
                args.extend(["--action", action])
            if option_index is not None:
                args.extend(["--option-index", str(option_index)])
            tool = get_tool_by_id(tool_id)
            title = tool["title"] if tool else "Tool"
        elif category_id:
            args.extend(["--category-id", str(category_id)])
            args.extend(["--action", "install-missing"])
            category = get_category_by_id(category_id)
            title = category["label"] if category else "Category"
        
        env = os.environ.copy()
        if target:
            env["ODK_TARGET"] = target

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(get_tools_dir()),
            env=env,
        )

        self.jobs[job_id] = {
            "id": job_id,
            "title": title,
            "status": "running",
            "process": process,
            "buffer": "",
            "startedAt": datetime.now(timezone.utc).isoformat(),
        }
        self.active_job_id = job_id
        
        asyncio.create_task(self._consume_output(job_id))
        return job_id

    async def _consume_output(self, job_id):
        job = self.jobs.get(job_id)
        if not job: return
        process = job["process"]
        
        while True:
            line = await process.stdout.read(4096)
            if not line:
                break
            text = line.decode(errors="replace")
            job["buffer"] += text
            
        exit_code = await process.wait()
        job["status"] = "finished"
        job["exit_code"] = exit_code
        if self.active_job_id == job_id:
            # We keep it as active until a new one starts or it's cleared
            pass

job_manager = JobManager()

app = FastAPI(title="Open Defense Kit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Open Defense Kit (ODK) API"}


@app.get("/api/system")
def get_system():
    return {
        "os": {
            "system": CURRENT_OS.system,
            "distroId": CURRENT_OS.distro_id,
            "distroLike": CURRENT_OS.distro_like,
            "version": CURRENT_OS.distro_version,
            "packageManager": CURRENT_OS.pkg_manager,
            "isRoot": CURRENT_OS.is_root,
            "arch": CURRENT_OS.arch,
            "isWsl": CURRENT_OS.is_wsl,
        },
        "paths": {
            "toolsDir": str(get_tools_dir()),
            "backendDir": str(BACKEND_DIR),
            "repoRoot": str(ROOT_DIR),
        },
        "user": {
            "home": str(Path.home()),
            "name": os.environ.get("USER", os.environ.get("LOGNAME", "")),
        },
    }


@app.get("/api/categories")
def get_categories():
    return get_categories_payload()


@app.get("/api/categories/{category_id}")
def get_category(category_id: int):
    category = get_category_by_id(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.get("/api/tools")
def get_tools():
    return get_tools_payload()


@app.get("/api/tools/{tool_id}")
def get_tool(tool_id: int):
    tool = get_tool_by_id(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@app.get("/api/jobs/active")
def get_active_job():
    if not job_manager.active_job_id:
        return None
    job = job_manager.jobs.get(job_manager.active_job_id)
    if not job:
        return None
    return {
        "id": job["id"],
        "title": job["title"],
        "status": job["status"],
        "startedAt": job["startedAt"],
    }

@app.websocket("/ws/execute")
async def websocket_execute(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        
        job_id = data.get("job_id")
        if not job_id:
            # Create new job
            tool_id = data.get("toolId")
            action = data.get("action")
            option_index = data.get("optionIndex")
            category_id = data.get("categoryId")
            target = data.get("target")
            job_id = await job_manager.create_job(tool_id, action, option_index, category_id, target)
        
        job = job_manager.jobs.get(job_id)
        if not job:
            await websocket.send_json({"type": "error", "message": "Job not found"})
            await websocket.close()
            return

        # Stream existing buffer
        if job["buffer"]:
            await websocket.send_json({"type": "stdout", "data": job["buffer"]})

        last_buffer_pos = len(job["buffer"])
        while job["status"] == "running":
            if len(job["buffer"]) > last_buffer_pos:
                new_data = job["buffer"][last_buffer_pos:]
                await websocket.send_json({"type": "stdout", "data": new_data})
                last_buffer_pos = len(job["buffer"])
            await asyncio.sleep(0.1)

        if len(job["buffer"]) > last_buffer_pos:
            await websocket.send_json({"type": "stdout", "data": job["buffer"][last_buffer_pos:]})
        
        await websocket.send_json({"type": "exit", "code": job.get("exit_code", 0)})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try: await websocket.send_json({"type": "error", "message": str(e)})
        except: pass
    finally:
        try: await websocket.close()
        except: pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
