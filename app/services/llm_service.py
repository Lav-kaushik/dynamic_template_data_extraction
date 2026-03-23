from langchain_groq import ChatGroq
from app.app_configs import settings
import os
from langchain.agents import create_agent
from typing import TypedDict

app_settings = settings.get_settings()

os.environ["GROQ_API_KEY"] = app_settings.GROQ_API_KEY

if not os.environ["GROQ_API_KEY"]:
    raise ValueError("GROQ_API_KEY is not set")

def get_agent(schema: TypedDict):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        max_retries=2
    )

    agent = create_agent(
        model=llm,
        response_format=schema
    )

    return agent

