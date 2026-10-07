from src.property_spend import WorkItem, approve_work


def test_monthly_cap_rejects_item_after_allowance_is_used() -> None:
    item = WorkItem("inspection reminder", "building-17", 5.0, "remind")
    assert approve_work(item, 0.0, monthly_cap_usd=5.0)
    assert not approve_work(item, 5.0, monthly_cap_usd=5.0)
