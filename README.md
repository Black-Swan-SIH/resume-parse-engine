# resume-parser-api

---

<span style="color:red">THIS IS NO THE MATCHING ENGINE</span>

## Steps

1) Install all dependencies from requirement.txt
2) Load venv 
3) Run the api. 

## Current API Routes

1) (POST) **/resume/pdf** - send your resume here in the form of form-data with key "file" and MIME type application/pdf
2) (GET) **/predict/<filename.pdf>** will return the predicted output. 

### Currently using V1 of model, I am working on a new model from scratch, the output will be same till then enjoy with this. 

## ToDo

- [ ] OCR Using tesseract
- [ ] ~~Your Mom~~