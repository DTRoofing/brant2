#!/usr/bin/env python3
"""Fix all import statements to use app. prefix"""

import os
import re

def fix_imports_in_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Patterns to replace
    replacements = [
        (r'from core\.', 'from app.core.'),
        (r'from models\.', 'from app.models.'),
        (r'from services\.', 'from app.services.'),
        (r'from workers\.', 'from app.workers.'),
        (r'from api\.', 'from app.api.'),
    ]
    
    modified = False
    for pattern, replacement in replacements:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            modified = True
            content = new_content
    
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed imports in: {filepath}")
        return True
    return False

def main():
    """Walk through app directory and fix all Python files"""
    app_dir = '/mnt/c/Development/Final Build/brant/app'
    fixed_count = 0
    
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    print(f"\nFixed imports in {fixed_count} files")

if __name__ == '__main__':
    main()