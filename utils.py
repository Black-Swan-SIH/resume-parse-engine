import io
import os
import pandas as pd
import spacy
import re
import fitz
import  docx2txt
import constants as cs
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from datetime import datetime
from dateutil import relativedelta

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

def extract_entities_with_custom_model(custom_text):
    """
    function to extract entities with custom model
    """
    entities = {}
    for ent in custom_text.ents:
        if ent.label_ in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    for key in entities.keys():
        entities[key] = list(set(entities[key]))
    return entities

def extract_name(nlp_text, matcher):
    """
    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param matcher: object of `spacy.matcher.Matcher`
    :return: string of full name
    """
    pattern = [cs.NAME_PATTERN]

    matcher.add('NAME', pattern)

    matches = matcher(nlp_text)

    for _, start, end in matches:
        span = nlp_text[start:end]
        if 'name' not in span.text.lower():
            return span.text

def extract_email(text):
    """
    Helper function to extract email id from text

    :param text: plain text extracted from resumes file
    """
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

def extract_mobile_number(text, custom_regex=None):


    if not custom_regex:
        mob_num_regex = r'''(\(?\d{3}\)?[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)
                                [-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'''
        phone = re.findall(re.compile(mob_num_regex), text)
    else:
        phone = re.findall(re.compile(custom_regex), text)
    if phone:
        number = ''.join(phone[0])
        return number

#Checkpoint 1
def extract_skills(nlp_text, noun_chunks, skills_file=None):
    """
    Function to do dingle dangle
    """
    tokens = [token.text for token in nlp_text if not token.is_stop]
    if not skills_file:
        data = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'skills.csv')
        )
    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

def extract_linkedin(text):
    """
    function to extract LinkedIn URL from text

    """
    # Regular expression to match LinkedIn URLs
    linkedin_regex = r'(https?://[a-zA-Z0-9.-]+linkedin.com/in/[^ \s]+)'

    linkedin = re.findall(linkedin_regex, text)
    if linkedin:
        return linkedin[0]
    else:
        return None

def extract_entity_sections_grad(text):
    """
    function to extract all the raw text from sections of resume

    """
    text_split = [i.strip() for i in text.split('\n')]
    # sections_in_resume = [i for i in text_split if i.lower() in sections]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS_GRAD)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_GRAD:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)

    # entity_key = False
    # for entity in entities.keys():
    #     sub_entities = {}
    #     for entry in entities[entity]:
    #         if u'\u2022' not in entry:
    #             sub_entities[entry] = []
    #             entity_key = entry
    #         elif entity_key:
    #             sub_entities[entity_key].append(entry)
    #     entities[entity] = sub_entities

    # pprint.pprint(entities)

    # make entities that are not found None
    # for entity in cs.RESUME_SECTIONS:
    #     if entity not in entities.keys():
    #         entities[entity] = None
    return entities

def get_total_experience(experience_list):
    """
    Wrapper function to extract total months of experience from a resumes

    :param experience_list: list of experience text extracted
    :return: total months of experience
    """
    exp_ = []
    for line in experience_list:
        experience = re.search(
            r'(?P<fmonth>\w+.\d+)\s*(\D|to)\s*(?P<smonth>\w+.\d+|present)',
            line,
            re.I
        )
        if experience:
            exp_.append(experience.groups())
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return total_experience_in_months

def get_number_of_months_from_dates(date1, date2):
    """
    Helper function to extract total months of experience from a resumes

    :param date1: Starting date
    :param date2: Ending date
    :return: months of experience from date1 to date2
    """
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience
def get_number_of_pages(file_name):
    try:
        if isinstance(file_name, io.BytesIO):
            # for remote pdf file
            count = 0
            for page in PDFPage.get_pages(
                    file_name,
                    caching=True,
                    check_extractable=True
            ):
                count += 1
            return count
        else:
            # for local pdf file
            if file_name.endswith('.pdf'):
                count = 0
                with open(file_name, 'rb') as fh:
                    for page in PDFPage.get_pages(
                            fh,
                            caching=True,
                            check_extractable=True
                    ):
                        count += 1
                return count
            else:
                return None
    except PDFSyntaxError:
        return None