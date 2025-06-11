import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
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
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt',
    'ppt', 'pptx', 'xls', 'xlsx', 'csv',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'zip', 'rar', '7z', 'tar', 'gz'
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

def get_file_category(filename):
    """Categorize file based on extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext in ['pdf']:
        return 'PDF Documents'
    elif ext in ['doc', 'docx', 'txt', 'rtf', 'odt']:
        return 'Text Documents'
    elif ext in ['ppt', 'pptx']:
        return 'Presentations'
    elif ext in ['xls', 'xlsx', 'csv']:
        return 'Spreadsheets'
    elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
        return 'Images'
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz']:
        return 'Archives'
    else:
        return 'Other Files'

@app.route('/')
def index():
    """Homepage showing all uploaded files"""
    try:
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                if filename != '.gitkeep':
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    if os.path.isfile(filepath):
                        file_stat = os.stat(filepath)
                        files.append({
                            'name': filename,
                            'size': get_file_size(filepath),
                            'category': get_file_category(filename),
                            'upload_date': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'extension': filename.rsplit('.', 1)[1].lower() if '.' in filename else 'none'
                        })
        
        # Group files by category
        categories = {}
        for file in files:
            category = file['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(file)
        
        return render_template('index.html', categories=categories, total_files=len(files))
    
    except Exception as e:
        app.logger.error(f"Error loading files: {str(e)}")
        flash('Error loading files. Please try again.', 'error')
        return render_template('index.html', categories={}, total_files=0)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload new files"""
    if request.method == 'POST':
        try:
            # Check if files were uploaded
            if 'files' not in request.files:
                flash('No files selected', 'error')
                return redirect(request.url)
            
            files = request.files.getlist('files')
            uploaded_count = 0
            
            for file in files:
                if file and file.filename:
                    if allowed_file(file.filename):
                        # Secure the filename
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
                        uploaded_count += 1
                        app.logger.info(f"File uploaded: {filename}")
                    
                    else:
                        flash(f'File type not allowed: {file.filename}', 'error')
            
            if uploaded_count > 0:
                flash(f'Successfully uploaded {uploaded_count} file(s)', 'success')
                return redirect(url_for('index'))
            else:
                flash('No valid files were uploaded', 'error')
        
        except Exception as e:
            app.logger.error(f"Upload error: {str(e)}")
            flash('An error occurred during upload. Please try again.', 'error')
    
    return render_template('upload.html', allowed_extensions=ALLOWED_EXTENSIONS)

@app.route('/download/<filename>')
def download(filename):
    """Download a file"""
    try:
        # Secure the filename
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            flash('File not found', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        flash('Error downloading file', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<filename>')
def delete(filename):
    """Delete a file"""
    try:
        # Secure the filename
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Delete physical file
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
            flash(f'File "{filename}" deleted successfully', 'success')
            app.logger.info(f"File deleted: {filename}")
        else:
            flash('File not found', 'error')
    
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
    return render_template('index.html', categories={}, total_files=0), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)