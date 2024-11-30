import io
import os
import random
import json
from textwrap import indent
import spacy
import pickle
import re
import sys, fitz
import pymupdf
import nltk
import pandas as pd
import  docx2txt
from datetime import datetime
from dateutil import relativedelta
import constants as cs
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import defaultdict


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

'''
Below code is v2
'''
def extract_text_from_pdf(file_path):
    """
    Function to extract text from pdf file
    """
    if not isinstance(file_path, io.BytesIO):
        with open(file_path, "rb") as fh:
            try:
                for page in PDFPage.get_pages(
                    fh,
                    caching=True,
                    check_extractable=True
                ):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()

                    converter = TextConverter(
                        resource_manager,
                        fake_file_handle,
                        laparams=LAParams()

                    )
                    page_interpretor = PDFPage.get_pages(
                        resource_manager,
                        converter
                    )
                    page_interpretor = PDFPageInterpreter(
                        resource_manager,
                        converter
                    )
                    page_interpretor.process_page(page)
                    text = fake_file_handle.getvalue()
                    yield text

                    converter.close()
                    fake_file_handle.close()
            except PDFSyntaxError:
                return
    else:
        #incase file is not in drive, extracting a remote file
        try:
            for page in PDFPage.get_pages(
                file_path,
                caching=True,
                check_extractable=True
            ):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(
                    resource_manager,
                    fake_file_handle,
                    laparams=LAParams()
                )
                page_interpretor = PDFPageInterpreter(
                    resource_manager,
                    converter
                )
                page_interpretor.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return

def extract_text_from_docx(doc_path):
    try:
        temp = docx2txt.process(doc_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except KeyError:
        return ' '

def extract_text(file_path, ext):
    """
    This is used to extract text from pdf, and also call the correct functionn
    accordingly.
    """
    text = ''
    if ext == '.pdf':
        for page in extract_text_from_pdf(file_path):
            text += ' ' + page
    elif ext == '.docx':
        text = extract_text_from_docx(file_path)