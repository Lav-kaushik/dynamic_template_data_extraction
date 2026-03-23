from typing import TypedDict, Literal

class Candidate(TypedDict):
    """
    Schema for a candidate's resume.
    
    Attributes:
        name: Name of the candidate
        email_id: Email of the candidate
        skills: The skills candidate have
        certificates: The certificates that candidate have completed
        project_names: The name of projects candidate have worked on
        technologies_used: The technologies candidate have used to build projects
        is_experienced: Whether the candidate is experienced (yes/no)
    """
    name: str
    email_id: str
    skills: list[str]
    certificates: list[str]
    project_names: list[str]
    technologies_used: list[str]
    is_experienced: Literal["yes", "no"]
