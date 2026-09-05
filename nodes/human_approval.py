def human_approval(state):
    print("\n--- Generated Email Summary ---")
    print(state["summary"])

    while True:
        decision = input("Type 'approve', 'edit', or 'reject': ").strip().lower()

        if decision == "approve":
            return {"approved": True}

        if decision == "edit":
            new_summary = input("\nEnter edited summary:\n")
            return {"summary": new_summary, "approved": True}

        if decision == "reject":
            return {"approved": False}
