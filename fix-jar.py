#!/usr/bin/env python3
"""Replace class files in a Spring Boot fat JAR."""
import sys
import zipfile
import shutil
import os
import base64

def fix_jar(jar_path, class_files):
    """class_files: dict of {internal_path: base64_content}"""
    tmp_path = jar_path + '.tmp'
    
    # Read all content from original JAR
    with zipfile.ZipFile(jar_path, 'r') as zin:
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename in class_files:
                    print(f"Replacing: {item.filename}")
                    data = base64.b64decode(class_files[item.filename])
                zout.writestr(item, data)
    
    os.replace(tmp_path, jar_path)
    print(f"Done: {jar_path}")

if __name__ == '__main__':
    jar = sys.argv[1]
    # Remaining args are "path:base64data" pairs
    class_files = {}
    for arg in sys.argv[2:]:
        if ':' in arg:
            path, b64 = arg.split(':', 1)
            class_files[path] = b64
    
    if not class_files:
        print("No class files provided")
        sys.exit(1)
    
    fix_jar(jar, class_files)
