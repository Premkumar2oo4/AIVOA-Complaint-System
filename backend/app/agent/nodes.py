import json
import re
from langchain_groq import ChatGroq
from ..config import get_settings


FIELDS = [
    "complaint_source", "customer_name", "product_name", "product_strength",
    "batch_number", "affected_quantity", "manufacturing_date", "expiry_date",
    "originating_site", "impacted_material", "complaint_category",
    "complaint_description", "severity", "suggested_action", "risk_assessment"
]
REQUIRED = ["complaint_source", "customer_name", "product_name", "batch_number", "affected_quantity", "complaint_description"]


def _clean_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("The model did not return JSON")
    return json.loads(text[start:end + 1])


def _rule_based(message: str, current: dict) -> dict:
    data = {**current}
    low = message.lower()
    patterns = {
        "batch_number": r"(?:batch|lot)(?:\s*(?:number|no\.?))?\s*[:#-]?\s*([A-Z0-9-]{4,})",
        "affected_quantity": r"(?:affected quantity(?: is|:)?|reported|found|quantity(?: is|:)?)\s*(\d+\s*(?:capsules?|tablets?|units?|drums?|bottles?|packs?)?)",
        "product_strength": r"\b(\d+(?:\.\d+)?\s*(?:mg|g|kg|ml|mcg|%)(?:\s*[A-Z/]+)?)\b",
        "manufacturing_date": r"(?:manufactured|manufacturing date|mfg)\s*(?:in|on|:)?\s*([A-Za-z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        "expiry_date": r"(?:expiry|expires?|exp)\s*(?:in|on|:)?\s*([A-Za-z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            data[field] = match.group(1).strip()

    if "pharmacy" in low:
        data["complaint_source"] = "Pharmacy"
        match = re.search(r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+Pharmacy", message)
        if match:
            data["customer_name"] = f"{match.group(1)} Pharmacy"
    elif "email" in low:
        data["complaint_source"] = "Email"

    product_patterns = [
        r"((?:Amoxicillin|Metformin|Paracetamol|Ibuprofen)[A-Za-z\s-]*?(?:Capsules?|Tablets?|API)?)\s+\d",
        r"product\s*[:#-]?\s*([A-Za-z][A-Za-z\s-]{3,40})"
    ]
    for pattern in product_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            data["product_name"] = match.group(1).strip()
            break

    if any(word in low for word in ["foreign particle", "contamination", "black particle"]):
        data["complaint_category"] = "Foreign Matter Contamination"
        data["severity"] = "Critical"
        data["suggested_action"] = "Quarantine the batch and initiate an urgent manufacturing investigation."
        data["risk_assessment"] = "Potential foreign-matter contamination with high impact on product quality and patient safety."
    elif any(word in low for word in ["discoloured", "discolored", "discolouration", "discoloration"]):
        data["complaint_category"] = "Product Defect - Discoloration"
        data["severity"] = "Major"
        data["suggested_action"] = "Initiate a quality investigation and inspect retained samples and packaging integrity."
        data["risk_assessment"] = "Possible moisture ingress, stability issue, or packaging-seal failure causing discoloration."
    else:
        data.setdefault("severity", "Major")
        data.setdefault("suggested_action", "Initiate quality review and verify the batch manufacturing record.")
        data.setdefault("risk_assessment", "Quality impact requires assessment by the complaint investigation team.")

    if len(message) > 20 and not data.get("complaint_description"):
        data["complaint_description"] = message.strip()
    return data


def extract_complaint(state: dict) -> dict:
    settings = get_settings()
    current = state.get("current_data") or {}
    if not settings.groq_api_key:
        return {"complaint_data": _rule_based(state["message"], current), "mode": "demo"}

    prompt = f"""You extract pharmaceutical customer complaint data. Return only valid JSON.
Allowed keys: {FIELDS}.
Preserve known values from CURRENT DATA and update them using the new message.
Classify severity as Minor, Major, or Critical. Give a concise suggested_action and risk_assessment.
Do not invent identifiers, quantities, customers, dates, products, or sites.
CURRENT DATA: {json.dumps(current)}
NEW MESSAGE: {state['message']}"""
    llm = ChatGroq(api_key=settings.groq_api_key, model=settings.groq_model, temperature=0)
    response = llm.invoke(prompt)
    extracted = _clean_json(response.content)
    return {"complaint_data": {**current, **{k: v for k, v in extracted.items() if k in FIELDS}}, "mode": "groq"}


def validate_complaint(state: dict) -> dict:
    data = state.get("complaint_data", {})
    missing = [field for field in REQUIRED if not data.get(field)]
    labels = {
        "complaint_source": "complaint source", "customer_name": "customer name",
        "product_name": "product name", "batch_number": "batch or lot number",
        "affected_quantity": "affected quantity", "complaint_description": "complaint description"
    }
    follow_up = f"Please provide the {labels[missing[0]]}." if missing else None
    message = (
        f"I extracted the complaint details. I still need the {labels[missing[0]]} before it is complete."
        if missing else "Complaint analysis is complete. Please review the populated form and risk assessment before committing it."
    )
    return {"missing_fields": missing, "follow_up_question": follow_up, "assistant_message": message}

