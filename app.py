from flask import Flask, render_template, request, jsonify
from backend.parser import process_pdf
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded'
    
    file = request.files['file']

    if file.filename == '':
        return 'No file selected'
    
    if file:
        filename = file.filename
        filepath = os.path.join('uploads', filename)

        file.save(filepath)
        courses = process_pdf(filepath)

        return jsonify({'courses': courses})

if __name__ == '__main__':
    app.run(debug=True)