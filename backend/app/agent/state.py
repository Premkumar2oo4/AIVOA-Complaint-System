from typing import TypedDict


class ComplaintState(TypedDict, total=False):
    message: str
    current_data: dict
    complaint_data: dict
    missing_fields: list[str]
    follow_up_question: str | None
    assistant_message: str
    mode: str

