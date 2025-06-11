import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'data.json'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',
    'ppt', 'pptx', 'xls', 'xlsx', 'csv',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'zip', 'rar', '7z', 'tar', 'gz'
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_data():
    """Load data from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            # Initialize with sample data
            data = {
                "departments": {
                    "computer_science": {
                        "name": "Computer Science",
                        "semesters": {
                            "1": {"name": "Semester 1"},
                            "2": {"name": "Semester 2"},
                            "3": {"name": "Semester 3"},
                            "4": {"name": "Semester 4"},
                            "5": {"name": "Semester 5"},
                            "6": {"name": "Semester 6"},
                            "7": {"name": "Semester 7"},
                            "8": {"name": "Semester 8"}
                        }
                    },
                    "mechanical": {
                        "name": "Mechanical Engineering",
                        "semesters": {
                            "1": {"name": "Semester 1"},
                            "2": {"name": "Semester 2"},
                            "3": {"name": "Semester 3"},
                            "4": {"name": "Semester 4"},
                            "5": {"name": "Semester 5"},
                            "6": {"name": "Semester 6"},
                            "7": {"name": "Semester 7"},
                            "8": {"name": "Semester 8"}
                        }
                    },
                    "electrical": {
                        "name": "Electrical Engineering",
                        "semesters": {
                            "1": {"name": "Semester 1"},
                            "2": {"name": "Semester 2"},
                            "3": {"name": "Semester 3"},
                            "4": {"name": "Semester 4"},
                            "5": {"name": "Semester 5"},
                            "6": {"name": "Semester 6"},
                            "7": {"name": "Semester 7"},
                            "8": {"name": "Semester 8"}
                        }
                    }
                },
                "files": []
            }
            save_data(data)
            return data
    except Exception as e:
        app.logger.error(f"Error loading data: {e}")
        return {"departments": {}, "files": []}

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error saving data: {e}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(filepath):
    """Get human readable file size"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

@app.route('/')
def index():
    """Homepage showing list of departments"""
    data = load_data()
    return render_template('index.html', departments=data['departments'])

@app.route('/department/<dept_id>')
def department(dept_id):
    """Department page showing list of semesters"""
    data = load_data()
    if dept_id not in data['departments']:
        flash('Department not found', 'error')
        return redirect(url_for('index'))
    
    department_data = data['departments'][dept_id]
    return render_template('department.html', 
                         department=department_data, 
                         dept_id=dept_id)

@app.route('/semester/<dept_id>/<semester_id>')
def semester(dept_id, semester_id):
    """Semester page showing list of categories"""
    data = load_data()
    if dept_id not in data['departments']:
        flash('Department not found', 'error')
        return redirect(url_for('index'))
    
    department_data = data['departments'][dept_id]
    categories = ['CAT', 'ESE', 'SAT', 'Practical']
    
    return render_template('semester.html', 
                         department=department_data,
                         dept_id=dept_id,
                         semester_id=semester_id,
                         categories=categories)

@app.route('/category/<dept_id>/<semester_id>/<category>')
def category_view(dept_id, semester_id, category):
    """Category page showing downloadable files"""
    data = load_data()
    if dept_id not in data['departments']:
        flash('Department not found', 'error')
        return redirect(url_for('index'))
    
    # Filter files for this specific category
    filtered_files = [
        f for f in data['files'] 
        if f['department'] == dept_id and 
           f['semester'] == semester_id and 
           f['category'] == category
    ]
    
    department_data = data['departments'][dept_id]
    
    return render_template('category.html',
                         department=department_data,
                         dept_id=dept_id,
                         semester_id=semester_id,
                         category=category,
                         files=filtered_files)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload new files"""
    data = load_data()
    
    if request.method == 'POST':
        try:
            # Get form data
            department = request.form.get('department')
            semester = request.form.get('semester')
            category = request.form.get('category')
            subject = request.form.get('subject')
            custom_filename = request.form.get('filename')
            
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            if file and file.filename and allowed_file(file.filename):
                # Use custom filename if provided, otherwise use original
                if custom_filename:
                    filename = secure_filename(custom_filename)
                    # Add extension if not present
                    if '.' in file.filename:
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        if not filename.endswith('.' + ext):
                            filename += '.' + ext
                else:
                    filename = secure_filename(file.filename)
                
                # Handle duplicate filenames
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                counter = 1
                base_name, extension = os.path.splitext(filename)
                
                while os.path.exists(filepath):
                    filename = f"{base_name}_{counter}{extension}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    counter += 1
                
                # Save the file
                file.save(filepath)
                
                # Add file metadata to JSON
                file_data = {
                    "id": len(data['files']) + 1,
                    "filename": filename,
                    "original_filename": file.filename,
                    "custom_filename": custom_filename or filename,
                    "department": department,
                    "semester": semester,
                    "category": category,
                    "subject": subject,
                    "size": get_file_size(filepath),
                    "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "file_path": filepath
                }
                
                data['files'].append(file_data)
                save_data(data)
                
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('category_view', 
                              dept_id=department, 
                              semester_id=semester, 
                              category=category))
            else:
                flash('File type not allowed', 'error')
                
        except Exception as e:
            app.logger.error(f"Upload error: {str(e)}")
            flash('An error occurred during upload. Please try again.', 'error')
    
    return render_template('upload.html', departments=data['departments'])

@app.route('/download/<int:file_id>')
def download(file_id):
    """Download a file"""
    try:
        data = load_data()
        file_data = None
        
        for f in data['files']:
            if f['id'] == file_id:
                file_data = f
                break
        
        if not file_data:
            flash('File not found', 'error')
            return redirect(url_for('index'))
        
        filepath = file_data['file_path']
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return send_file(filepath, as_attachment=True, download_name=file_data['custom_filename'])
        else:
            flash('File not found on disk', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<int:file_id>')
def delete_file(file_id):
    """Delete a file"""
    try:
        data = load_data()
        file_data = None
        file_index = -1
        
        for i, f in enumerate(data['files']):
            if f['id'] == file_id:
                file_data = f
                file_index = i
                break
        
        if not file_data:
            flash('File not found', 'error')
            return redirect(url_for('index'))
        
        # Delete physical file
        filepath = file_data['file_path']
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
        
        # Remove from JSON data
        data['files'].pop(file_index)
        save_data(data)
        
        flash('File deleted successfully', 'success')
        return redirect(url_for('category_view', 
                      dept_id=file_data['department'], 
                      semester_id=file_data['semester'], 
                      category=file_data['category']))
    
    except Exception as e:
        app.logger.error(f"Delete error: {str(e)}")
        flash('Error deleting file', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large error"""
    flash(f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB', 'error')
    return redirect(url_for('upload'))

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)