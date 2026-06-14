import os
import json
import subprocess
import sys
from tkinter import *
from tkinter import messagebox

# Import the centralized database configuration
import database_for_courses as db

# 1. System Directories and Session Setup
# Save the session file strictly within the base directory of the scripts.
SESSION_FILE = os.path.join(db.BASE_DIR, "current_user.json")

# Dynamic profile setup synchronized with the LMS architecture.
student_name = "Christian Bergola"
student_email = "christian.bergola@edu.ph"

if os.path.exists(SESSION_FILE):
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as file:
            user_data = json.load(file)
            student_name = user_data.get("fullname", "Christian Bergola")
            student_email = user_data.get("email", "christian.bergola@edu.ph")
    except Exception:
        pass

initials = "".join([part[0].upper() for part in student_name.split()[:2]]) if student_name else "CB"

# 2. Dynamic Data Streaming Manager
def load_courses():
    """Reads courses directly from the shared database file populated by the Professor app."""
    if not os.path.exists(db.COURSES_DATABASE):
        with open(db.COURSES_DATABASE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
        return []
    try:
        with open(db.COURSES_DATABASE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [c for c in data if isinstance(c, dict)]
            return []
    except Exception:
        return []

def save_courses(data):
    try:
        with open(db.COURSES_DATABASE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error synchronizing layout state: {e}")

def open_student_file(file_name):
    # Rely entirely on the shared module for the file storage path.
    file_path = os.path.join(db.FILE_DIR, file_name)
    
    if os.path.exists(file_path):
        if sys.platform.startswith("win"):
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", file_path])
        else:
            subprocess.Popen(["xdg-open", file_path])
    else:
        messagebox.showerror("Error", f"File not found at: {file_path}")

# Live runtime array directly linked to submissions.
courses_data = load_courses()

# 3. Master Application Window Initialization
root = Tk()
root.title("EduLearn LMS - Student Dashboard")
root.state("zoomed")
root.configure(bg="#f4e8e8") 

# Global badge setup tracking enrollment metrics dynamically.
enrolled_count_var = StringVar()

def update_enrolled_count():
    count = sum(1 for c in courses_data if student_email in c.get("enrolled_students", []))
    enrolled_count_var.set(str(count))

# 4. Scrollable Canvas Container Generator
def create_scrollable_page(parent):
    container = Frame(parent, bg="#f4e8e8")
    container.pack(fill="both", expand=True)

    canvas = Canvas(container, bg="#f4e8e8", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = Frame(canvas, bg="#f4e8e8")

    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def _mouse_scroll_event(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _mouse_scroll_event)
        
    return scrollable_frame

# 5. Sidebar Navigation Core Panel Layout
sidebar = Frame(root, width=260, bg="#800000") 
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

logo_frame = Frame(sidebar, bg="#800000")
logo_frame.pack(anchor="w", pady=(25, 30), padx=20)

fav_container = Frame(logo_frame, width=42, height=42, bg="#f7c948")
fav_container.pack(side="left", padx=(0, 10))
fav_container.pack_propagate(False)
Label(fav_container, text="🎓", font=("Arial", 18), fg="#800000", bg="#f7c948").pack(expand=True)

text_logo = Frame(logo_frame, bg="#800000")
text_logo.pack(side="left")
Label(text_logo, text="EduLearn", font=("Plus Jakarta Sans", 18, "bold"), fg="#f7c948", bg="#800000").pack(anchor="w")
Label(text_logo, text="Learning Management System", font=("Inter", 8), fg="#e0e0e0", bg="#800000").pack(anchor="w")

# 6. App Multi-Page View Controller
right_container = Frame(root, bg="#f4e8e8")
right_container.pack(side="left", fill="both", expand=True)

header = Frame(right_container, bg="#f4e8e8")
header.pack(fill="x", padx=35, pady=(20, 10))

text_frame = Frame(header, bg="#f4e8e8")
text_frame.pack(side="left")
Label(text_frame, text="Welcome back, Iskolar ng Bayan", font=("Inter", 11), fg="#8a8a8a", bg="#f4e8e8").pack(anchor="w")
Label(text_frame, text=student_name, font=("Plus Jakarta Sans", 22, "bold"), fg="black", bg="#f4e8e8").pack(anchor="w")

profile = Frame(header, width=220, height=55, bg="white", highlightbackground="#e5dcd1", highlightthickness=1)
profile.pack(side="right", pady=5)
profile.pack_propagate(False)

avatar_lbl = Label(profile, text=initials, bg="#f7c948", fg="black", font=("Inter", 10, "bold"), width=4, height=2)
avatar_lbl.pack(side="left", padx=10, pady=8)

info = Frame(profile, bg="white")
info.pack(side="left", fill="y", pady=8)
Label(info, text=student_name, bg="white", font=("Inter", 10, "bold"), fg="black").pack(anchor="w")
Label(info, text="Student", bg="white", fg="gray", font=("Inter", 9)).pack(anchor="w")

page_container = Frame(right_container, bg="#f4e8e8")
page_container.pack(fill="both", expand=True)

dashboard_page = Frame(page_container, bg="#f4e8e8")
mycourses_page = Frame(page_container, bg="#f4e8e8")
browse_page = Frame(page_container, bg="#f4e8e8")
resources_page = Frame(page_container, bg="#f4e8e8")

for pg in (dashboard_page, mycourses_page, browse_page, resources_page):
    pg.place(relx=0, rely=0, relwidth=1, relheight=1)

dashboard_content = create_scrollable_page(dashboard_page)
mycourses_content = create_scrollable_page(mycourses_page)
browse_content = create_scrollable_page(browse_page)
resources_content = create_scrollable_page(resources_page)

def show_page(page):
    global courses_data
    courses_data = load_courses() 
    update_enrolled_count()
    render_dashboard_feed()
    render_my_courses_view()
    render_course_catalog_grid()
    render_resources_table()
    page.tkraise()

def enroll_course(target_name):
    for course in courses_data:
        if course.get("course_name") == target_name:
            if "enrolled_students" not in course:
                course["enrolled_students"] = []
                
            if student_email not in course["enrolled_students"]:
                course["enrolled_students"].append(student_email)
                save_courses(courses_data)
                update_enrolled_count()
                
                render_dashboard_feed()
                render_my_courses_view()
                render_course_catalog_grid()
                
                messagebox.showinfo("Success", f"Successfully enrolled in {target_name}!")
            break

def unenroll_course(target_name):
    for course in courses_data:
        if course.get("course_name") == target_name:
            if student_email in course.get("enrolled_students", []):
                course["enrolled_students"].remove(student_email)
                save_courses(courses_data)
                update_enrolled_count()
                
                render_dashboard_feed()
                render_my_courses_view()
                render_course_catalog_grid()
                
                messagebox.showinfo("Success", f"You have been unenrolled from {target_name}.")
            break
            
# Dynamic Course Classroom Window
def open_course_classroom(course):
    """Opens an explicit window displaying files uploaded specific to this selected course."""
    classroom = Toplevel(root)
    classroom.title(f"{course.get('course_name')} - Classroom")
    classroom.geometry("650x500")
    classroom.configure(bg="#f4e8e8")
    classroom.transient(root)
    classroom.grab_set()

    banner = Frame(classroom, bg="#800000", pady=20, padx=25)
    banner.pack(fill="x")
    
    Label(banner, text=course.get("course_name", "Untitled Course"), font=("Plus Jakarta Sans", 18, "bold"), fg="#f7c948", bg="#800000").pack(anchor="w")
    Label(banner, text=f"Instructor: {course.get('course_instructor', 'Unknown Professor')}", font=("Inter", 10), fg="#e0e0e0", bg="#800000").pack(anchor="w", pady=(2,0))

    body = Frame(classroom, bg="#f4e8e8", padx=25, pady=20)
    body.pack(fill="both", expand=True)

    Label(body, text="Course Description", font=("Plus Jakarta Sans", 12, "bold"), bg="#f4e8e8", fg="#1d2235").pack(anchor="w")
    Label(body, text=course.get("course_description", "No description provided."), font=("Inter", 10), fg="#5a5a5a", bg="#f4e8e8", justify="left", wraplength=600).pack(anchor="w", pady=(5, 20))

    Label(body, text="Shared Course Files & Learning Materials", font=("Plus Jakarta Sans", 12, "bold"), bg="#f4e8e8", fg="#1d2235").pack(anchor="w")

    files_box = Frame(body, bg="white", highlightbackground="#eaeaea", highlightthickness=1)
    files_box.pack(fill="both", expand=True, pady=(5, 10))

    files_list = course.get("course_files", [])
    if isinstance(files_list, str):
        files_list = [files_list] if files_list else []

    is_enrolled = student_email in course.get("enrolled_students", [])

    if not is_enrolled:
        Label(files_box, text="Enroll in this course to view learning materials.", font=("Inter", 10, "italic"), fg="red", bg="white").pack(pady=40, expand=True)
    elif not files_list:
        Label(files_box, text="No shared learning materials uploaded for this class yet.", font=("Inter", 10, "italic"), fg="gray", bg="white").pack(pady=40, expand=True)
    else:
        for file_name in files_list:
            if not file_name.strip(): continue
            row = Frame(files_box, bg="white", height=45, highlightbackground="#f1f1f1", highlightthickness=1)
            row.pack(fill="x")
            row.pack_propagate(False)

            Label(row, text="📄", font=("Arial", 11), fg="#f7c948", bg="white").pack(side="left", padx=(15, 5))
            Label(row, text=file_name, font=("Inter", 10, "bold"), bg="white", fg="black").pack(side="left", padx=10)
            
            btn_frame = Frame(row, bg="white")
            btn_frame.pack(side="right", padx=15, fill="y")
            
            btn = Button(
                btn_frame, 
                text="Open File", 
                bg="#800000", 
                fg="white", 
                font=("Inter", 8, "bold"), 
                relief="flat", 
                padx=10, 
                command=lambda f=file_name: open_student_file(f)
            )
            btn.pack(side="left", anchor="center", pady=10)

    Button(body, text="Close Window", command=classroom.destroy, font=("Inter", 10, "bold"), bg="#e0dcd9", fg="#5a5a5a", relief="flat", width=15, height=2).pack(anchor="e", pady=(10, 0))

# Screen 1 Layout: Dashboard Controls
dash_top = Frame(dashboard_content, bg="#f4e8e8")
dash_top.pack(fill="x", padx=35, pady=(15, 5))

Label(dash_top, text="Dashboard", bg="#f4e8e8", fg="#1d2235", font=("Plus Jakarta Sans", 24, "bold")).pack(anchor="w")
Label(dash_top, text="View the overview of your courses and progress.", bg="#f4e8e8", fg="gray", font=("Inter", 11)).pack(anchor="w", pady=(2, 15))

tile = Frame(dashboard_content, width=320, height=140, bg="#f5e3cc")
tile.pack(anchor="nw", padx=35, pady=5)
tile.pack_propagate(False)

Label(tile, text="📋", bg="#f5e3cc", font=("Arial", 22)).pack(anchor="w", padx=20, pady=(15, 2))
Label(tile, text="Enrolled Courses", bg="#f5e3cc", fg="#5a5a5a", font=("Inter", 10)).pack(anchor="w", padx=20)
Label(tile, textvariable=enrolled_count_var, bg="#f5e3cc", fg="black", font=("Plus Jakarta Sans", 28, "bold")).pack(anchor="w", padx=20, pady=2)

dash_bottom = Frame(dashboard_content, bg="#f4e8e8")
dash_bottom.pack(fill="x", padx=35, pady=(30, 20))

feed_header = Frame(dash_bottom, bg="#f4e8e8")
feed_header.pack(fill="x", pady=(0, 10))
Label(feed_header, text="Resources", font=("Plus Jakarta Sans", 16, "bold"), bg="#f4e8e8", fg="#1d2235").pack(side="left")

view_all_lbl = Label(feed_header, text="View all resources >", font=("Inter", 10, "bold"), fg="#800000", bg="#f4e8e8", cursor="hand2")
view_all_lbl.pack(side="right", pady=5)
view_all_lbl.bind("<Button-1>", lambda e: show_page(resources_page))

feed_list_container = Frame(dash_bottom, bg="#f4e8e8")
feed_list_container.pack(fill="x")

def render_dashboard_feed():
    for widget in feed_list_container.winfo_children():
        widget.destroy()

    active_feed_items = []
    for course in courses_data:
        files = course.get("course_files", [])
        attachment_name = files[0] if (isinstance(files, list) and files) else None
        
        if student_email in course.get("enrolled_students", []) and attachment_name:
            active_feed_items.append((
                attachment_name,
                course.get("course_name", "Untitled Course"),
                course.get("course_instructor", "Unknown Professor")
            ))

    if not active_feed_items:
        Label(feed_list_container, text="No shared resources available from your enrolled classes.", 
              font=("Inter", 11, "italic"), fg="gray", bg="#f4e8e8").pack(anchor="w", pady=10)
        return

    for title, subject, uploader in active_feed_items:
        card = Frame(feed_list_container, bg="white", height=75, highlightbackground="#eaeaea", highlightthickness=1)
        card.pack(fill="x", pady=4)
        card.pack_propagate(False)

        icon_box = Frame(card, width=45, height=45, bg="#800000")
        icon_box.pack(side="left", padx=15, pady=15)
        icon_box.pack_propagate(False)
        Label(icon_box, text="📄", font=("Arial", 12), fg="white", bg="#800000").pack(expand=True)

        text_area = Frame(card, bg="white")
        text_area.pack(side="left", fill="both", expand=True, pady=12)
        Label(text_area, text=title, font=("Inter", 11, "bold"), bg="white", fg="black").pack(anchor="w")
        Label(text_area, text=f"{subject}   •   Author: {uploader}", font=("Inter", 9), fg="gray", bg="white").pack(anchor="w")

        action_frame = Frame(card, bg="white")
        action_frame.pack(side="right", padx=15, fill="y")

        Button(action_frame, text="Open", bg="#800000", fg="white", activebackground="#f7c948",
        activeforeground="black", font=("Inter", 9, "bold"), relief="flat", padx=12, pady=4,
        command=lambda f=title: open_student_file(f)).pack(side="left", anchor="center", pady=22)

        Button(action_frame, text="↓", font=("Arial", 16, "bold"), fg="#800000", bg="white", relief="flat",
        command=lambda f=title: open_student_file(f)).pack(side="left", padx=(15, 5), pady=18)

# Screen 2 Layout: My Enrolled Curriculum 
def render_my_courses_view():
    for widget in mycourses_content.winfo_children():
        widget.destroy()

    bc_frame = Frame(mycourses_content, bg="#f4e8e8")
    bc_frame.pack(fill="x", padx=35, pady=(15, 0))
    Label(bc_frame, text="Dashboard  >  My Courses", font=("Inter", 9), fg="gray", bg="#f4e8e8").pack(anchor="w")

    Label(mycourses_content, text="My Courses", bg="#f4e8e8", fg="#1d2235", font=("Plus Jakarta Sans", 24, "bold")).pack(anchor="w", padx=35, pady=(5, 0))
    Label(mycourses_content, text="View and manage all your enrolled courses.", bg="#f4e8e8", fg="gray", font=("Inter", 11)).pack(anchor="w", padx=35, pady=(0, 15))

    enrolled_any = False
    for course in courses_data:
        if student_email in course.get("enrolled_students", []):
            enrolled_any = True
            card = Frame(mycourses_content, bg="white", height=125, highlightbackground="#eaeaea", highlightthickness=1)
            card.pack(fill="x", padx=35, pady=6)
            card.pack_propagate(False)

            info_box = Frame(card, bg="white")
            info_box.pack(side="left", fill="both", expand=True, padx=20, pady=12)

            course_title = course.get("course_name", "Untitled Course")
            Label(info_box, text=course_title, font=("Plus Jakarta Sans", 15, "bold"), bg="white", fg="#1d2235").pack(anchor="w")
            
            desc_lbl = Label(info_box, text=course.get("course_description", "No description provided."), font=("Inter", 10), fg="gray", bg="white", justify="left", wraplength=700)
            desc_lbl.pack(anchor="w", pady=2)

            meta_frame = Frame(info_box, bg="white")
            meta_frame.pack(anchor="w", pady=(2, 0))
            Label(meta_frame, text="Status: Active", font=("Inter", 9, "bold"), fg="green", bg="white").pack(side="left")
            
            files = course.get("course_files", [])
            attachment_name = files[0] if (isinstance(files, list) and files) else None
            if attachment_name:
                Label(meta_frame, text=" 📄 ", font=("Arial", 9), fg="gray", bg="white").pack(side="left", padx=(10, 2))
                Label(meta_frame, text=f"{len(files)} file(s) available", font=("Inter", 9), fg="gray", bg="white").pack(side="left")

            Button(card, text="Continue", bg="#800000", fg="white", font=("Inter", 10, "bold"),
            activebackground="#f7c948", activeforeground="black", relief="flat", 
            width=14, height=2, command=lambda c=course: open_course_classroom(c)).pack(side="right", padx=(10, 20), pady=35)


            Button(card, text="Unenroll", bg="#e0dcd9", fg="#5a5a5a", font=("Inter", 10, "bold"),
            activebackground="#ffcccc", activeforeground="black", relief="flat", 
            width=14, height=2, command=lambda c=course.get("course_name"): unenroll_course(c)).pack(side="right", padx=10, pady=35)
            
    if not enrolled_any:
        Label(mycourses_content, text="You have not enrolled in any tracks currently. Browse the catalog to register!", 
              font=("Inter", 12, "italic"), fg="gray", bg="#f4e8e8").pack(anchor="w", padx=35, pady=20)

# Screen 3 Layout: Course Catalog Grid
def render_course_catalog_grid():
    for widget in browse_content.winfo_children():
        widget.destroy()

    bc_frame = Frame(browse_content, bg="#f4e8e8")
    bc_frame.pack(fill="x", padx=35, pady=(15, 0))
    Label(bc_frame, text="Dashboard  >  Browse Courses", font=("Inter", 9), fg="gray", bg="#f4e8e8").pack(anchor="w")

    Label(browse_content, text="Course Catalog", font=("Plus Jakarta Sans", 24, "bold"), bg="#f4e8e8", fg="#1d2235").pack(anchor="w", padx=35, pady=(5, 0))
    Label(browse_content, text="Browse and enroll in available courses.", font=("Inter", 11), bg="#f4e8e8", fg="gray").pack(anchor="w", padx=35, pady=(0, 15))

    grid_container = Frame(browse_content, bg="#f4e8e8")
    grid_container.pack(fill="both", expand=True, padx=35, pady=5)

    if not courses_data:
        Label(grid_container, text="No courses have been created by professors yet.", 
              font=("Inter", 12, "italic"), fg="gray", bg="#f4e8e8").pack(anchor="w", pady=10)
        return

    for index, course in enumerate(courses_data):
        row = index // 2
        col = index % 2

        card = Frame(grid_container, bg="white", highlightbackground="#eaeaea", highlightthickness=1, height=175, width=440)
        card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        card.pack_propagate(False)

        grid_container.columnconfigure(col, weight=1)

        info_area = Frame(card, bg="white")
        info_area.pack(fill="both", expand=True, padx=15, pady=(12, 5))

        course_title = course.get("course_name", "Untitled Course")
        Label(info_area, text=course_title, font=("Plus Jakarta Sans", 13, "bold"), bg="white", fg="#1d2235").pack(anchor="w")
        
        prof_name = course.get("course_instructor", "Unknown Professor")
        Label(info_area, text=prof_name, font=("Inter", 9), fg="gray", bg="white").pack(anchor="w", pady=(1, 4))
        
        desc_lbl = Label(info_area, text=course.get("course_description", "No description added."), font=("Inter", 9), fg="#666666", bg="white", justify="left", wraplength=400)
        desc_lbl.pack(anchor="w")

        if student_email in course.get("enrolled_students", []):
            btn = Button(card, text="Already Enrolled", bg="#e0dcd9", fg="#7a7a7a", font=("Inter", 10, "bold"),
                         relief="flat", state="disabled", height=2)
            btn.pack(fill="x", side="bottom")
        else:
            btn = Button(card, text="+ Enroll Now", bg="#800000", fg="white", font=("Inter", 10, "bold"),
                         activebackground="#f7c948", activeforeground="black", relief="flat", height=2,
                         command=lambda name=course_title: enroll_course(name))
            btn.pack(fill="x", side="bottom")

# Screen 4 Layout: Archive Resource Tabular 
def render_resources_table():
    for widget in resources_content.winfo_children():
        widget.destroy()

    bc_frame = Frame(resources_content, bg="#f4e8e8")
    bc_frame.pack(fill="x", padx=35, pady=(15, 0))
    Label(bc_frame, text="Dashboard  >  Resources", font=("Inter", 9), fg="gray", bg="#f4e8e8").pack(anchor="w")

    Label(resources_content, text="Resources", font=("Plus Jakarta Sans", 24, "bold"), bg="#f4e8e8", fg="#1d2235").pack(anchor="w", padx=35, pady=(5, 0))
    Label(resources_content, text="Access all your learning materials and resources.", font=("Inter", 11), bg="#f4e8e8", fg="gray").pack(anchor="w", padx=35, pady=(0, 20))

    table_container = Frame(resources_content, bg="white", highlightbackground="#eaeaea", highlightthickness=1)
    table_container.pack(fill="both", expand=True, padx=35, pady=5)

    t_header = Frame(table_container, bg="#fbf8f8", height=40)
    t_header.pack(fill="x")
    t_header.pack_propagate(False)

    Label(t_header, text="Resource Name", font=("Inter", 10, "bold"), bg="#fbf8f8", fg="#4a4a4a").pack(side="left", padx=45)
    Label(t_header, text="Uploaded By", font=("Inter", 10, "bold"), bg="#fbf8f8", fg="#4a4a4a").pack(side="left", padx=200)
    Label(t_header, text="Actions", font=("Inter", 10, "bold"), bg="#fbf8f8", fg="#4a4a4a").pack(side="right", padx=45)

    archive_items = []
    for course in courses_data:
        if student_email in course.get("enrolled_students", []):
            files = course.get("course_files", [])
            if isinstance(files, list):
                for file_item in files:
                    archive_items.append((
                        file_item, 
                        course.get("course_instructor", "Unknown Professor")
                    ))

    if not archive_items:
        Label(table_container, text="No curriculum resource items are currently uploaded to the database.", 
              font=("Inter", 11, "italic"), fg="gray", bg="white").pack(pady=40)
        return

    for name, prof in archive_items:
        row = Frame(table_container, bg="white", height=45, highlightbackground="#f1f1f1", highlightthickness=1)
        row.pack(fill="x")
        row.pack_propagate(False)

        file_lbl = Label(row, text="📄", font=("Arial", 11), fg="#f7c948", bg="white")
        file_lbl.pack(side="left", padx=(15, 5))

        Label(row, text=name, font=("Inter", 10, "bold"), bg="white", fg="black").pack(side="left", padx=10)
        
        prof_lbl = Label(row, text=prof, font=("Inter", 10), bg="white", fg="#5a5a5a")
        prof_lbl.place(x=380, y=11)

        Button(row, text="↓", font=("Arial", 14, "bold"), fg="black", bg="white", relief="flat",
        command=lambda f=name: open_student_file(f)).pack(side="right", padx=60)

    footer = Frame(table_container, bg="white", height=50)
    footer.pack(fill="x", side="bottom")

    Label(footer, text=f"Showing 1-{len(archive_items)} of {len(archive_items)} resources", font=("Inter", 9), fg="gray", bg="white").pack(side="left", padx=15, pady=15)

# 7. Sidebar Component Generator Loops
menu_items = [
    ("🏠    Dashboard", dashboard_page),
    ("📖    My Courses", mycourses_page),
    ("🔍    Browse Courses", browse_page),
    ("📂    Resources", resources_page)
]

for text, page in menu_items:
    btn = Button(
        sidebar,
        text=text,
        command=lambda p=page: show_page(p),
        font=("Inter", 11, "bold"),
        fg="white",
        bg="#800000",
        activebackground="#f7c948",
        activeforeground="#1d2235",
        relief="flat",
        width=25,
        height=2,
        anchor="w",
        padx=20
    )
    btn.pack(anchor="w", pady=3, padx=15)

logout_btn = Button(
    sidebar,
    text="[→    Logout",
    font=("Inter", 11, "bold"),
    fg="white",
    bg="#800000",
    activebackground="#f7c948",
    activeforeground="black",
    relief="flat",
    width=25,
    height=2,
    anchor="w",
    padx=20,
    command=root.destroy
)
logout_btn.pack(anchor="w", side="bottom", pady=25, padx=15)

show_page(dashboard_page)
root.mainloop()