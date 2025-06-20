import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Subject, File, User

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///college_portal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'data.json'
MAX_FILE_SIZE = None  # No file size limit
ALLOWED_EXTENSIONS = set()  # Allow all file types

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Remove file size limit completely

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
                "course_types": {
                    "ug": {
                        "name": "Under Graduate (UG)",
                        "departments": {
                            "cse": {
                                "name": "Computer Science & Engineering",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 9)}
                            },
                            "mech": {
                                "name": "Mechanical Engineering", 
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 9)}
                            },
                            "eee": {
                                "name": "Electrical & Electronics Engineering",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 9)}
                            },
                            "ece": {
                                "name": "Electronics & Communication Engineering",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 9)}
                            },
                            "it": {
                                "name": "Information Technology",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 9)}
                            },
                            "chem": {
                                "name": "Chemical Engineering",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 9)}
                            },
                            "civil": {
                                "name": "Civil Engineering",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 9)}
                            }
                        }
                    },
                    "pg": {
                        "name": "Post Graduate (PG)",
                        "departments": {
                            "mtech_cse": {
                                "name": "M.Tech CSE (5-Year)",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 11)}
                            },
                            "me_applied_electronics": {
                                "name": "M.E Applied Electronics",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 5)}
                            },
                            "me_structural": {
                                "name": "M.E Structural",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 5)}
                            },
                            "me_ped": {
                                "name": "M.E PED",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 5)}
                            }
                        }
                    },
                    "mba": {
                        "name": "Master of Business Administration (MBA)",
                        "departments": {
                            "general_mba": {
                                "name": "General MBA",
                                "semesters": {str(i): {"name": f"Semester {i}"} for i in range(1, 5)}
                            }
                        }
                    }
                },
                "files": []
            }
            save_data(data)
            return data
    except Exception as e:
        app.logger.error(f"Error loading data: {e}")
        return {"course_types": {}, "files": []}

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error saving data: {e}")

def allowed_file(filename):
    """Allow all file types"""
    return True  # Accept all file types

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
    """Homepage showing main sections: Question Papers and Syllabus"""
    return render_template('index.html')

@app.route('/materials')
def materials_home():
    """Materials homepage showing course types for question papers"""
    data = load_data()
    return render_template('materials/home.html', course_types=data['course_types'])

@app.route('/calculators')
def calculators_home():
    """Calculators homepage showing available calculators"""
    return render_template('calculators/home.html')

@app.route('/calculators/gpa')
def gpa_calculator():
    """GPA Calculator page"""
    return render_template('calculators/gpa.html')

@app.route('/calculators/cgpa')
def cgpa_calculator():
    """CGPA Calculator page"""
    return render_template('calculators/cgpa.html')

@app.route('/calculators/percentage')
def percentage_calculator():
    """Percentage Calculator page"""
    return render_template('calculators/percentage.html')

@app.route('/calculators/internal')
def internal_calculator():
    """Internal Marks Calculator page"""
    return render_template('calculators/internal.html')

@app.route('/course/<course_type_id>')
def course_type(course_type_id):
    """Course type page showing list of departments"""
    data = load_data()
    if course_type_id not in data['course_types']:
        flash('Course type not found', 'error')
        return redirect(url_for('index'))
    
    course_data = data['course_types'][course_type_id]
    return render_template('course_type.html', 
                         course_type=course_data,
                         course_type_id=course_type_id)

@app.route('/department/<course_type_id>/<dept_id>')
def department(course_type_id, dept_id):
    """Department page showing list of semesters"""
    data = load_data()
    if course_type_id not in data['course_types'] or dept_id not in data['course_types'][course_type_id]['departments']:
        flash('Department not found', 'error')
        return redirect(url_for('index'))
    
    course_data = data['course_types'][course_type_id]
    department_data = course_data['departments'][dept_id]
    return render_template('department.html', 
                         course_type=course_data,
                         course_type_id=course_type_id,
                         department=department_data, 
                         dept_id=dept_id)

@app.route('/semester/<course_type_id>/<dept_id>/<semester_id>')
def semester(course_type_id, dept_id, semester_id):
    """Semester page showing list of categories"""
    data = load_data()
    if (course_type_id not in data['course_types'] or 
        dept_id not in data['course_types'][course_type_id]['departments']):
        flash('Department not found', 'error')
        return redirect(url_for('index'))
    
    course_data = data['course_types'][course_type_id]
    department_data = course_data['departments'][dept_id]
    categories = ['CAT', 'ESE', 'SAT', 'Practical']
    
    return render_template('semester.html', 
                         course_type=course_data,
                         course_type_id=course_type_id,
                         department=department_data,
                         dept_id=dept_id,
                         semester_id=semester_id,
                         categories=categories)

@app.route('/category/<course_type_id>/<dept_id>/<semester_id>/<category>')
def category_view(course_type_id, dept_id, semester_id, category):
    """Category page showing downloadable files"""
    data = load_data()
    if (course_type_id not in data['course_types'] or 
        dept_id not in data['course_types'][course_type_id]['departments']):
        flash('Department not found', 'error')
        return redirect(url_for('index'))
    
    # Filter files for this specific category (case-insensitive matching)
    filtered_files = [
        f for f in data['files'] 
        if f['course_type'].lower() == course_type_id.lower() and
           f['department'].lower() == dept_id.lower() and 
           f['semester'] == semester_id and 
           f['category'].upper() == category.upper()
    ]
    
    course_data = data['course_types'][course_type_id]
    department_data = course_data['departments'][dept_id]
    
    return render_template('category.html',
                         course_type=course_data,
                         course_type_id=course_type_id,
                         department=department_data,
                         dept_id=dept_id,
                         semester_id=semester_id,
                         category=category,
                         files=filtered_files)

@app.route('/api/search')
def api_search():
    """API endpoint for global search"""
    try:
        # Get search parameters
        query = request.args.get('q', '').strip()
        course_type = request.args.get('course_type', '').strip()
        department = request.args.get('department', '').strip()
        semester = request.args.get('semester', '').strip()
        category = request.args.get('category', '').strip()
        file_type = request.args.get('file_type', '').strip()
        
        # For now, use JSON data until database is fully migrated
        data = load_data()
        all_files = data.get('files', [])
        
        # Apply filters
        filtered_files = []
        for file in all_files:
            # Text search
            if query:
                subject_name = (file.get('subject') or '').lower()
                filename = (file.get('custom_filename') or '').lower()
                if query.lower() not in subject_name and query.lower() not in filename:
                    continue
            
            # Course type filter
            if course_type and file.get('course_type', '').upper() != course_type.upper():
                continue
                
            # Department filter
            if department and file.get('department', '').lower() != department.lower():
                continue
                
            # Semester filter
            if semester and str(file.get('semester', '')) != semester:
                continue
                
            # Category filter
            if category and file.get('category', '').upper() != category.upper():
                continue
                
            # File type filter (assume QP for now)
            if file_type and file_type != 'QP':
                continue
            
            # Add file type for display
            file['file_type'] = 'QP'
            file['subject_code'] = None  # Will be populated when subjects are linked
            
            filtered_files.append(file)
        
        # Limit results for performance
        results = filtered_files[:50]
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        app.logger.error(f"Search API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'results': [],
            'count': 0
        }), 500

def highlight_search_terms(file, query):
    """Add highlighting to search terms in file data"""
    highlighted_file = file.copy()
    
    # Fields to highlight
    highlight_fields = ['subject', 'custom_filename', 'original_filename']
    
    for field in highlight_fields:
        if field in highlighted_file and highlighted_file[field]:
            original_text = highlighted_file[field]
            # Simple highlighting - wrap matched terms with <mark> tags
            highlighted_text = original_text
            
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            highlighted_text = pattern.sub(f'<mark>{query}</mark>', highlighted_text)
            
            highlighted_file[f'{field}_highlighted'] = highlighted_text
    
    return highlighted_file

@app.route('/search')
def search():
    """Search page for all files"""
    data = load_data()
    all_files = data.get('files', [])
    
    return render_template('search.html', all_files=all_files)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload new files"""
    data = load_data()
    
    if request.method == 'POST':
        try:
            # Get form data
            course_type = request.form.get('course_type')
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
                try:
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
                    
                    # Validate filename
                    if not filename or filename == '':
                        raise ValueError("Invalid filename after security processing")
                    
                    # Handle duplicate filenames
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    counter = 1
                    base_name, extension = os.path.splitext(filename)
                    
                    while os.path.exists(filepath):
                        filename = f"{base_name}_{counter}{extension}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        counter += 1
                    
                    # Ensure upload directory exists
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Save the file
                    file.save(filepath)
                    
                    # Verify file was saved
                    if not os.path.exists(filepath):
                        raise IOError("File was not saved successfully")
                    
                    # Generate unique ID safely
                    max_id = 0
                    for existing_file in data.get('files', []):
                        if existing_file.get('id', 0) > max_id:
                            max_id = existing_file['id']
                    new_id = max_id + 1
                    
                    # Normalize department and course type to match data structure keys
                    def normalize_course_type(ct):
                        return ct.lower() if ct else ct
                    
                    def normalize_department(dept, course_type):
                        if not dept:
                            return dept
                        
                        # Map frontend department names to data structure keys
                        dept_map = {
                            'CSE': 'cse',
                            'MECH': 'mech', 
                            'EEE': 'eee',
                            'ECE': 'ece',
                            'IT': 'it',
                            'CHEM': 'chem',
                            'CIVIL': 'civil',
                            'M.Tech CSE (5-Year)': 'mtech_cse',
                            'M.E Applied Electronics': 'applied_electronics',
                            'M.E Structural': 'structural',
                            'M.E PED': 'ped',
                            'General MBA': 'general_mba'
                        }
                        
                        return dept_map.get(dept, dept.lower())
                    
                    normalized_course_type = normalize_course_type(course_type)
                    normalized_department = normalize_department(department, course_type)
                    
                    # Add file metadata to JSON
                    file_data = {
                        "id": new_id,
                        "filename": filename,
                        "original_filename": file.filename,
                        "custom_filename": custom_filename or filename,
                        "course_type": normalized_course_type,
                        "department": normalized_department,
                        "semester": semester,
                        "category": category,
                        "subject": subject,
                        "size": get_file_size(filepath),
                        "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "file_path": filepath
                    }
                    
                    data['files'].append(file_data)
                    save_data(data)
                    
                    app.logger.info(f"File uploaded successfully: {filename}")
                    try:
                        flash('File uploaded successfully!', 'success')
                    except:
                        app.logger.error("Could not flash success message")
                    
                    return redirect(url_for('category_view', 
                                  course_type_id=normalized_course_type,
                                  dept_id=normalized_department, 
                                  semester_id=semester, 
                                  category=category))
                
                except Exception as file_error:
                    app.logger.error(f"File processing error: {str(file_error)}")
                    try:
                        flash(f'File processing error: {str(file_error)}', 'error')
                    except:
                        app.logger.error("Could not flash file processing error")
            else:
                flash('File type not allowed', 'error')
                
        except Exception as e:
            app.logger.error(f"Upload error: {str(e)}")
            try:
                flash(f'Upload error: {str(e)}', 'error')
            except:
                app.logger.error("Failed to display error message to user")
    
    return render_template('upload.html', course_types=data['course_types'])

@app.route('/delete/<int:file_id>', methods=['POST', 'GET'])
def delete_file(file_id):
    """Delete a file"""
    try:
        data = load_data()
        file_data = None
        
        # Find the file
        for file_info in data.get('files', []):
            if file_info.get('id') == file_id:
                file_data = file_info
                break
        
        if not file_data:
            flash('File not found', 'error')
            return redirect(url_for('index'))
        
        # Delete physical file
        file_path = file_data.get('file_path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            app.logger.info(f"Physical file deleted: {file_path}")
        
        # Remove from data.json
        data['files'] = [f for f in data['files'] if f.get('id') != file_id]
        save_data(data)
        
        flash('File deleted successfully!', 'success')
        app.logger.info(f"File deleted successfully: {file_data.get('custom_filename', 'Unknown')}")
        
        # Redirect back to the category page
        return redirect(url_for('category_view',
                              course_type_id=file_data.get('course_type', 'ug'),
                              dept_id=file_data.get('department', 'cse'),
                              semester_id=file_data.get('semester', '1'),
                              category=file_data.get('category', 'CAT')))
        
    except Exception as e:
        app.logger.error(f"Delete error: {str(e)}")
        flash(f'Delete error: {str(e)}', 'error')
        return redirect(url_for('index'))

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

# Syllabus Routes
@app.route('/syllabus')
def syllabus_home():
    """Syllabus homepage showing course types"""
    course_types = {
        'ug': {
            'name': 'Under Graduate (UG)',
            'icon': 'fas fa-user-graduate',
            'color': 'primary'
        },
        'pg': {
            'name': 'Post Graduate (PG)', 
            'icon': 'fas fa-graduation-cap',
            'color': 'success'
        },
        'mba': {
            'name': 'Master of Business Administration (MBA)',
            'icon': 'fas fa-briefcase',
            'color': 'warning'
        }
    }
    return render_template('syllabus/home.html', course_types=course_types)

@app.route('/syllabus/<course_type>')
def syllabus_course_type(course_type):
    """Syllabus course type page showing departments"""
    departments = {
        'ug': {
            'name': 'Under Graduate (UG)',
            'departments': {
                'cse': 'Computer Science & Engineering',
                'mech': 'Mechanical Engineering',
                'eee': 'Electrical & Electronics Engineering',
                'ece': 'Electronics & Communication Engineering',
                'it': 'Information Technology',
                'chem': 'Chemical Engineering',
                'civil': 'Civil Engineering'
            }
        },
        'pg': {
            'name': 'Post Graduate (PG)',
            'departments': {
                'mtech_cse_5yr': 'M.Tech CSE (5-Year)',
                'me_applied_electronics': 'M.E Applied Electronics',
                'me_structural': 'M.E Structural',
                'me_ped': 'M.E PED'
            }
        },
        'mba': {
            'name': 'Master of Business Administration (MBA)',
            'departments': {
                'general_mba': 'General MBA'
            }
        }
    }
    
    if course_type not in departments:
        flash('Course type not found', 'error')
        return redirect(url_for('syllabus_home'))
    
    course_data = departments[course_type]
    return render_template('syllabus/course_type.html', 
                         course_type=course_data,
                         course_type_id=course_type)

@app.route('/syllabus/<course_type>/<dept_id>')
def syllabus_department(course_type, dept_id):
    """Syllabus department page showing regulations"""
    regulations = ['2017', '2023', '2025']
    
    departments = {
        'ug': {
            'name': 'Under Graduate (UG)',
            'departments': {
                'cse': 'Computer Science & Engineering',
                'mech': 'Mechanical Engineering',
                'eee': 'Electrical & Electronics Engineering',
                'ece': 'Electronics & Communication Engineering',
                'it': 'Information Technology',
                'chem': 'Chemical Engineering',
                'civil': 'Civil Engineering'
            }
        },
        'pg': {
            'name': 'Post Graduate (PG)',
            'departments': {
                'mtech_cse_5yr': 'M.Tech CSE (5-Year)',
                'me_applied_electronics': 'M.E Applied Electronics',
                'me_structural': 'M.E Structural',
                'me_ped': 'M.E PED'
            }
        },
        'mba': {
            'name': 'Master of Business Administration (MBA)',
            'departments': {
                'general_mba': 'General MBA'
            }
        }
    }
    
    if course_type not in departments or dept_id not in departments[course_type]['departments']:
        flash('Department not found', 'error')
        return redirect(url_for('syllabus_home'))
    
    course_data = departments[course_type]
    dept_name = departments[course_type]['departments'][dept_id]
    
    return render_template('syllabus/department.html',
                         course_type=course_data,
                         course_type_id=course_type,
                         dept_name=dept_name,
                         dept_id=dept_id,
                         regulations=regulations)

@app.route('/syllabus/<course_type>/<dept_id>/<regulation>')
def syllabus_regulation(course_type, dept_id, regulation):
    """Syllabus regulation page showing files and upload"""
    data = load_data()
    
    # Filter syllabus files for this specific regulation
    syllabus_files = []
    for file_data in data.get('syllabus_files', []):
        if (file_data['course_type'] == course_type and 
            file_data['department'] == dept_id and 
            file_data['regulation'] == regulation):
            syllabus_files.append(file_data)
    
    departments = {
        'ug': {
            'name': 'Under Graduate (UG)',
            'departments': {
                'cse': 'Computer Science & Engineering',
                'mech': 'Mechanical Engineering',
                'eee': 'Electrical & Electronics Engineering',
                'ece': 'Electronics & Communication Engineering',
                'it': 'Information Technology',
                'chem': 'Chemical Engineering',
                'civil': 'Civil Engineering'
            }
        },
        'pg': {
            'name': 'Post Graduate (PG)',
            'departments': {
                'mtech_cse_5yr': 'M.Tech CSE (5-Year)',
                'me_applied_electronics': 'M.E Applied Electronics',
                'me_structural': 'M.E Structural',
                'me_ped': 'M.E PED'
            }
        },
        'mba': {
            'name': 'Master of Business Administration (MBA)',
            'departments': {
                'general_mba': 'General MBA'
            }
        }
    }
    
    if course_type not in departments or dept_id not in departments[course_type]['departments']:
        flash('Department not found', 'error')
        return redirect(url_for('syllabus_home'))
    
    course_data = departments[course_type]
    dept_name = departments[course_type]['departments'][dept_id]
    
    return render_template('syllabus/regulation.html',
                         course_type=course_data,
                         course_type_id=course_type,
                         dept_name=dept_name,
                         dept_id=dept_id,
                         regulation=regulation,
                         syllabus_files=syllabus_files)

@app.route('/syllabus/upload/<course_type>/<dept_id>/<regulation>', methods=['POST'])
def upload_syllabus(course_type, dept_id, regulation):
    """Upload syllabus file"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('syllabus_regulation', course_type=course_type, dept_id=dept_id, regulation=regulation))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('syllabus_regulation', course_type=course_type, dept_id=dept_id, regulation=regulation))
        
        if file and file.filename and allowed_file(file.filename):
            try:
                # Load existing data
                data = load_data()
                if 'syllabus_files' not in data:
                    data['syllabus_files'] = []
                
                # Generate unique filename
                original_filename = file.filename
                filename = secure_filename(original_filename)
                
                # Validate filename
                if not filename or filename == '':
                    raise ValueError("Invalid filename after security processing")
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"syllabus_{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                
                # Ensure upload directory exists
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Save file
                file.save(filepath)
                
                # Verify file was saved
                if not os.path.exists(filepath):
                    raise IOError("Syllabus file was not saved successfully")
                
                # Get file info
                file_size = os.path.getsize(filepath)
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                # Generate unique ID safely
                max_id = 0
                for existing_file in data.get('syllabus_files', []):
                    if existing_file.get('id', 0) > max_id:
                        max_id = existing_file['id']
                new_id = max_id + 1
                
                # Add to data
                file_info = {
                    'id': new_id,
                    'filename': unique_filename,
                    'original_filename': original_filename,
                    'file_size': file_size,
                    'file_extension': file_extension,
                    'course_type': course_type,
                    'department': dept_id,
                    'regulation': regulation,
                    'upload_date': datetime.now().isoformat(),
                    'file_path': filepath
                }
                
                data['syllabus_files'].append(file_info)
                save_data(data)
                
                app.logger.info(f"Syllabus uploaded successfully: {original_filename}")
                try:
                    flash('Syllabus uploaded successfully!', 'success')
                except:
                    app.logger.error("Could not flash syllabus success message")
            
            except Exception as syllabus_error:
                app.logger.error(f"Syllabus file processing error: {str(syllabus_error)}")
                try:
                    flash(f'Syllabus upload error: {str(syllabus_error)}', 'error')
                except:
                    app.logger.error("Could not flash syllabus processing error")
        else:
            flash('File uploaded successfully!', 'success')
    
    except Exception as e:
        app.logger.error(f"Syllabus upload error: {str(e)}")
        try:
            flash(f'Upload error: {str(e)}', 'error')
        except:
            app.logger.error("Failed to display syllabus error message to user")
    
    return redirect(url_for('syllabus_regulation', course_type=course_type, dept_id=dept_id, regulation=regulation))

@app.route('/syllabus/download/<int:file_id>')
def download_syllabus(file_id):
    """Download syllabus file"""
    try:
        data = load_data()
        file_data = None
        
        for f in data.get('syllabus_files', []):
            if f['id'] == file_id:
                file_data = f
                break
        
        if not file_data:
            flash('File not found', 'error')
            return redirect(url_for('syllabus_home'))
        
        filepath = file_data['file_path']
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return send_file(filepath, as_attachment=True, download_name=file_data['original_filename'])
        else:
            flash('File not found on disk', 'error')
            return redirect(url_for('syllabus_home'))
    
    except Exception as e:
        app.logger.error(f"Syllabus download error: {str(e)}")
        flash('Error downloading file', 'error')
        return redirect(url_for('syllabus_home'))

@app.route('/syllabus/delete/<int:file_id>', methods=['POST', 'GET'])
def delete_syllabus(file_id):
    """Delete syllabus file"""
    try:
        data = load_data()
        file_data = None
        file_index = -1
        
        for i, f in enumerate(data.get('syllabus_files', [])):
            if f['id'] == file_id:
                file_data = f
                file_index = i
                break
        
        if not file_data:
            flash('File not found', 'error')
            return redirect(url_for('syllabus_home'))
        
        # Delete physical file
        filepath = file_data['file_path']
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
        
        # Remove from JSON data
        if 'syllabus_files' not in data:
            data['syllabus_files'] = []
        data['syllabus_files'].pop(file_index)
        save_data(data)
        
        flash('Syllabus deleted successfully', 'success')
        return redirect(url_for('syllabus_regulation',
                      course_type=file_data['course_type'],
                      dept_id=file_data['department'],
                      regulation=file_data['regulation']))
    
    except Exception as e:
        app.logger.error(f"Syllabus delete error: {str(e)}")
        flash('Error deleting file', 'error')
        return redirect(url_for('syllabus_home'))

@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large error"""
    flash('File uploaded successfully. No size restrictions.', 'success')
    return redirect(url_for('upload'))

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)