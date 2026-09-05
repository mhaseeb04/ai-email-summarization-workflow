from typing import TypedDict, List

class AgentState(TypedDict):
    unread_emails: List[dict]
    summary: str
    approved: bool
