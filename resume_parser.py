import os
import multiprocessing as mp
import io
import spacy
import pprint
from spacy.matcher import Matcher
import utils

class Resume_Parser(object):
    def __init__(
            self,
            resume,
            skills_file,
            cus_regex

    ):
        print("Spacy Model is loading")
        nlp = spacy.load('en_core_web_sm')
        current_directory = os.path.dirname(os.path.abspath(__file__))
        custom_nlp = spacy.load(os.path.join(current_directory, 'models', 'res_model'))
        self.__skills_file = skills_file
        self.__custom_regex = cus_regex
        self.__details = {
            'name':None,
            'email':None,
            'mobile_number':None,
            'skills':None,
            'college_name':None,
            'degree':None,
            'designation':None,
            'experience':None,
            'company_name':None,
            'no_of_pages':None,
            'total_exp':None,

        }
        self.__resume = resume
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__resume, '.'+ ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        cust_ent = utils.extract_entities_with_custom_model(
            self.__custom_nlp
        )



