from langchain_google_community import GmailToolkit

toolkit = GmailToolkit()

def fetch_all_unread_emails(state):
    gmail_search_tool = next(
        t for t in toolkit.get_tools()
        if t.__class__.__name__ == "GmailSearch"
    )
    gmail_get_tool = next(
        t for t in toolkit.get_tools()
        if t.__class__.__name__ == "GmailGetMessage"
    )

    emails = []
    next_page_token = REDACTED

    while True:
        messages = gmail_search_tool.run({
            "query": "is:unread",
            "page_token": next_page_token
        })
        if not messages:
            break

        for msg in messages:
            msg_data = gmail_get_tool.run({"message_id": msg["id"]})
            payload = msg_data.get("payload", {})
            headers = {
                h.get("name", "").lower(): h.get("value", "")
                for h in payload.get("headers", [])
            }

            emails.append({
                "from": headers.get("from"),
                "subject": headers.get("subject"),
                "body": msg_data.get("snippet", "")
            })

        next_page_token = REDACTED, "next_page_token", None)
        if not next_page_token:
            REDACTED

    state["unread_emails"] = emails
    print(f"[INFO] Fetched {len(emails)} unread emails.")
    return {"unread_emails": emails}
