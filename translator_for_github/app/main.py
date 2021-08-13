# Run by typing python3 main.py

## **IMPORTANT:** only collaborators on the project where you run
## this can access this web server!

"""
    Bonus points if you want to have internship at AI Camp
    1. How can we save what user built? And if we can save them, like allow them to publish, can we load the saved results back on the home page? 
    2. Can you add a button for each generated item at the frontend to just allow that item to be added to the story that the user is building? 
    3. What other features you'd like to develop to help AI write better with a user? 
    4. How to speed up the model run? Quantize the model? Using a GPU to run the model? 
"""

# import basics
import os
import json
import re
import random

# import stuff for our web server
from flask import Flask, flash, request, redirect, url_for, render_template
from flask import send_from_directory
from flask import jsonify
from utils import get_base_url, allowed_file, and_syntax
from flask_cors import cross_origin
from werkzeug.utils import secure_filename

# import stuff for our models
import torch
from aitextgen import aitextgen
from simplet5 import SimpleT5
import threading

#pdfminer will parse our arxiv articles
import io
import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

import PyPDF2

import sys
#nltk libraries
import nltk
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

'''
Coding center code - comment out the following 4 lines of code when ready for production
'''
# load up the model into memory
# you will need to have all your trained model in the app/ directory.
#ai = aitextgen(to_gpu=False, model=r"EleutherAI/gpt-neo-125M")

model = SimpleT5()
model.load_model(model_dir="SimpleT5-epoch-4-train-loss-0.0311")

# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
#port = 22224
#base_url = get_base_url(port)
#app = Flask(__name__, static_url_path=base_url+'static')

app = Flask(__name__)


'''
Deployment code - uncomment the following line of code when ready for production
'''

#Helper Functions
laparams = pdfminer.layout.LAParams()
setattr(laparams, 'all_texts', True)

import fitz
def extract_text_from_pdf_pymupdf(pdf_path):
    try:
        text = ""
        pdf = fitz.open(pdf_path)
        for page in pdf:
            text += page.get_text("text")
        return text
    except Exception as e:
        print (e)
        print("Error: could not parse this pdf")
        return "PDF could not be parsed"

def extract_text_from_pdf(pdf_path):
    try:
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=laparams)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh,
                                          caching=True,
                                          check_extractable=True):
                page_interpreter.process_page(page)

            text = fake_file_handle.getvalue()

        # close open handles
        converter.close()
        fake_file_handle.close()
        if text:
            return text
        else:
            return ""
    except Exception as e:
        print (e)
        print("Error: could not parse this pdf")
        converter.close()
        fake_file_handle.close()
        return ""

#removes stop wards, clears punctation, and lemmatizes the text
#might want to test using this model without cleaning the text as well, to see the result differences
def clean_text(text):
    sentences = nltk.sent_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    for i in range(len(sentences)):
        #removes stop words
        curr_words = nltk.word_tokenize(sentences[i])
        curr_words = [word for word in curr_words if word not in stopwords.words("english")]  
        #lemmatizes the words
        curr_words = [lemmatizer.lemmatize(word) for word in curr_words]
        #brings the words in curr_words into one sentence
        sentences[i] = " ".join(curr_words)
        #removes punctuation and extra spaces
        sentences[i] = re.sub(r"[\W]", " ", sentences[i])
        sentences[i] = re.sub(r"[\s+]", " ", sentences[i])
        sentences[i] = re.sub(r"[\n]", " ", sentences[i])

    text = " ".join(sentences)
    return text

#Open JSON file:
dictFile = open('cleaned_database2.json', 'r')
syn_dict = json.load(dictFile)
dictFile.close()
print(base_url)


@app.route('/')
#@app.route(base_url)
def home():
    return render_template('Home.html', generated=None)

app.route('/science')
#@app.route(base_url + '/science')
def science():
    #return render_template('Science-Translator.html', generated=None)
    return render_template('Science-Translator-text-box-version.html', generated=None)

@app.route('/generate_text', methods=["POST"])
#@app.route(base_url + '/generate_text', methods=["POST"])
def generate_text():
    """
    view function that will return json response for generated text. 
    """
    sat_dict = {'very' : 3, 'absolutely' : 3, 'awfully' : 3, 'certainly' : 2, 'decidedly' : 2, 'deeply' : 3, 'exceedingly' : 3, 'extremely' : 3, 'incredibly' : 3, 'particularly' : 1, 'pretty' : 1, 'profoundly' : 3, 'super': 2, 'really' : 2, 'truly' : 3, 'unquestionably' : 3, 'wonderfully' : 3, 'considerably' : 2, 'fairly' : 1, 'mostly' : 1, 'moderately' : 1, 'reasonably' : 1, 'adequately' : 1, 'quite' : 2, 'somewhat' : 1}
    prompt = request.form['prompt']
    conn_inc = int(request.form['connotation_inc'])
    #conn_inc = 4
    ###Load in the json of sent_dict and make it a dict
    conn_inc = conn_inc*0.8
    prompt_words = nltk.word_tokenize(prompt)
    for word in prompt_words:#, syn_list in sent_dict.items():
        if word in sat_dict:
            sat = satellite(word, conn_inc, sat_dict)
            prompt = re.sub(word, sat, prompt)
            continue
        if word not in syn_dict.keys():
            continue
        syn_list = syn_dict[word]
        closest_syn = word
        min_difference = abs(conn_inc)
        for index, tuple in enumerate(syn_list):
            syn = tuple[0]
            sent_difference = tuple[1]
            curr_difference = abs(sent_difference - conn_inc)
            if curr_difference < min_difference:
                min_difference = curr_difference
                closest_syn = syn
        prompt = re.sub(word, closest_syn, prompt)
    generated = [prompt]
    data = {'generated_ls': generated}

    return jsonify(data)

def satellite(sat, inc, sat_dict):
    inc = inc * 0.75
    closest_val = round(abs(sat_dict[sat] + inc))
    if closest_val != 0:
        if closest_val > 3:
            closest_val = 3
        similar_satellites = [key for key, val in sat_dict.items() if val == closest_val]
        return random.choice(similar_satellites)
    return sat

@app.route('/science', methods=["POST"])
#@app.route(base_url + '/science' ,methods=["POST"])
def science_thread_post():
    print("threading")
    print(request.json)
    text = request.json['prompt']
    text = text[:10000]
    print(text)
    input_path = "static/inputs/inputted_text.txt"
    predicted_path = "static/predictions/predicted_text.txt"
    txtfile = open(input_path,'w')
    txtfile.write(text)
    txtfile.close()
    open2delete = open(predicted_path,'w')
    open2delete.write("")
    open2delete.close()
    open2delete = open(predicted_path,'r')
    print(open2delete.read())
    def get_prediction():
        text = open(input_path, 'r').read()
        prediction = model.predict("summarize: " + text)
        predictfile =  open(predicted_path,'w')
        print("MY PREDICTION:")
        print(prediction)
        predictfile.write(prediction[0])
        predictfile.close()
        print("I AM DONE PREDICTING")
        return
    
    thread = threading.Thread(target = get_prediction)
    thread.start()
    data = {"file_path" : predicted_path}
    return jsonify(data)

@app.route('/donttypeme', methods = ["POST"])
#@app.route(base_url + '/donttypeme', methods = ["POST"])
def file_contents():
    predictfile =  open("static/predictions/predicted_text.txt",'r')
    prediction = predictfile.read()
    print(request.form)
    print(prediction)
    data = {"generated_ls": [prediction]}
    return jsonify(data)


if __name__ == "__main__":
    '''
    coding center code
    '''
    # IMPORTANT: change the cocalcx.ai-camp.org to the site where you are editing this file.
    website_url = 'cocalc1.ai-camp.org'
    print(f"Try to open\n\n    https://{website_url}" + base_url + '\n\n')

    app.run(host = '0.0.0.0', port=port, debug=True)
    import sys; sys.exit(0)

    '''
    scaffold code
    '''
    # Only for debugging while developing
    # app.run(port=80, debug=True)
