import openai
import requests
import configparser
from flask import Flask, request, render_template_string, render_template
from flask_bootstrap import Bootstrap
import PyPDF2


app = Flask(__name__)
Bootstrap(app)
openai.api_key = "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"
model_engine = 'text-davinci-002'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if file is uploaded
        if 'pdf_file' not in request.files:
            return "No file found", 400

        pdf_file = request.files['pdf_file']

        # Check if file is PDF
        if not pdf_file.filename.endswith('.pdf'):
            return "Invalid file format. Please upload a PDF file.", 400

        # Read PDF file and extract text
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        text = ''
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()

        # Summarize text using ChatGPT API
        response = openai.Completion.create(
            engine=model_engine,
            prompt=f"Summarize this resume focusing on the type of projects this candidate worked:\n{text}",
            max_tokens=1024,
            n=1,
            stop=None
        )
        summary = response.choices[0].text.strip()

        # Render summarized text in HTML format
        
        return render_template("1result.html", summary=summary)
 
    
    return render_template("1home.html")




@app.route('/JDGenerator')
def index():
    return render_template('2jdgenerator.html')

@app.route('/JDGenerator', methods=['POST'])
def generate_job_description():
    # Get input values from form
    input1 = request.form['input1']
    input2 = request.form['input2']
    input3 = request.form['input3']
    input4 = request.form['input4']
    input5 = request.form['input5']

    # Make API request to ChatGPT API

    response1 = openai.Completion.create(
        engine=model_engine,
        prompt=f"Generate a FULL job description with at least with the following requirements, job title: \n{input1} must haves: \n {input2} good to haves: \n {input3} years of experience: \n{input4} extras: \n{input5}",
        max_tokens=3900,
        temperature=1.3,
        n=1,
        stop=None
        )

    # Extract generated job description from API response
    job_description = response1.choices[0].text.strip()

    return render_template('2resultjd.html', job_description=job_description)


if __name__ == '__main__':
    app.run(debug=True)