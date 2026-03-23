from fastapi import APIRouter , HTTPException , UploadFile , File
from fastapi.exceptions import RequestValidationError
from app.services import reader 
from pathlib import Path
from app.hitl.graph import app_graph
from uuid import uuid4
from app.schemas.response import InitialResponse , AdditionalDataResponse , HumanRequest
import time

router = APIRouter(prefix="/extract")

@router.post("/start_extraction" , response_model=InitialResponse)
async def extract(file: UploadFile = File(...)) -> InitialResponse:
    if not file.content_type:
        raise HTTPException(
            status_code=400 , 
            detail="No file provided"
        )
    file_name = Path(file.filename).stem.replace(" ", "_").lower()
    
    try:
        file_content = await reader.read(file)
    except RuntimeError as e:
        raise HTTPException(
            status_code=500 ,
            detail=str(e)
        )

    thread_id = str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    try:
        t1 = time.time()
        graph_response = app_graph.invoke({
            "thread_id": thread_id,
            "file_name": file_name,
            "file_content": file_content
        } , config)
        print(f"[TIMER] Graph invoke (initial extraction): {time.time() - t1:.2f}s")
    except Exception as e:
        raise HTTPException(
            status_code=500 ,
            detail=f"[ERROR] Failed to extract data: {e}"
        )

    return InitialResponse(
        thread_id=thread_id,
        file_name=file_name,
        extracted_data=graph_response["extracted_data"],
        template=graph_response["template"],
        suggested_additional_data=graph_response["suggested_additional_data"],
        confidence=graph_response["confidence"]
    )
    

@router.post("/resume_extraction" , response_model=AdditionalDataResponse)
async def resume_extraction(request: HumanRequest) -> AdditionalDataResponse:
    try:
        thread_id = request.thread_id
        file_name = request.file_name
        requested_additional_data_template = request.requested_additional_data_template
        additional_prompt = request.additional_prompt

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
    
        state = app_graph.get_state(config)
        if not state.next:
            raise HTTPException(
                status_code=400 ,
                detail="No pending human tasks for this thread"
            )
        
        update_state = {
            "requested_additional_data_template": requested_additional_data_template,
            "additional_prompt": additional_prompt
        }

        app_graph.update_state(
            config=config,
            values=update_state,
        )

        graph_response = app_graph.invoke(None , config)

    except RequestValidationError as e:
        raise HTTPException(
            status_code=422 ,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500 ,
            detail=str(e)
        )

    return AdditionalDataResponse(
        thread_id=thread_id,
        file_name=file_name,
        extracted_additional_data=graph_response["extracted_additional_data"],
        additonal_extracted_info=graph_response["additonal_extracted_info"],
        confidence=graph_response["confidence"]
    )
