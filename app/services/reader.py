from pypdf import PdfReader
from io import BytesIO

async def read(file: BytesIO) -> str:
    reader = PdfReader(file)
    content = ""
    for page_num in range(min(len(reader.pages) , 5)):
        data = reader.pages[page_num].extract_text()
        content += (data or "") + '\n'
    print(content)
    return content