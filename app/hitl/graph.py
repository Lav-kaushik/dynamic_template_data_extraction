import os
import time
from typing import Any, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from app.services import llm_service
from app.hitl.registry import SCHEMA_REGISTRY, TYPE_MAPPING
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, HumanMessage

checkpointer = MemorySaver()

class graph_state(TypedDict):
    thread_id: str
    file_name: str
    file_content: str
    extracted_data: dict[str, Any]
    suggested_additional_data: dict[str, Any]
    requested_additional_data_template: dict[str, str]
    extracted_additional_data: dict[str, Any]
    additional_prompt: str
    additonal_extracted_info: str
    template: dict[str, str]
    confidence: float


def extract_data(state: graph_state) -> graph_state:
    # Extract just the filename without the extension, e.g. "resume.pdf" -> "resume"
    base_name = os.path.splitext(state.get("file_name", ""))[0].lower()

    schema = SCHEMA_REGISTRY.get(base_name)

    if not schema:
        raise ValueError(f"No schema defined in SCHEMA_REGISTRY for file: {state.get('file_name')}")

    # Wrap the user's schema inside a Pydantic model for structured output
    class SubmitExtractionResults(TypedDict):
        """Submit the final extracted data, suggestions, and confidence score."""
        extracted_data: schema
        suggested_additional_data: dict[str, Any]
        confidence: float

    # Extract field descriptions from the schema to help the agent focus
    schema_fields = ""
    if hasattr(schema, "__annotations__"):
        schema_fields = "\n".join([f"- {k}" for k in schema.__annotations__.keys()])

    # Create the agent with structured output
    agent = llm_service.get_agent(SubmitExtractionResults)

    # Build messages for the agent
    system_msg = SystemMessage(content=(
        "You are an expert data extraction assistant.\n"
        "Your task is to carefully read the provided document and extract information precisely matching the required schema.\n"
        "Rules for handling missing data:\n"
        "- For string fields: if no relevant data is found, set the value to an empty string \"\".\n"
        "- For list fields: if no relevant data is found, set the value to an empty list [].\n"
        "- For int/float fields: if no relevant data is found, leave them as 0.\n"
        "- NEVER guess, fabricate, or hallucinate data. Only extract what is explicitly present in the document.\n"
        "For `suggested_additional_data`, proactively identify and suggest 2-4 valuable pieces of information that are clearly present in the document but NOT covered by the main schema. Only include data that actually exists in the document.\n"
        "You must also provide a confidence score between 0.0 and 1.0 evaluating the quality of your extraction.\n"
        "- High confidence (0.9-1.0): document contains clear information for all or most fields.\n"
        "- Lower confidence: ambiguity or missing information for several fields."
    ))

    human_msg = HumanMessage(content=(
        f"File Name: {state.get('file_name', 'unknown')}\n\n"
        f"File Content:\n{state.get('file_content', '')}\n\n"
        f"Extract the data for the following fields:\n"
        f"{schema_fields}"
    ))

    # Invoke the agent
    try:
        t_llm = time.time()
        agent_response = agent.invoke({"messages": [system_msg, human_msg]})

        print(f"[TIMER] Agent call (extract_data): {time.time() - t_llm:.2f}s")

        result = agent_response["structured_response"]
    except Exception as e:
        print(f"[WARN] Structured extraction failed: {e}")
        raise RuntimeError(f"Structured extraction failed: {e}")
    print("Initial Extraction:", result)

    # Convert the TypedDict schema to a readable dictionary of fields
    template_info = {}
    if hasattr(schema, "__annotations__"):
        for field, f_type in schema.__annotations__.items():
            type_str = str(f_type).replace("<class '", "").replace("'>", "")
            template_info[field] = type_str

    return {
        "extracted_data": result["extracted_data"],
        "template": template_info,
        "confidence": result["confidence"],
        "suggested_additional_data": result["suggested_additional_data"]
    }

def human_node(state: graph_state) -> graph_state:
    pass

def extract_additional_data(state: graph_state) -> graph_state:
    requested_additional_data_template = state.get("requested_additional_data_template", {})
    extracted_additional_data = {}

    if requested_additional_data_template:

        dynamic_fields = {}
        # Keep a mapping of sanitized_key -> original_key to restore names later
        key_mapping = {}

        for key, value in requested_additional_data_template.items():
            python_type = TYPE_MAPPING.get(value)
            if python_type:
                # Sanitize key: replace spaces with underscores for valid Python identifiers
                safe_key = key.replace(" ", "_")
                dynamic_fields[safe_key] = python_type
                key_mapping[safe_key] = key

        DynamicSchema = TypedDict(
            "DynamicSchema",
            dynamic_fields
        )

        class AdditionalExtractionResponse(TypedDict):
            extracted_fields: DynamicSchema
            additional_extracted_info: str
            confidence: float

        # Create the agent with structured output
        agent = llm_service.get_agent(AdditionalExtractionResponse)

        # Prepare a readable list of keys for the prompt
        keys_to_extract = "\n".join([f"- {k}: {v}" for k, v in requested_additional_data_template.items()])

        system_msg = SystemMessage(content=(
            "You are an expert data extraction assistant.\n"
            "Your task is to search the provided document for specific pieces of information.\n"
            "Rules for handling missing data:\n"
            "- For string fields: if no relevant data is found, set the value to \"No data found\".\n"
            "- For list fields: if no relevant data is found, set the value to an empty list [].\n"
            "- For int/float fields: if no relevant data is found, leave them as 0.\n"
            "- NEVER guess, fabricate, or hallucinate data. Only extract what is explicitly present in the document."
        ))

        human_msg = HumanMessage(content=(
            f"File Name: {state.get('file_name', 'unknown')}\n\n"
            f"File Content:\n{state.get('file_content', '')}\n\n"
            f"Please specifically look for and extract the following information:\n"
            f"{keys_to_extract}\n\n"
            f"Please also suggest additional data that the user needed according to the additional_extracted_info according to the additional_prompt.\n"
            f"Additional Prompt: {state.get('additional_prompt', '')}\n\n"
        ))

        # Invoke the agent
        agent_response = agent.invoke({"messages": [system_msg, human_msg]})
        result = agent_response["structured_response"]

        # Restore original key names (with spaces) in the output
        for safe_key, value in result["extracted_fields"].items():
            original_key = key_mapping.get(safe_key, safe_key)
            extracted_additional_data[original_key] = value

        print("Additional Extraction", result)
    return {
            "extracted_additional_data": extracted_additional_data,
            "additonal_extracted_info": result["additional_extracted_info"],
            "confidence": result["confidence"]
        }


def build_graph():
    workflow = StateGraph(graph_state)

    workflow.add_node("extract_data", extract_data)
    workflow.add_node("human_node", human_node)
    workflow.add_node("extract_additional_data", extract_additional_data)

    workflow.add_edge(START, "extract_data")
    workflow.add_edge("extract_data", "human_node")
    workflow.add_edge("human_node", "extract_additional_data")
    workflow.add_edge("extract_additional_data", END)
    return workflow.compile(interrupt_before=["human_node"], checkpointer=checkpointer)

app_graph = build_graph()
