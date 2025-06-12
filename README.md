# College Materials & PYQs Portal

A comprehensive web portal for college students to upload, organize, and download study materials, previous year question papers (PYQs), and academic resources.

## Features

### 📚 Course Structure
- **UG (Under Graduate)**: CSE, MECH, EEE, ECE, IT, CHEM, CIVIL
- **PG (Post Graduate)**: M.Tech CSE (5-Year), M.E Applied Electronics, M.E Structural, M.E PED
- **MBA**: General MBA

### 🗂️ Navigation Hierarchy
1. **Course Types** → Select UG/PG/MBA
2. **Departments** → Select specific department
3. **Semesters** → Choose semester (1-8 for UG, 1-4 for PG/MBA, 1-10 for 5-year programs)
4. **Categories** → CAT, ESE, SAT, Practical files
5. **File Management** → View, download, delete files

### 📁 File Categories
- **CAT**: Continuous Assessment Tests
- **ESE**: End Semester Examinations  
- **SAT**: Semester Assessment Tests
- **Practical**: Practical Examinations

### 🎨 User Interface
- **Responsive Design**: Bootstrap-based responsive layout
- **Table & Card Views**: Toggle between table and card view for files
- **Smooth Navigation**: Breadcrumb navigation with smooth transitions
- **File Type Icons**: Visual indicators for different file types
- **Search Functionality**: Search through uploaded files

### 📤 Upload System
- **Multi-field Selection**: Course type, department, semester, category, subject
- **Custom File Names**: Option to provide custom display names
- **File Validation**: Support for documents, presentations, images, and archives
- **Duplicate Handling**: Automatic handling of duplicate filenames

## Technology Stack

### Backend
- **Flask**: Python web framework
- **JSON Storage**: Simple file-based data storage
- **Werkzeug**: File upload handling and security

### Frontend
- **Bootstrap 5.3**: Responsive CSS framework
- **Font Awesome 6.4**: Icon library
- **Vanilla JavaScript**: Client-side functionality
- **Custom CSS**: Enhanced styling and animations

### File Support
- **Documents**: PDF, DOC, DOCX, TXT, RTF, ODT
- **Presentations**: PPT, PPTX
- **Spreadsheets**: XLS, XLSX, CSV
- **Images**: JPG, JPEG, PNG, GIF, BMP
- **Archives**: ZIP, RAR, 7Z, TAR, GZ

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd college-materials-portal
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Access the portal**
   Open your browser and navigate to `http://localhost:5000`

### Environment Variables (Optional)
- `SESSION_SECRET`: Custom session secret key (defaults to development key)

## Project Structure

```
college-materials-portal/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── models.py             # Data models (legacy, not used in current version)
├── data.json             # JSON database file (auto-generated)
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Custom CSS styles
│   └── js/
│       └── main.js      # JavaScript functionality
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Course types page
│   ├── course_type.html # Departments page
│   ├── department.html  # Semesters page
│   ├── semester.html    # Categories page
│   ├── category.html    # Files listing page
│   └── upload.html      # File upload page
└── uploads/             # Uploaded files directory
```

## Data Storage

The application uses a simple JSON file (`data.json`) for data persistence. The structure includes:

```json
{
  "course_types": {
    "ug": {
      "name": "Under Graduate (UG)",
      "departments": {
        "cse": {
          "name": "Computer Science & Engineering",
          "semesters": {...}
        }
      }
    }
  },
  "files": [
    {
      "id": 1,
      "filename": "actual_filename.pdf",
      "custom_filename": "display_name.pdf",
      "course_type": "ug",
      "department": "cse",
      "semester": "1",
      "category": "CAT",
      "subject": "Mathematics",
      "size": "2.5 MB",
      "upload_date": "2024-01-15 10:30:00",
      "file_path": "uploads/actual_filename.pdf"
    }
  ]
}
```

## API Endpoints

### Navigation Routes
- `GET /` - Course types listing
- `GET /course/<course_type_id>` - Departments listing
- `GET /department/<course_type_id>/<dept_id>` - Semesters listing
- `GET /semester/<course_type_id>/<dept_id>/<semester_id>` - Categories listing
- `GET /category/<course_type_id>/<dept_id>/<semester_id>/<category>` - Files listing

### File Management Routes
- `GET /upload` - Upload form
- `POST /upload` - File upload handler
- `GET /download/<file_id>` - File download
- `GET /delete/<file_id>` - File deletion

## Features in Detail

### File Upload Process
1. Select course type (UG/PG/MBA)
2. Choose department from available options
3. Pick semester (dynamically loaded based on department)
4. Select category (CAT/ESE/SAT/Practical)
5. Enter subject name
6. Optionally provide custom filename
7. Upload file (max 16MB)

### File Management
- **View**: Table and card view options
- **Download**: Direct file download with original names
- **Delete**: Secure file deletion with confirmation
- **Search**: Real-time search through file listings

### Security Features
- **Filename Sanitization**: Secure filename handling
- **File Type Validation**: Restricted file types
- **Size Limits**: 16MB maximum file size
- **Path Security**: Prevents directory traversal attacks

## Customization

### Adding New Departments
Edit the `data.json` file to add new departments under the appropriate course type:

```json
"new_dept_id": {
  "name": "New Department Name",
  "semesters": {
    "1": {"name": "Semester 1"},
    "2": {"name": "Semester 2"}
  }
}
```

### Modifying Categories
Update the categories list in `app.py`:

```python
categories = ['CAT', 'ESE', 'SAT', 'Practical', 'Assignment']
```

### Styling Customization
- Modify `static/css/style.css` for visual changes
- Update `static/js/main.js` for functionality changes
- Edit templates in `templates/` for layout modifications

## Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## Future Enhancements

### Planned Features
- User authentication and authorization
- File versioning system
- Advanced search and filtering
- File sharing and collaboration
- Mobile app integration
- Database migration (SQLite/PostgreSQL)
- Bulk file operations
- File preview functionality
- Email notifications
- Analytics and reporting

### Technical Improvements
- Database optimization
- Caching implementation
- API rate limiting
- Enhanced security measures
- Performance monitoring
- Automated testing
- CI/CD pipeline
- Docker containerization

---

**Built with ❤️ for students by developers who understand the academic journey.**