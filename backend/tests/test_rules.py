from app.agent.nodes import _rule_based


def test_extracts_demo_complaint():
    message = (
        "Apollo Pharmacy reported 12 discoloured capsules in Amoxicillin Capsules "
        "500 mg. Batch AMX240602, manufactured March 2026, expiry February 2028."
    )
    result = _rule_based(message, {})
    assert result["customer_name"] == "Apollo Pharmacy"
    assert result["batch_number"] == "AMX240602"
    assert result["affected_quantity"] == "12 discoloured capsules" or "12" in result["affected_quantity"]
    assert result["severity"] == "Major"

