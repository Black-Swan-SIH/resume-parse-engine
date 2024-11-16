# used to train an genenrate model.

#filed o be store as either data.json or data.pkl

import spacy
import json
import pickle
import random

train_data = pickle.load(open(r'data/training/train_data.pkl', 'rb'))

def clean_entity_spans(train_data):
    cleaned_data = []
    for text, annotations in train_data:
        entities = annotations['entities']
        cleaned_entities = []
        for start, end, label in entities:

            while start < len(text) and text[start].isspace():
                start += 1
            while end > start and text[end - 1].isspace():
                end -= 1

            if start < end:
                cleaned_entities.append((start, end, label))
        annotations['entities'] = cleaned_entities
        cleaned_data.append((text, annotations))
    return cleaned_data

train_data = clean_entity_spans(train_data)

from spacy.training import Example, offsets_to_biluo_tags
#example used to create spacy formt examples from our dataset for internal processing.
#biluo used for BIO or IOB tagging
nlp = spacy.blank('en') #ceate a spacy pipeline for english language. Hindi nhi hai isme, nhi toh gaali bot bnaskte.

def filter_valid_data(train_data, nlp):
    valid_data = [] #initialise an empty list
    for text, annotations in train_data: #goes through each text and iteration
        doc = nlp.make_doc(text) # translate text to spacy object
        try:
            offsets_to_biluo_tags(doc, annotations["entities"]) #make sures that there is no mimsmatch in data , there was a data wher character number was coincing.
            valid_data.append((text, annotations))  # Add valid data
        except ValueError:
            pass
    return valid_data

def train_model(train_data):
    if 'ner' not in nlp.pipe_names: #checks if ner model is there in pipe
        ner = nlp.add_pipe('ner', last=True)
    else:
        ner = nlp.get_pipe('ner') #runs when running script first time.


    for _, annotation in train_data:
        for ent in annotation['entities']: #exclusively used to extract each entity type.
            ner.add_label(ent[2]) #adds the entity (Like y axis in Linear regression)

    #
    filtered_data = filter_valid_data(train_data, nlp)

    if not filtered_data:
        print("No data available.")
        return


    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner'] #essential to make sure older pipes are stopped before running newone.
    with nlp.disable_pipes(*other_pipes): #initialise optimzer. most prbably adam v2.
        optimizer = nlp.begin_training()

        for itn in range(10):
            print(f"Starting iteration {itn}")
            random.shuffle(filtered_data) #this shuffles data everytime so that learning is proper and not same everytime.
            losses = {}
            for text, annotations in filtered_data:

                doc = nlp.make_doc(text) #convert the text into doc object
                example = Example.from_dict(doc, annotations) #creates an "example" for the NER to learn from (Our ner here is BERT)

                nlp.update([example], drop=0.2, sgd=optimizer, losses=losses)#This exact line is what fine tunes the model.

            print(losses)


train_model(train_data) #function call on data.
nlp.to_disk('nlp_model_v1')