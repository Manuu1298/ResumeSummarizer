import openai
import requests
import configparser
from flask import Flask, request, render_template_string, render_template
import PyPDF2
import asyncio
import aiohttp
from flask import jsonify

 
app = Flask(__name__)
openai.api_key = "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"
model_engine = 'text-davinci-003'

async def summarize_text(text):
    response = openai.Completion.create(
        engine=model_engine,
        prompt= f"Summarize in 100-150 words this resume focusing on the type of companies and projects the person worked, always use the name of the candidate (make sure you share the main technologies used):\n{text}",
        max_tokens=150,
        temperature=0.3,
        n=1,
        stop=None
    )
    return response.choices[0].text.strip()

async def extract_companies(text):
    companies = openai.Completion.create(
        engine=model_engine,
        prompt=f"Based on the following Resume, can you list the main companies this candidate worked at and from what year he started to what year he left. Do not use They, only refer to the candidate by their name. This is the resume: \n{text}",
        max_tokens= 80,
        temperature=0.3,
        n=1,
        stop=None
    )
    return companies.choices[0].text.strip()

async def extract_company_type(companies):
    response = openai.Completion.create(
        engine=model_engine,
        prompt=f" Based on this list of companies: \n{companies}\n Can you tell me what these companies do. Use the following structure: \n Name of company (years he worked there): what they do\n",
        max_tokens= 150,
        temperature=0.2,
        n=1,
        stop=None
    )
    return response.choices[0].text.strip()

@app.route('/', methods=['GET', 'POST'])
async def upload_file():
    if request.method == 'POST':
        # Check if file is uploaded
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file found'}), 400

        pdf_file = request.files['pdf_file']

        # Check if file is PDF
        if not pdf_file.filename.endswith('.pdf'):
            return jsonify({'error': 'Invalid file format. Please upload a PDF file.'}), 400

        # Read PDF file and extract text
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        text = ''
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()

        # Make API requests using asyncio
        summary_task = asyncio.create_task(summarize_text(text))
        companies_task = asyncio.create_task(extract_companies(text))

        # Wait for API responses
        summary = await summary_task
        companies = await companies_task

        companytype = await extract_company_type(companies)

        # Return JSON response
        return jsonify({'summary': summary, 'companytype': companytype})

    return render_template("1summarizer.html")


model_engine = 'text-davinci-003'

async def generate_job_description(input1, input2, input3, input4, input5):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                'https://api.openai.com/v1/engines/text-davinci-003/completions',
                headers={'Authorization': f'Bearer {openai.api_key}'},
                json={
                    'prompt': f"Generate a FULL job description with the following requirements and structure, Remote or Relocation: \n{input1} Job Title: \n {input2} Must Have: \n {input3} Good to Have: \n{input4} Years of Experience: \n{input5}, please use this structure: Remote or Relocation opportunity: Explain if this a a remote or relocation opportunity -Job Title: Clearly state the title of the position, which should accurately reflect the role and responsibilities of the job. -Overview: Provide a brief summary of the job, including its purpose and how it fits within the organization. -Responsibilities: List the main tasks, duties, and responsibilities of the role. Use bullet points to make it easy to read and understand. Include both the day-to-day tasks and any larger projects or initiatives the employee will be responsible for. -Qualifications: Outline must haves and good to haves qualifications for the job. This may include experience, skills, certifications, and any other relevant qualifications necessary to perform the job successfully. -Company Culture and Values: Briefly describe the company's culture and values, and how they align with the expectations for the role.",
                    'max_tokens': 3700,
                    'temperature': 1.3,
                    'n': 1,
                    'stop': None
                }
        ) as response:
            response = await response.json()
            job_description = response['choices'][0]['text'].strip()
            return job_description

@app.route('/JDGenerator', methods=['POST'])
async def generate_job_description_handler():
    # Get input values from request JSON
    input1 = request.json['input1']
    input2 = request.json['input2']
    input3 = request.json['input3']
    input4 = request.json['input4']
    input5 = request.json['input5']

    # Make asynchronous API request to OpenAI
    job_description = await generate_job_description(input1, input2, input3, input4, input5)

    # Return job description as JSON response
    return jsonify(job_description=job_description)

@app.route('/JDGenerator')
def index():
    return render_template('2testgenerator.html')

if __name__ == '__main__':
    app.run(debug=True)