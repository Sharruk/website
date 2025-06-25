import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory, jsonify, session
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

def load_community_data():
    """Load community data from JSON file"""
    try:
        if os.path.exists('community.json'):
            with open('community.json', 'r') as f:
                return json.load(f)
        else:
            return {"discussions": []}
    except Exception as e:
        app.logger.error(f"Error loading community data: {str(e)}")
        return {"discussions": []}

def save_community_data(data):
    """Save community data to JSON file"""
    try:
        with open('community.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error saving community data: {str(e)}")

def load_clubs_data():
    """Load clubs data from JSON file"""
    try:
        if os.path.exists('clubs.json'):
            with open('clubs.json', 'r') as f:
                return json.load(f)
        else:
            return {"clubs": [], "next_id": 1}
    except Exception as e:
        app.logger.error(f"Error loading clubs data: {str(e)}")
        return {"clubs": [], "next_id": 1}

def save_clubs_data(data):
    """Save clubs data to JSON file"""
    try:
        with open('clubs.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app.logger.error(f"Error saving clubs data: {str(e)}")
        raise

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

@app.route('/vote/<int:file_id>', methods=['POST'])
def vote_file(file_id):
    """Handle like/dislike votes for files"""
    try:
        vote_type = request.json.get('vote_type')  # 'like' or 'dislike'
        
        if vote_type not in ['like', 'dislike']:
            return jsonify({'success': False, 'error': 'Invalid vote type'}), 400
        
        data = load_data()
        files = data.get('files', [])
        
        # Find the file
        file_found = False
        for file in files:
            if file['id'] == file_id:
                file_found = True
                
                # Initialize vote counts if not present
                if 'likes' not in file:
                    file['likes'] = 0
                if 'dislikes' not in file:
                    file['dislikes'] = 0
                
                # Increment the vote count
                if vote_type == 'like':
                    file['likes'] += 1
                else:
                    file['dislikes'] += 1
                
                break
        
        if not file_found:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Save updated data
        save_data(data)
        
        return jsonify({
            'success': True,
            'likes': file['likes'],
            'dislikes': file['dislikes']
        })
        
    except Exception as e:
        app.logger.error(f"Vote error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/comment/<int:file_id>', methods=['POST'])
def add_comment(file_id):
    """Add a comment to a file"""
    try:
        comment_data = request.json
        name = comment_data.get('name', '').strip()
        comment_text = comment_data.get('comment', '').strip()
        file_type = comment_data.get('file_type', 'QP')  # 'QP' or 'Syllabus'
        
        if not name or not comment_text:
            return jsonify({'success': False, 'error': 'Name and comment are required'}), 400
        
        data = load_data()
        
        # Choose the right file list based on file type
        if file_type == 'Syllabus':
            files = data.get('syllabus_files', [])
        else:
            files = data.get('files', [])
        
        # Find the file
        file_found = False
        for file in files:
            if file['id'] == file_id:
                file_found = True
                
                # Initialize comments if not present
                if 'comments' not in file:
                    file['comments'] = []
                
                # Add the new comment
                new_comment = {
                    'name': name,
                    'comment': comment_text,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                file['comments'].append(new_comment)
                
                break
        
        if not file_found:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Save updated data
        save_data(data)
        
        return jsonify({
            'success': True,
            'comment': new_comment,
            'total_comments': len(file['comments'])
        })
        
    except Exception as e:
        app.logger.error(f"Comment error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/vote_syllabus/<int:file_id>', methods=['POST'])
def vote_syllabus_file(file_id):
    """Handle like/dislike votes for syllabus files"""
    try:
        vote_type = request.json.get('vote_type')  # 'like' or 'dislike'
        
        if vote_type not in ['like', 'dislike']:
            return jsonify({'success': False, 'error': 'Invalid vote type'}), 400
        
        data = load_data()
        files = data.get('syllabus_files', [])
        
        # Find the file
        file_found = False
        for file in files:
            if file['id'] == file_id:
                file_found = True
                
                # Initialize vote counts if not present
                if 'likes' not in file:
                    file['likes'] = 0
                if 'dislikes' not in file:
                    file['dislikes'] = 0
                
                # Increment the vote count
                if vote_type == 'like':
                    file['likes'] += 1
                else:
                    file['dislikes'] += 1
                
                break
        
        if not file_found:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Save updated data
        save_data(data)
        
        return jsonify({
            'success': True,
            'likes': file['likes'],
            'dislikes': file['dislikes']
        })
        
    except Exception as e:
        app.logger.error(f"Vote error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/file/<int:file_id>')
def file_detail(file_id):
    """Display detailed view of a file"""
    try:
        data = load_data()
        
        # Search in regular files first
        file_found = None
        file_type = 'QP'
        
        for file in data.get('files', []):
            if file['id'] == file_id:
                file_found = file
                file_type = 'QP'
                break
        
        # Search in syllabus files if not found
        if not file_found:
            for file in data.get('syllabus_files', []):
                if file['id'] == file_id:
                    file_found = file
                    file_type = 'Syllabus'
                    break
        
        if not file_found:
            flash('File not found.', 'error')
            return redirect(url_for('index'))
        
        # Check if the physical file exists
        if 'filename' in file_found:
            file_path = os.path.join(UPLOAD_FOLDER, file_found['filename'])
            if not os.path.exists(file_path):
                app.logger.warning(f"Database has file {file_found['filename']} but physical file missing")
                flash('File has been deleted or moved. Please contact administrator.', 'error')
                return redirect(url_for('index'))
        
        # Ensure social fields exist
        if 'likes' not in file_found:
            file_found['likes'] = 0
        if 'dislikes' not in file_found:
            file_found['dislikes'] = 0
        if 'comments' not in file_found:
            file_found['comments'] = []
        
        return render_template('file_detail.html', 
                             file=file_found, 
                             file_type=file_type)
        
    except Exception as e:
        app.logger.error(f"File detail error: {str(e)}")
        flash('Error loading file details.', 'error')
        return redirect(url_for('index'))

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
            description = request.form.get('description', '').strip()
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
                        "description": description,
                        "size": get_file_size(filepath),
                        "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "file_path": filepath,
                        "likes": 0,
                        "dislikes": 0,
                        "comments": []
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
                # Get form data for syllabus
                custom_filename = request.form.get('custom_filename', '').strip()
                description = request.form.get('description', '').strip()
                
                file_info = {
                    'id': new_id,
                    'filename': unique_filename,
                    'original_filename': original_filename,
                    'custom_filename': custom_filename or original_filename,
                    'file_size': file_size,
                    'file_extension': file_extension,
                    'course_type': course_type,
                    'department': dept_id,
                    'regulation': regulation,
                    'description': description,
                    'size': f"{file_size / (1024*1024):.1f} MB" if file_size > 1024*1024 else f"{file_size / 1024:.1f} KB",
                    'upload_date': datetime.now().isoformat(),
                    'file_path': filepath,
                    'likes': 0,
                    'dislikes': 0,
                    'comments': []
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

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files securely"""
    try:
        # Security check: ensure filename doesn't contain path traversal
        if '..' in filename or filename.startswith('/'):
            app.logger.warning(f"Invalid file path attempted: {filename}")
            return "Invalid file path", 400
        
        # Construct absolute path
        file_path = os.path.join(os.path.abspath(UPLOAD_FOLDER), filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            # List available files for debugging
            available_files = []
            if os.path.exists(UPLOAD_FOLDER):
                available_files = os.listdir(UPLOAD_FOLDER)
            app.logger.info(f"Available files in uploads: {available_files}")
            return "File not found", 404
        
        # Verify file is within uploads directory (additional security)
        if not file_path.startswith(os.path.abspath(UPLOAD_FOLDER)):
            app.logger.warning(f"File path outside uploads directory: {file_path}")
            return "Invalid file path", 400
            
        return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename, as_attachment=False)
    except Exception as e:
        app.logger.error(f"Error serving file {filename}: {str(e)}")
        return f"Error serving file: {str(e)}", 500

@app.route('/community')
def community():
    """Community discussion page"""
    community_data = load_community_data()
    discussions = community_data.get('discussions', [])
    return render_template('community.html', discussions=discussions)

@app.route('/community/create', methods=['POST'])
def create_discussion():
    """Create a new discussion"""
    try:
        data = request.json
        name = data.get('name', 'Anonymous').strip()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title or not description:
            return jsonify({'success': False, 'error': 'Title and description are required'}), 400
        
        community_data = load_community_data()
        
        # Generate unique ID
        max_id = 0
        for discussion in community_data.get('discussions', []):
            if discussion.get('id', 0) > max_id:
                max_id = discussion['id']
        new_id = max_id + 1
        
        # Create new discussion
        new_discussion = {
            'id': new_id,
            'name': name,
            'title': title,
            'description': description,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'replies': []
        }
        
        community_data['discussions'].insert(0, new_discussion)  # Add to beginning
        save_community_data(community_data)
        
        return jsonify({'success': True, 'discussion': new_discussion})
        
    except Exception as e:
        app.logger.error(f"Error creating discussion: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/community/reply', methods=['POST'])
def add_discussion_reply():
    """Add a reply to a discussion"""
    try:
        data = request.json
        discussion_id = data.get('discussion_id')
        name = data.get('name', 'Anonymous').strip()  
        message = data.get('message', '').strip()
        
        if not discussion_id or not message:
            return jsonify({'success': False, 'error': 'Discussion ID and message are required'}), 400
        
        community_data = load_community_data()
        
        # Find the discussion
        discussion_found = False
        for discussion in community_data.get('discussions', []):
            if discussion['id'] == discussion_id:
                discussion_found = True
                
                # Initialize replies if not present
                if 'replies' not in discussion:
                    discussion['replies'] = []
                
                # Add new reply
                new_reply = {
                    'name': name,
                    'message': message,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                discussion['replies'].append(new_reply)
                break
        
        if not discussion_found:
            return jsonify({'success': False, 'error': 'Discussion not found'}), 404
        
        save_community_data(community_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        app.logger.error(f"Error adding reply: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/clubs')
def clubs():
    """Student Clubs page"""
    clubs_data = load_clubs_data()
    return render_template('clubs.html', clubs=clubs_data.get('clubs', []))

@app.route('/clubs/add')
def add_club():
    """Add new club page (admin only)"""
    # Simple admin check via URL parameter
    if request.args.get('admin') != 'true':
        flash('Admin access required to add clubs.', 'error')
        return redirect(url_for('clubs'))
    
    return render_template('add_club.html')

@app.route('/clubs/add', methods=['POST'])
def add_club_post():
    """Handle club addition"""
    try:
        # Simple admin check
        if request.args.get('admin') != 'true':
            flash('Admin access required to add clubs.', 'error')
            return redirect(url_for('clubs'))
        
        club_name = request.form.get('club_name', '').strip()
        description = request.form.get('description', '').strip()
        instagram_link = request.form.get('instagram_link', '').strip()
        
        if not club_name:
            flash('Club name is required.', 'error')
            return redirect(url_for('add_club') + '?admin=true')
        
        # Handle file upload
        screenshot_filename = None
        if 'instagram_screenshot' in request.files:
            file = request.files['instagram_screenshot']
            if file and file.filename:
                # Create clubs upload directory
                clubs_upload_dir = os.path.join(UPLOAD_FOLDER, 'clubs')
                os.makedirs(clubs_upload_dir, exist_ok=True)
                
                # Secure filename and save
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                screenshot_filename = timestamp + filename
                file_path = os.path.join(clubs_upload_dir, screenshot_filename)
                file.save(file_path)
        
        # Load existing clubs data
        clubs_data = load_clubs_data()
        
        # Create new club entry
        new_club = {
            'id': clubs_data.get('next_id', 1),
            'name': club_name,
            'description': description if description else None,
            'instagram_link': instagram_link if instagram_link else None,
            'instagram_screenshot': screenshot_filename,
            'created_at': datetime.now().isoformat()
        }
        
        # Add to clubs list and update next_id
        clubs_data['clubs'].append(new_club)
        clubs_data['next_id'] = clubs_data.get('next_id', 1) + 1
        
        # Save to file
        save_clubs_data(clubs_data)
        
        flash(f'Club "{club_name}" added successfully!', 'success')
        return redirect(url_for('clubs'))
        
    except Exception as e:
        app.logger.error(f"Error adding club: {str(e)}")
        flash(f'Error adding club: {str(e)}', 'error')
        return redirect(url_for('add_club') + '?admin=true')

@app.route('/clubs/screenshot/<filename>')
def club_screenshot(filename):
    """Serve club screenshots securely"""
    try:
        # Security check: ensure filename doesn't contain path traversal
        if '..' in filename or filename.startswith('/'):
            app.logger.warning(f"Invalid file path attempted: {filename}")
            return "Invalid file path", 400
        
        clubs_dir = os.path.join(UPLOAD_FOLDER, 'clubs')
        file_path = os.path.join(clubs_dir, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            app.logger.error(f"Club screenshot not found: {file_path}")
            return "File not found", 404
        
        # Verify file is within clubs directory (fix path normalization)
        clubs_dir_abs = os.path.abspath(clubs_dir)
        file_path_abs = os.path.abspath(file_path)
        if not file_path_abs.startswith(clubs_dir_abs):
            app.logger.warning(f"File path outside clubs directory: {file_path_abs}")
            return "Invalid file path", 400
            
        return send_from_directory(clubs_dir_abs, filename, as_attachment=False)
    except Exception as e:
        app.logger.error(f"Error serving club screenshot {filename}: {str(e)}")
        return f"Error serving file: {str(e)}", 500

@app.route('/admin/clubs/delete/<int:club_id>', methods=['POST'])
def delete_club(club_id):
    """Delete a club (admin only)"""
    try:
        # Simple admin check
        if request.args.get('admin') != 'true':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        clubs_data = load_clubs_data()
        clubs = clubs_data.get('clubs', [])
        
        # Find and remove the club
        club_found = False
        club_to_delete = None
        for i, club in enumerate(clubs):
            if club['id'] == club_id:
                club_to_delete = clubs.pop(i)
                club_found = True
                break
        
        if not club_found:
            return jsonify({'success': False, 'error': 'Club not found'}), 404
        
        # Delete screenshot file if exists
        if club_to_delete and club_to_delete.get('instagram_screenshot'):
            screenshot_path = os.path.join(UPLOAD_FOLDER, 'clubs', club_to_delete['instagram_screenshot'])
            if os.path.exists(screenshot_path):
                try:
                    os.remove(screenshot_path)
                except Exception as e:
                    app.logger.warning(f"Could not delete screenshot file: {str(e)}")
        
        # Save updated data
        save_clubs_data(clubs_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        app.logger.error(f"Error deleting club: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)