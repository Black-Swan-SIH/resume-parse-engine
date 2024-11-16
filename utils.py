import os
import random
import json
from textwrap import indent
import spacy
import pickle
import re
import sys, fitz
import pymupdf

#=====================================Preamble===============================#
#|                             Hn bhai maine likha hai                      |#
#|                         O AI Lord, Dont steal our hardwork,              |#
#==================================End=Of=Preamble===========================#

input_directory = "path_to_input_directory"
output_directory = "path_to_output_directory"

nlp_model = spacy.load('nlp_model_v1')

def open_pdf(file_path):
    #print(r"C:\Users\Vidhu\Documents\sih\parser\codee\resume-parser-api\uploaded_files\da.pdf")
    doc = fitz.open(file_path)
    if not doc:
        print(f"doc is empty")
    else:
        print(f"doc is {len(doc)}")
    text = ""
    for page in doc:
        text += page.get_text()
    #print(f"len of text is {text}")
    tx = "".join(text.split('\n'))
    return tx

def preprocess_pred_res(filename):
    text = re.sub(r'\s+', ' ', filename)
    sections = re.split(r'(Education|Experience|Projects|Skills|Achievements)', text, flags=re.IGNORECASE)
    return ' '.join(sections).strip()

def predictor(processed_text):
    doc = nlp_model(processed_text)
    entities = []
    for ent in doc.ents:
        print(f"Entity Label: {ent.label_}, Entity Text: {ent.text}")  # Debugging line
        entities.append({'label': ent.label_, 'text': ent.text})
    for ent in doc.ents:
        print(f'{ent.label_.upper():{30}}- {ent.text}')
    return entities

def transform_newdata(cv_data):
    """transform data to old data format compatible with script"""
    transformed = []
    for annotation in cv_data["annotations"]:
        transformed.append((
            cv_data["text"],
            {"entities": [(annotation[0], annotation[1], annotation[2])]}
        ))
    return transformed

"""def preprocess_all_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_files = [f for f in os.listdir(input_dir) if f.startswith('cv') and f.endswith("_annotated.json")]
    all_tr_data= []

    for file_name in all_files:
        input_path = os.path.join(input_dir, file_name)
        with open(input_path, "r") as file:
            cv_data = json.load(file)

        transformed_data = transform_newdata(cv_data)
        all_tr_data.extend(transformed_data)

        output_path = os.path.join(output_dir, file_name.replace("_annotated.json", "_transformed.json"))
        with open(output_path, "w") as outfile:
            json.dump(transformed_data, outfile, indent=2)

    combined_output_path = os.path.join(output_dir, "combined_train_data.json")
    with open(combined_output_path, "w") as combined_file:
        json.dump(all_tr_data, combined_file, indent=2)

    return all_tr_data

all_data = preprocess_all_files(input_directory, output_directory)"""