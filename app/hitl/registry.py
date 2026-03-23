from app.schemas import resume , insurance , admit_card
from typing import Any
# Map the base filename (without extension) to its corresponding schema
SCHEMA_REGISTRY = {
    "resume": resume.Candidate,
    "insurance": insurance.InsuranceDetails,
    "admit_card": admit_card.AdmitCard
}

TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "dict": dict[str, Any],
    "list[str]": list[str]
}
