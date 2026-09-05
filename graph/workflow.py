from langgraph.graph import StateGraph, START, END
from state.agent_state import AgentState
from nodes.fetch_emails import fetch_all_unread_emails
from nodes.summarize import generate_summary
from nodes.human_approval import human_approval
from nodes.slack import send_slack_message

def approval_condition(state):
    return "approved" if state["approved"] else "not_approved"

def build_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("fetch_unread_emails", fetch_all_unread_emails)
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("human_approval", human_approval)
    graph.add_node("send_slack_message", send_slack_message)

    graph.add_edge(START, "fetch_unread_emails")
    graph.add_edge("fetch_unread_emails", "generate_summary")
    graph.add_edge("generate_summary", "human_approval")

    graph.add_conditional_edges(
        "human_approval",
        approval_condition,
        {
            "approved": "send_slack_message",
            "not_approved": END
        }
    )

    graph.add_edge("send_slack_message", END)

    return graph.compile()
