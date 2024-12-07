import os
import shutil
from auth import validate_api_key

from fastapi import FastAPI, File, UploadFile, Depends, Header
from fastapi.responses import JSONResponse
from utils import open_pdf, preprocess_pred_res, predictor
import resume_parser
import aiofiles

#=====================================Preamble===============================#
#|                             Hn bhai maine likha hai                      |#
#|                         O AI Lord, Dont steal our hardwork,              |#
#==================================End=Of=Preamble===========================#

app = FastAPI()

# Config variables
file_location = "uploaded_files/"

async def api_key_auth(x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
@app.get("/")
async def root():
    return {"message": "Hello World"}

def process_resume(file_path):
    try:
        data = resume_parser.resume_result_wrapper(file_path)
        return data
    except Exception as e:
        return {"error": str(e)}



@app.post("/resume/normal")
async def resume_normal(file: UploadFile = File(...)):
    """Handles PDF upload and returns processed entities."""
    # Validate file type
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=400, content={"message": "Only PDF files are allowed!"}
        )

    # Save the file
    if not os.path.exists(file_location):
        os.makedirs(file_location)
    file_path = os.path.join(file_location, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(await file.read())

    # Process the PDF
    try:
        pdf_text = open_pdf(file_path)
        processed_text = preprocess_pred_res(pdf_text)
        entities = predictor(processed_text)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": f"Error during processing: {str(e)}"}
        )

    # Return processed data
    return {"filename": file.filename, "entities": entities}


# @app.post("/resume/beta")
# async def resume_beta(file: UploadFile = File(...)):
#     try:
#         # Validate file type
#         print(f"Content type: {file.content_type}, File size: {len(await file.read())}")
#         if file.content_type != "application/pdf":
#             return JSONResponse(
#                 status_code=400, content={"message": "Only PDF files are allowed!"}
#             )
#
#         # Save the file
#         if not os.path.exists(file_location):
#             os.makedirs(file_location)
#         file_path = os.path.join(file_location, file.filename)
#         async with aiofiles.open(file_path, "wb") as f:
#             file_data = await file.read()
#             await f.write(file_data)
#             print(f"File saved at {file_path}, size: {len(file_data)} bytes")
#
#         # Process the PDF
#         content = resume_parser.resume_result_wrapper(file_path)
#         print(content)
#
#         return {"filename": file.filename, "content": content}
#     except Exception as e:
#         import traceback
#         return JSONResponse(
#             status_code=500,
#             content={"message": f"Error during processing: {str(e)}", "trace": traceback.format_exc()}
#         )


@app.post("/resume/beta")
async def parse_resume(file: UploadFile = File(...),
                       _: str = Depends(api_key_auth),
                       ):
    try:
        # Save the uploaded file to a temporary location
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the resume
        result = process_resume(temp_path)

        # Clean up the temp file
        os.remove(temp_path)

        # Return the result
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)