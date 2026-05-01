from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the root directory to sys.path so we can import from core and tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from odk import all_tools

app = FastAPI(title="Open Defense Kit API")

# Configure CORS so the React frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Open Defense Kit (ODK) API"}

@app.get("/api/categories")
def get_categories():
    """Return all tool categories."""
    from odk import tool_definitions
    
    categories = []
    # tool_definitions is a list of tuples: (full_title, icon, menu_label)
    # The last one is the update/uninstall manager, so we exclude it or flag it
    for i, (full_title, icon, menu_label) in enumerate(tool_definitions):
        categories.append({
            "id": i + 1,
            "title": full_title,
            "icon": icon,
            "label": menu_label
        })
    return categories

@app.get("/api/tools")
def get_tools():
    """Return a flat list of all tools with their metadata."""
    from core import ODKTool, ODKToolsCollection
    
    tools_list = []
    tool_id_counter = 1
    
    def _extract_tools(items, category_name=""):
        nonlocal tool_id_counter
        for item in items:
            if isinstance(item, ODKToolsCollection):
                _extract_tools(item.TOOLS, item.TITLE)
            elif isinstance(item, ODKTool):
                tools_list.append({
                    "id": tool_id_counter,
                    "title": item.TITLE,
                    "description": getattr(item, "DESCRIPTION", ""),
                    "category": category_name,
                    "tags": getattr(item, "TAGS", []),
                    "installed": item.is_installed if hasattr(item, "is_installed") else False,
                    "projectUrl": getattr(item, "PROJECT_URL", "")
                })
                tool_id_counter += 1

    _extract_tools(all_tools)
    return tools_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
