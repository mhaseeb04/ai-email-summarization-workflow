from langchain_ollama import ChatOllama

def generate_summary(state):
    llm = ChatOllama(model="qwen3-coder:480b-cloud")

    prompt = f"""
You are an AI assistant. Summarize these unread emails clearly.

Emails:
{state['unread_emails']}
"""
    summary = llm.invoke(prompt).content
    state["summary"] = summary
    return {"summary": summary}
