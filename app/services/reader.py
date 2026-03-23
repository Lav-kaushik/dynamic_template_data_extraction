import os
import tempfile
import pymupdf4llm
import time

async def read(file) -> str:
    tmp_path = None # Initialize tmp_path to None
    try:
        t0 = time.time()
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir="/tmp") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        md_text = pymupdf4llm.to_markdown(tmp_path)
        print(f"[TIMER] PDF read: {time.time() - t0:.2f}s")
    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed to read PDF: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
    return md_text