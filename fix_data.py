#!/usr/bin/env python3
"""
Script to fix existing data.json entries to use normalized keys
"""
import json

def normalize_course_type(ct):
    return ct.lower() if ct else ct

def normalize_department(dept):
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

def fix_data():
    # Load existing data
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    # Fix files array
    if 'files' in data:
        for file_entry in data['files']:
            if 'course_type' in file_entry:
                file_entry['course_type'] = normalize_course_type(file_entry['course_type'])
            if 'department' in file_entry:
                file_entry['department'] = normalize_department(file_entry['department'])
    
    # Save updated data
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Data normalization complete!")
    print("Fixed entries:")
    for file_entry in data.get('files', []):
        print(f"  File {file_entry['id']}: {file_entry['course_type']}/{file_entry['department']}/{file_entry['semester']}/{file_entry['category']}")

if __name__ == "__main__":
    fix_data()