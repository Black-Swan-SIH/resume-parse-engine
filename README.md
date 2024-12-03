# Resume Parser API

---

<span style="color:red">**THIS IS NOT THE MATCHING ENGINE**</span>

---

## Steps to Run

1. Install all dependencies from `requirements.txt`.  
2. Activate the virtual environment (`venv`).  
3. Start the API.  

---

## Current API Routes

1. **(POST) `/resume/pdf`**  
   - **Description**: Upload your resume as `form-data`.  
     - Key: `file`  
     - MIME Type: `application/pdf`  
   - **Output**:  
     ```json
     {
         "filename": "da.pdf",
         "status": "Received file and saved successfully"
     }
     ```

2. **(GET) `/predict/<filename.pdf>`**  
   - **Description**: Fetch the predicted output for the uploaded file.  
   - **Output**:  
     ```json
     {
         "entities": [
             {
                 "label": "Entity 1",
                 "text": "Entity Value"
             },
             {
                 "label": "Entity 2",
                 "text": "Entity Value"
             }
         ]
     }
     ```
3. **(NEW!!!) (POST) `/resume/beta`**  
   - **Description**: Newer, Optimised and Faster Method to get predictions.  
     - Key: `file`  
     - MIME Type: `application/pdf`  
   - **Output**:  
     ```json
      {
         "entities": [
             {
                 "label": "Entity 1",
                 "text": "Entity Value"
             },
             {
                 "label": "Entity 2",
                 "text": "Entity Value"
             }
         ]
     }
     ```

---

## Notes

- The current implementation uses **V1 of the model**.  
- A new model is under development, but the output structure will remain the same.  
- Enjoy using the current version in the meantime!

---

## To-Do List

- [ ] Add OCR support using Tesseract.  
- [ ] Add Matching Engine.
- [ ] Add JD Parser. 
- [ ] ~~Your Mom~~ .  
