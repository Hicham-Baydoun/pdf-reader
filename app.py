from flask import Flask, render_template, request, jsonify, session
from PyPDF2 import PdfReader
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# API Key and URL
API_KEY = "AIzaSyD1xDa7y6DZvkXduXygl7IW5iU7jsDMdqk"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def extract_text_from_pdf(pdf_file):
    """Extracts text from the uploaded PDF file."""
    reader = PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def ask_ai_studio(content, question):
    """Sends a question to Google AI Studio based on the extracted PDF content."""
    try:
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"{content}\n\nQ: {question}\nA:"
                }]
            }]
        }
        
        response = requests.post(f"{API_URL}?key={API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as e:
        app.logger.error(f"API request failed: {str(e)}")
        return "Error: An unexpected error occurred while contacting the AI service."
    except (KeyError, IndexError) as e:
        app.logger.error(f"Error parsing API response: {str(e)}")
        return "Error: Unexpected response format from the API."
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return "Error: An unexpected error occurred. Please try again later."

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf' in request.files:
            pdf_file = request.files['pdf']
            if pdf_file.filename == '' or not pdf_file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'Invalid file type or no file selected'}), 400
            
            # Extract text from the uploaded PDF
            pdf_text = extract_text_from_pdf(pdf_file)
            
            # Store PDF text in session
            session['pdf_text'] = pdf_text
            
            return jsonify({'message': 'PDF uploaded successfully. You can now ask questions about it.'})
        
        elif 'question' in request.form:
            if 'pdf_text' not in session:
                return jsonify({'error': 'No PDF uploaded. Please upload a PDF first.'}), 400
            
            question = request.form.get('question', '')
            if not question:
                return jsonify({'error': 'No question provided'}), 400
            
            # Ask AI Studio the question based on the extracted text
            answer = ask_ai_studio(session['pdf_text'], question)
            
            return jsonify({'answer': answer})
        
        elif 'message' in request.form:
            user_message = request.form['message']
            
            # If no PDF is uploaded, use an empty string or default content for context
            pdf_text = session.get('pdf_text', '')  # Default to empty if no PDF is uploaded
            chat_response = ask_ai_studio(pdf_text, user_message)
            
            return jsonify({'answer': chat_response})
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
