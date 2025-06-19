# College Materials & PYQs Portal

## Overview

A comprehensive Flask-based web portal designed for college students to upload, organize, and download study materials, previous year question papers (PYQs), and academic resources. The application features a hierarchical navigation system organized by course types (UG/PG/MBA), departments, semesters, and categories.

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.0+ (Python web framework)
- **Data Storage**: JSON-based file storage system with `data.json` as the primary data store
- **File Storage**: Local filesystem with organized directory structure in `uploads/` folder
- **Session Management**: Flask's built-in session handling with configurable secret key
- **Web Server**: Gunicorn WSGI server for production deployment

### Frontend Architecture
- **CSS Framework**: Bootstrap 5.3 for responsive design
- **Icons**: Font Awesome 6.4 for consistent iconography
- **JavaScript**: Vanilla JavaScript for client-side functionality
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **UI Components**: Card-based layout with table and card view toggles

### Key Architectural Decisions
1. **JSON over Database**: Chosen for simplicity and rapid prototyping, avoiding database setup complexity
2. **File-based Storage**: Direct filesystem storage for uploaded files with secure filename handling
3. **Hierarchical Navigation**: Multi-level navigation structure (Course Type → Department → Semester → Category → Files)
4. **Responsive Design**: Mobile-first approach using Bootstrap's grid system

## Key Components

### Core Application Structure
- **Main Application** (`app.py`): Primary Flask application with all route handlers
- **Entry Point** (`main.py`): Application startup script for development
- **Data Models** (`models.py`): SQLAlchemy models (prepared for potential database migration)
- **Configuration**: Environment-based configuration with development defaults

### Navigation Hierarchy
1. **Course Types**: UG (8 semesters), PG (4 semesters), MBA (4 semesters), 5-year programs (10 semesters)
2. **Departments**: CSE, MECH, EEE, ECE, IT, CHEM, CIVIL, various PG specializations
3. **Categories**: CAT, ESE, SAT, Practical files for academic assessments
4. **File Management**: Upload, view, download, and delete functionality

### Calculator Suite
- **GPA Calculator**: Single semester grade point calculation
- **CGPA Calculator**: Multi-semester cumulative grade calculation  
- **Percentage Calculator**: GPA/CGPA to percentage conversion
- **Internal Marks Calculator**: CAT, SAT, assignment, and viva mark processing

## Data Flow

### File Upload Process
1. User selects course type, department, semester, category, and subject
2. File validation and secure filename generation using Werkzeug
3. File stored in organized directory structure: `uploads/[course]/[dept]/[semester]/[category]/`
4. Metadata stored in `data.json` with file paths and details

### Navigation Flow
1. Home → Course Types (UG/PG/MBA)
2. Course Type → Departments (CSE, MECH, etc.)
3. Department → Semesters (1-8 for UG, 1-4 for PG/MBA)
4. Semester → Categories (CAT, ESE, SAT, Practical)
5. Category → File listing with download/view options

### Calculator Data Flow
1. Form input validation on client-side
2. Grade/credit calculations using predefined mappings
3. Real-time result display with detailed breakdown tables
4. Local storage for preserving user input across sessions

## External Dependencies

### Python Dependencies
- **Flask**: Web framework and routing
- **Werkzeug**: File upload security and utilities
- **Gunicorn**: Production WSGI server
- **Optional**: SQLAlchemy, psycopg2-binary (prepared for database migration)

### Frontend Dependencies
- **Bootstrap 5.3**: CSS framework loaded via CDN
- **Font Awesome 6.4**: Icon library via CDN
- **No build process**: Direct HTML/CSS/JS approach for simplicity

### Development Environment
- **Replit Configuration**: Multi-language support (Python 3.11, Node.js 20, web modules)
- **Nix Packages**: System-level dependencies for image processing and multimedia support

## Deployment Strategy

### Current Deployment
- **Platform**: Replit with autoscale deployment target
- **Server**: Gunicorn binding to 0.0.0.0:5000
- **Port Mapping**: Internal 5000 → External 80
- **Process Management**: Replit workflows with automatic restart and reload capabilities

### Production Considerations
- **Database Migration**: Prepared SQLAlchemy models for PostgreSQL migration
- **File Storage**: Current local storage can be migrated to cloud storage (AWS S3, etc.)
- **Environment Variables**: Session secret and database URL configuration
- **Scaling**: Stateless design allows horizontal scaling with shared storage

### Security Measures
- **File Upload**: Werkzeug secure filename handling
- **Input Validation**: Form validation for all user inputs
- **Session Security**: Configurable secret key for session management
- **No File Size Limits**: Currently unrestricted (configurable for production)

## Changelog

- June 19, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.