from typing import TypedDict

class InsuranceDetails(TypedDict):
    premium_amount: str       # "15,000" as text
    max_age_of_entry: str     # "55 years" as text  
    min_age_of_entry: str     # "18 years" as text
    sum_assured: str          # "₹50,00,000 to ₹1,00,00,000" as text
    benefits: list[str]
    terms_and_conditions: list[str]

