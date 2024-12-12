import json
import os
import shutil
import time
from http.client import responses
from pydantic import BaseModel
from auth import validate_api_key
from fastapi import FastAPI, File, UploadFile, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from utils import open_pdf, preprocess_pred_res, predictor
import resume_parser
import aiofiles
from matching import compare_profiles_with_expert, compare_profiles_with_board
from scrapy import scrape_page
import requests



app = FastAPI()

file_location = "uploaded_files/"

async def api_key_auth(x_api_key: str = Header(...)):
    validate_api_key(x_api_key)
class URLRequest(BaseModel):
    url: str
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
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=400, content={"message": "Only PDF files are allowed!"}
        )
    if not os.path.exists(file_location):
        os.makedirs(file_location)
    file_path = os.path.join(file_location, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(await file.read())

    try:
        pdf_text = open_pdf(file_path)
        processed_text = preprocess_pred_res(pdf_text)
        entities = predictor(processed_text)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"message": f"Error during processing: {str(e)}"}
        )

    return {"filename": file.filename, "entities": entities}

@app.post("/resume/beta")
async def parse_resume(file: UploadFile = File(...), _: str = Depends(api_key_auth)):
    try:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_resume(temp_path)

        os.remove(temp_path)

        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/matching/short")
async def matching_short(data: dict):
    try:
        result = compare_profiles_with_expert(data)
        profile_score = result.get("profile_score", 0)
        relevancy_score = result.get("relevancy_score", 0)
        return JSONResponse(content={"profile_score": profile_score, "relevancy_score": relevancy_score})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/matching/longVerbose")
async def matching_long_verbose(data: dict):
    try:
        result = compare_profiles_with_expert(data)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/matching/candy")
async def matching_candy(data: dict):
    try:
        result = compare_profiles_with_board(data)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/extraExpert/giveme")
async def send_expert_data(request: URLRequest):
    params = {
        'field': 'all',
        'title': '',
        'designation[]': 'Professor',
        'page': 1,
        'limits': 200  # Set the number of entries per page to 100
    }
    url = request.url
    try:
        time.sleep(2)
        experts = scrape_page(url, params)
        return experts
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)