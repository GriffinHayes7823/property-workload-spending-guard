from property_spend import WorkItem, client_from_environment, run_item


def main() -> None:
    client = client_from_environment()
    client.set_monthly_cap(100.0)
    items = [
        WorkItem("maintenance request", "building-17", 25.0, "Summarize the repair request and next action."),
        WorkItem("tenant document", "building-17", 10.0, "Extract the document expiry date."),
        WorkItem("inspection reminder", "building-17", 5.0, "Draft a concise inspection reminder."),
    ]
    spent = 0.0
    for item in items:
        result = run_item(client, item, spent)
        print(f"{item.kind}: {result}")
        if not result.startswith("rejected:"):
            spent += item.monthly_allowance_usd


if __name__ == "__main__":
    main()
