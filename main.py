from dotenv import load_dotenv
from graph.workflow import build_workflow

load_dotenv()

initial_state = {
    "unread_emails": [],
    "summary": "",
    "approved": False
}

workflow = build_workflow()
workflow.invoke(initial_state)
