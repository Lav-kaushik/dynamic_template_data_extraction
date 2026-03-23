from pydantic import BaseModel
from typing import Any

class InitialResponse(BaseModel):
    thread_id: str
    file_name: str
    extracted_data: dict[str, Any]
    template: dict[str, Any]
    suggested_additional_data: dict[str, Any]
    confidence: float

class HumanRequest(BaseModel):
    thread_id: str
    file_name: str
    requested_additional_data_template: dict[str, str]
    additional_prompt: str


class AdditionalDataResponse(BaseModel):
    thread_id: str
    file_name: str
    extracted_additional_data: dict[str, Any]
    additonal_extracted_info: str