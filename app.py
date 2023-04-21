import openai
import requests
import configparser
from flask import Flask, request, render_template_string, render_template
import PyPDF2


app = Flask(__name__)
openai.api_key = "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"
model_engine = 'text-davinci-003'

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
            prompt= f"Summarize in 1 paragraph this resume focusing on the type of companies and projects the person worked, always use the name of the candidate (make sure you share the main technologies used):\n{text}",
            max_tokens=500,
            n=1,
            stop=None
        )

        companies = openai.Completion.create(
            engine=model_engine,
            prompt=f"Based on the following Resume, can you list the main companies this candidate worked at. This is the resume: \n{text}",
            max_tokens= 300,
            temperature=0.3,
            n=1,
            stop=None
        )

        response3 = openai.Completion.create(
            engine=model_engine,
            prompt=f" Based on this list of companies: \n{companies}\n Can you tell me what these companies do. Use the following structure: \n Name of company : what they do\n",
            max_tokens= 800,
            temperature=0.2,
            n=1,
            stop=None
        )
    
        companytype = response3.choices[0].text.strip()
        summary = response.choices[0].text.strip()

        # Render summarized text in HTML format
        
        return render_template("1summarizerresult.html", summary=summary, companytype=companytype)
 
    
    return render_template("1summarizer.html")




@app.route('/JDGenerator')
def index():
    return render_template('testgenerator.html')

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
        prompt=f"Generate a FULL job description with the following requirements and structure, Remote or Relocation: \n{input1} Job Title: \n {input2} Must Have: \n {input3} Good to Have: \n{input4} Years of Experience: \n{input5}, please use this structure: Remote or Relocation opportunity: Explain if this a a remote or relocation opportunity -Job Title: Clearly state the title of the position, which should accurately reflect the role and responsibilities of the job. -Overview: Provide a brief summary of the job, including its purpose and how it fits within the organization. -Responsibilities: List the main tasks, duties, and responsibilities of the role. Use bullet points to make it easy to read and understand. Include both the day-to-day tasks and any larger projects or initiatives the employee will be responsible for. -Qualifications: Outline must haves and good to haves qualifications for the job. This may include experience, skills, certifications, and any other relevant qualifications necessary to perform the job successfully. -Company Culture and Values: Briefly describe the company's culture and values, and how they align with the expectations for the role. -Equal Opportunity Employer Statement: Include a statement indicating that the company is an equal opportunity employer and does not discriminate based on race, color, religion, sex, sexual orientation, gender identity, national origin, age, disability, or any other protected status. ",
        max_tokens=3700,
        temperature=1.3,
        n=1,
        stop=None
        )



    # Extract generated job description from API response
    job_description = response1.choices[0].text.strip()



    return render_template('testgeneratorresult.html', job_description=job_description)


if __name__ == '__main__':
    app.run(debug=True)