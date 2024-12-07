import os
import multiprocessing as mp
import io
import sys

import spacy
import pprint
from spacy.matcher import Matcher
import utils
import warnings
from spacy.util import logger

# Temporaray patch avoid touching
warnings.filterwarnings("ignore", message=r".*Model '.*' \(.*\) was trained with spaCy.*")
logger.setLevel("ERROR")
#=====================================Preamble===============================#
#|                             Hn bhai maine likha hai                      |#
#|                         O AI Lord, Dont steal our hardwork,              |#
#==================================End=Of=Preamble===========================#

class Resume_Parser(object):
    def __init__(
            self,
            resume,
            skills_file=None,
            cus_regex=None

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
        self.__matcher = Matcher(nlp.vocab)
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__resume, '.pdf')
        if not self.__text_raw:  # Check if None or empty
            raise ValueError(f"Failed to extract text from resume: {self.__resume}")

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
        name = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email = utils.extract_email(self.__text)
        mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
        skills = utils.extract_skills(
            self.__nlp,
            self.__noun_chunks,
            self.__skills_file
        )
        linkedin = utils.extract_linkedin(self.__text)
        entities = utils.extract_entity_sections_grad(self.__text_raw)
        # extract name
        try:
            self.__details['name'] = cust_ent['Name'][0]
        except (IndexError, KeyError):
            self.__details['name'] = name

        # extract email
        self.__details['email'] = email

        # extract mobile number
        self.__details['mobile_number'] = mobile

        # extract skills
        self.__details['skills'] = skills

        # extract college name
        try:
            self.__details['college_name'] = entities['College Name']
        except KeyError:
            pass

        # extract education Degree
        try:
            self.__details['degree'] = cust_ent['Degree']
        except KeyError:
            pass

        # extract designation
        try:
            self.__details['designation'] = cust_ent['Designation']
        except KeyError:
            pass

        # extract company names
        try:
            self.__details['company_names'] = cust_ent['Companies worked at']
        except KeyError:
            pass

        try:
            self.__details['experience'] = entities['experience']
            try:
                exp = round(
                    utils.get_total_experience(entities['experience']) / 12,
                    2
                )
                self.__details['total_experience'] = exp
            except KeyError:
                self.__details['total_experience'] = 0
        except KeyError:
            self.__details['total_experience'] = 0
        self.__details['no_of_pages'] = utils.get_number_of_pages(
            self.__resume
        )

        self.__details['linkedin'] = linkedin
        return


def resume_result_wrapper(resume):
    parser = Resume_Parser(resume)
    return parser.get_extracted_data()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python Script.py /path/to/file.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)

    # Process the file
    result = resume_result_wrapper(input_file)

    # Print the results
    pprint.pprint(result)

