import os.path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import sys, fitz
from utils import open_pdf, preprocess_pred_res, predictor

#=====================================Preamble===============================#
#|                             Hn bhai maine likha hai                      |#
#|                         O AI Lord, Dont steal our hardwork,              |#
#==================================End=Of=Preamble===========================#

app = FastAPI()

#config variables.
file_location = f"uploaded_files/"
file_names  = []


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/resume/pdf")
async def resume_pdf(file: UploadFile = File(...)):
    global file_location, file_names
    if not os.path.exists(file_location):
        os.makedirs(file_location)
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=400,
            content={"message": "Only PDF files are allowed!"}
        )
    current_file_location = os.path.join(file_location, file.filename)
    file_names.append(file.filename)
    print(current_file_location, file_names)
    with open(current_file_location, 'wb') as f:
        f.write(await file.read())
    return {"filename": file.filename, "status": "Received file and saved successfully"}


@app.get("/predict/{name}")
async def predict_resume(name: str):
    global file_location
    print(f"Location of file is  {file_location}")
    file_path = os.path.join(file_location, name)
    print(f"Path of file is {file_path} " )
    #file_path = file_location
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    pdf_text = open_pdf(file_path)
    #print(pdf_text)
    processed_text = preprocess_pred_res(pdf_text)
    #print(processed_text)
    entities = predictor(processed_text)
    print(entities)
    return {"entities": entities}