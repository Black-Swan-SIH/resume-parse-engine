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
         "name": " ",
         "email": "",
         "mobile_number": "",
         "skills": [],
         "college_name": null,
         "degree": [""],
         "designation": [""],
         "experience": [""],
         "company_name": null,
         "no_of_pages": 2,
         "total_exp": null,
         "total_experience": 0.0,
         "linkedin": null
     }
     ```

4. **(POST) `/matching/short`**  
   - **Description**: Processes the provided JSON data and returns profile and relevancy scores.  
   - **Output**:  
     ```json
     {
         "profile_score": 85.0,
         "relevancy_score": 90.0
     }
     ```

5. **(POST) `/matching/longVerbose`**  
   - **Description**: Processes the provided JSON data and returns detailed profile comparison information.  
   - **Output**:  
     ```json
     {
         "profile_score": 85.0,
         "relevancy_score": 90.0,
         "candidates": [
             {
                 "name": "John Doe",
                 "intersection_score": 75.0,
                 "cosine_similarity": 85.0,
                 "jaccard_similarity": 60.0,
                 "overall_similarity": 70.0
             },
             {
                 "name": "Jane Doe",
                 "intersection_score": 65.0,
                 "cosine_similarity": 75.0,
                 "jaccard_similarity": 55.0,
                 "overall_similarity": 60.0
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
\