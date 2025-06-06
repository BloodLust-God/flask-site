import os
import uuid
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            unique_name = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
            return redirect(url_for('upload'))  # ⬅️ Return to upload page after uploading

    # ✅ Get file list to show in upload.html
    files = os.listdir(UPLOAD_FOLDER)
    excel_files = [f for f in files if f.endswith('.xlsx') or f.endswith('.xls')]
    return render_template('upload.html', files=excel_files)

@app.route('/view')
def view():
    files = os.listdir(UPLOAD_FOLDER)
    excel_files = [f for f in files if f.endswith('.xlsx') or f.endswith('.xls')]
    return render_template('view.html', files=excel_files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/preview/<filename>')
def preview_excel(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        df = pd.read_excel(file_path)
        table_html = df.to_html(classes='table table-bordered', index=False)
        return render_template('preview.html', filename=filename, table=table_html)
    except Exception as e:
        return f"Error reading file: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
