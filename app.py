import openai
from flask import Flask, request, render_template

app = Flask(__name__)
openai.api_key = "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"


@app.route('/', methods=['POST'])
def upload():
    file = request.files['file']
    text = extract_text(file)
    summary = summarize_text(text)
    return render_template('home.html', summary=summary)

def extract_text(file):
    """Extract text from a file."""
    # Assumes the file is a PDF
    text = ""
    with openai.file(file.stream, content_type='application/pdf') as f:
        pdf = openai.Compression.gzip_decompress(f.read())
        text = openai.FormattedText(pdf).plain_text()
    return text

def summarize_text(text):
    """Summarize text using OpenAI GPT-3 API."""
    prompt = (f"Please summarize the following text into 5 sentences:\n\n{text}\n\nSummary:")
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.5,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    summary = response.choices[0].text.strip()
    return summary



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)