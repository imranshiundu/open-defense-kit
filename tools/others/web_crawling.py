from core import ODKTool, ODKToolsCollection, console

from rich.panel import Panel
from rich.prompt import Prompt
from rich import box


class GoSpider(ODKTool):
    TITLE = "Gospider"
    DESCRIPTION = "Gospider - Fast web spider written in Go"
    INSTALL_COMMANDS = ["sudo go get -u github.com/jaeles-project/gospider"]
    PROJECT_URL = "https://github.com/jaeles-project/gospider"

    def __init__(self):
        super().__init__(runnable = False)


class WebCrawlingTools(ODKToolsCollection):
    TITLE = "Web crawling"
    TOOLS = [GoSpider()]

if __name__ == "__main__":
    tools = WebCrawlingTools()
    tools.show_options()
