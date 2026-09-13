from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ComplaintData(BaseModel):
    complaint_source: str | None = None
    customer_name: str | None = None
    product_name: str | None = None
    product_strength: str | None = None
    batch_number: str | None = None
    affected_quantity: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None
    originating_site: str | None = None
    impacted_material: str | None = None
    complaint_category: str | None = None
    complaint_description: str | None = None
    severity: str | None = None
    suggested_action: str | None = None
    risk_assessment: str | None = None
    status: str = "Pending Triage"


class CopilotRequest(BaseModel):
    message: str = Field(min_length=2)
    current_data: ComplaintData | None = None


class CopilotResponse(BaseModel):
    extracted_data: ComplaintData
    missing_fields: list[str]
    follow_up_question: str | None = None
    assistant_message: str
    mode: str


class ComplaintCreate(ComplaintData):
    pass


class ComplaintResponse(ComplaintData):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

