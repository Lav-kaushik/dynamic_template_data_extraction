from typing import TypedDict

class AdmitCard(TypedDict):
    candidate_name: str
    registration_number: str
    exam_date: str
    exam_time: str
    exam_center: str
    