import os
import shutil
import json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

COURSES_DATABASE = os.path.join(ROOT_DIR, "courses.json")
FILE_DIR = os.path.join(ROOT_DIR, "file_storage")

def init_database():
    if not os.path.exists(COURSES_DATABASE):
        with open(COURSES_DATABASE, 'w') as f:
            json.dump([], f, indent=4)

def init_directory():
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)

def load_data(filepath=COURSES_DATABASE):
    with open(filepath, "r") as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def add_file_to_storage(local_path):
    init_directory()
    file_name = os.path.basename(local_path)
    destination = os.path.join(FILE_DIR, file_name)
    shutil.copy(local_path, destination)
    return file_name

def delete_file_in_storage(local_path):
    if local_path:
        file_name = os.path.join(FILE_DIR, local_path)
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except OSError:
                pass

def add_file_to_course(course, local_file_path):
    target_course = course.strip()
    course_list = load_data(COURSES_DATABASE)
    course_found = False
    new_file = os.path.basename(local_file_path)

    for c in course_list:
        if c['course_name'] == target_course:
            for existing_file in c['course_files']:
                if os.path.basename(existing_file) == new_file:
                    raise ValueError(f"The file '{new_file}' is already uploaded.")
                
            saved_path = add_file_to_storage(local_file_path)
            c['course_files'].append(saved_path)
            course_found = True
            break
    
    if not course_found:
        raise ValueError (f"Course '{target_course}' does not exist. ")
    
    save_data(COURSES_DATABASE, course_list)

def delete_file_in_course(course, local_file_path):
    target_course = course.strip()

    courses = load_data(COURSES_DATABASE)
    course_found = False

    for c in courses:
        if c['course_name'] == target_course:
            if local_file_path in c['course_files']:
                delete_file_in_storage(local_file_path)
                c['course_files'].remove(local_file_path)
                course_found = True
                break
    
    if not course_found:
        raise ValueError("File or course could not be found.")
    
    save_data(COURSES_DATABASE, courses)






