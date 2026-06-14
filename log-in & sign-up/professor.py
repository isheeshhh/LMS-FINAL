import json
import os
import subprocess
import sys
from tkinter import *
from tkinter import filedialog, Toplevel, messagebox
import database_for_courses as db

# Keep SCRIPT_DIR only for local UI assets (like images/icons)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(SCRIPT_DIR, "assets")

def asset(name):
    return os.path.join(ASSET_DIR, name)

db.init_database()
db.init_directory()

# Hardcoded professor name and ID used in place of session data.
prof_name = "Instructor"
professor_id = "professor"

def load_logged_in_session():
    global prof_name, professor_id
    # Use db.BASE_DIR to ensure current_user.json is in the correct directory
    session_file_path = os.path.join(db.BASE_DIR, "current_user.json")
    
    if os.path.exists(session_file_path):
        try:
            with open(session_file_path, "r", encoding="utf-8") as file:
                user_data = json.load(file)
                
                prof_name = user_data.get("fullname", "Instructor")
                professor_id = user_data.get("email", "professor")
                
        except Exception as e:
            print(f"Error reading session file: {e}")
            prof_name = "Instructor"
            professor_id = "professor"
    else:  
        prof_name = "Instructor"
        professor_id = "professor"

load_logged_in_session()


# WINDOW
root = Tk()
root.title("Learning Management System Dashboard")
try:
    root.iconbitmap(asset("puplogo.ico"))
except TclError:
    pass
root.state("zoomed")
root.configure(bg="#fdece6")

# FUNCTIONS
def clear_content():
    # Clears the main content area before loading another page.
    for widget in content_frame.winfo_children():
        widget.destroy()

# SIDEBAR
sidebar = Frame(root, width=300, bg="maroon")
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

# LOGO
try:
    logo = PhotoImage(file=asset("edulearn.png")).subsample(6, 6)
except TclError:
    logo = None

logo_frame = Frame(sidebar, bg="maroon")
logo_frame.pack(anchor="w", pady=(20, 10), padx=20)

if logo:
    logo_label = Label(logo_frame, image=logo, bg="maroon")
    logo_label.image = logo
    logo_label.pack(side="left")

text_logo = Frame(logo_frame, bg="maroon")
text_logo.pack(side="left", padx=10)

Label(
    text_logo,
    text="EduLearn",
    font=("Plus Jakarta Sans", 18, "bold"),
    fg="#f7c948",
    bg="maroon"
).pack(anchor="w")

Label(
    text_logo,
    text="Learning Management System",
    font=("Inter", 9),
    fg="#FFFFF0",
    bg="maroon"
).pack(anchor="w")

# RIGHT SIDE
right_frame = Frame(root, bg="#fdece6")
right_frame.pack(fill="both", expand=True)

# HEADER
header = Frame(right_frame, bg="#fdece6")
header.pack(fill="x", padx=20, pady=20)

text_frame = Frame(header, bg="#fdece6")
text_frame.pack(side="left")

Label(
    text_frame,
    text="Welcome back,",
    font=("Inter", 14),
    fg="Gray",
    bg="#fdece6"
).pack(anchor="w")

Label(
    text_frame,
    text=prof_name,
    font=("Plus Jakarta Sans", 20, "bold"),
    fg="Black",
    bg="#fdece6"
).pack(anchor="w")

# PROFILE

name_parts = prof_name.strip().split()

if len(name_parts) >= 2:
    initials = (name_parts[0][0] + name_parts[1][0]).upper()
elif len(name_parts) == 1 and len(name_parts[0]) >= 2:
    initials = name_parts[0][:2].upper()
else:
    initials = prof_name[:2].upper() if prof_name else "IN"


profile = Frame(header, bg="white", highlightbackground="#D3D3D3", highlightthickness=1)
profile.pack(side="right", padx=10, pady=5)


Label(
    profile,
    text=initials,
    bg="#f7c948",
    fg="black",
    width=3,
    height=3,
    font=("Inter", 9, "bold")
).pack(side="left", padx=10, pady=10)

info = Frame(profile, bg="white")
info.pack(side="left", pady=8, padx=(0, 15))

Label(
    info,
    text=prof_name,
    bg="white",
    font=("Plus Jakarta Sans", 11, "bold")
).pack(anchor="w")

Label(
    info,
    text=professor_id,
    bg="white",
    fg="gray",
    font=("Inter", 9)
).pack(anchor="w")

# CONTENT FRAME
content_frame = Frame(right_frame, bg="#fdece6")
content_frame.pack(fill="both", expand=True)

# --- GLOBAL POPUP FUNCTIONS ---

def open_manage_courses(edit_idx=None):
    # Opens a popup form for adding or editing course information.
    popup = Toplevel(root)
    popup.title("Manage Course")
    popup.geometry("650x700")
    popup.configure(bg="white")

    # Grab focus so user cannot interact with main window behind it.
    popup.grab_set()

    is_edit = edit_idx is not None
    title_text = "Edit Course" if is_edit else "Add New Course"

    Label(
        popup,
        text=title_text,
        font=("Plus Jakarta Sans", 18, "bold"),
        bg="white"
    ).pack(pady=15)

    # COURSE NAME
    Label(popup, text="Course Name", bg="white", font=("Inter", 10)).pack(anchor="w", padx=20, pady=(20, 5))
    course_name = Entry(popup, font=("Inter", 11), bg="#FAF9F6", relief="flat")
    course_name.pack(fill="x", padx=20, ipady=8)

    # COURSE DESCRIPTION
    Label(popup, text="Course Description", bg="white", font=("Inter", 10)).pack(anchor="w", padx=20, pady=(15, 5))
    course_desc = Text(popup, height=8, font=("Inter", 11), bg="#FAF9F6", relief="flat")
    course_desc.pack(fill="both", expand=True, padx=20)

    courses_db = db.load_data()

    # Pre-fill fields if editing an existing course.
    if is_edit:
        c_data = courses_db[edit_idx]
        course_name.insert(0, c_data["course_name"])
        course_desc.insert("1.0", c_data["course_description"])

    def save_course():
        name = course_name.get().strip()
        desc = course_desc.get("1.0", END).strip()

        if not name:
            messagebox.showwarning("Validation Error", "Course Name is required.", parent=popup)
            return

        course_db = db.load_data()

        if is_edit:
            # Update existing course in the database.
            for i, c in enumerate(course_db):
                if i != edit_idx and c["course_name"] == name:
                    messagebox.showwarning("Error", f"Course {name} already exists.")
                    return
                
            course_db[edit_idx]["course_name"] = name
            course_db[edit_idx]["course_description"] = desc
        else:
            # Add a new course entry to the database.
            for c in course_db:
                if c["course_name"] == name:
                    messagebox.showwarning("Error", f"Course {name} already exists.")
                    return
            new_course = {
                "course_name": name,
                "course_description": desc,
                "course_instructor": prof_name,
                "course_files": [],
                "enrolled_students": []
            }
            course_db.append(new_course)
        db.save_data(db.COURSES_DATABASE, course_db)
        popup.destroy()
        show_courses() # Refresh view to show changes

    # BOTTOM BUTTONS
    button_frame = Frame(popup, bg="white")
    button_frame.pack(fill="x", padx=20, pady=20)

    Button(button_frame, text="Cancel", command=popup.destroy, bg="#FAF9F6", relief="flat", font=("Inter", 10)).pack(side="left", ipadx=20, ipady=10)
    Button(button_frame, text="SAVE COURSE", bg="maroon", fg="white", relief="flat", font=("Inter", 10, "bold"), command=save_course).pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=10)

def open_manage_files():
    popup = Toplevel(root)
    popup.title("Managing Files")
    popup.geometry("650x450")
    popup.configure(bg="white")
    popup.grab_set()

    Label(popup, text="Managing Files", font=("Plus Jakarta Sans", 18, "bold"), bg="white").pack(pady=20)

    all_courses = db.load_data()
    my_courses = [c for c in all_courses if c.get("course_instructor") == prof_name]

    if not my_courses:
        Label(popup, text="Create a course first before managing files.", font=("Inter", 11), fg="gray", bg="white").pack(pady=60)
        Button(popup, text="Close", relief="flat", bg="#FAF9F6", command=popup.destroy).pack(pady=20)
        return

    body = Frame(popup, bg="white")
    body.pack(fill="both", expand=True, padx=30)

    #Left side: Selection
    left_side = Frame(body, bg="white")
    left_side.pack(side="left", fill="both", expand=True, padx=(0, 10))

    Label(left_side, text="Select Course", font=("Inter", 10, "bold"), bg="white").pack(anchor="w", pady=(0,5))
    course_list = Listbox(left_side, height=12, font=("Inter", 11), bg="#FAF9F6", relief="flat", exportselection=False)
    course_list.pack(fill="both", expand=True)

    #Middle: All files
    mid_side = Frame(body, bg="white")
    mid_side.pack(side="left", fill="both", expand=True, padx=10)
    
    Label(mid_side, text="Attached Files", font=("Inter", 10, "bold"), bg="white").pack(anchor="w", pady=(0,5))
    file_listbox = Listbox(mid_side, height=12, font=("Inter", 11), bg="#FAF9F6", relief="flat", exportselection=False)
    file_listbox.pack(fill="both", expand=True)

    detail = Frame(body, bg="white", width=260)
    detail.pack(side="right", fill="y")
    detail.pack_propagate(False)

    selected_title = Label(detail, text="", font=("Plus Jakarta Sans", 12, "bold"), bg="white", wraplength=240, justify="left")
    selected_title.pack(anchor="w", pady=(5, 10))
    

    def refresh_list():
        course_list.delete(0, END)
        course_db = db.load_data()
        instructor_courses = [c for c in course_db if c.get("course_instructor") == prof_name]

        for course in instructor_courses:
            files = course.get("course_files", [])
            count = len(files)
            file_suffix = "file" if count == 1 else "files"
            course_list.insert(END, f"{course.get('course_name')} ({count} {file_suffix})")
        

    def get_selected_index():
        selected = course_list.curselection()
        if not selected:
            messagebox.showwarning("No Course Selected", "Please select a course first.", parent=popup)
            return None
        
        local_idx = selected[0]
        course_db = db.load_data()
        instructor_courses = [c for c in course_db if c.get("course_instructor") == prof_name]
        selected_course = instructor_courses[local_idx]

        for global_idx, course in enumerate(course_db):
            if course["course_name"] == selected_course["course_name"]:
                return global_idx
        return None
        

    def update_file_display(_event=None):
        file_listbox.delete(0, END)
        selected = course_list.curselection()

        if not selected:
            return
        
        course_db = db.load_data()
        instructor_courses = [c for c in course_db if c.get("course_instructor") == prof_name]
        course = instructor_courses[selected[0]]

        selected_title.config(text=course.get("course_name"))

        files = course.get("course_files", [])
        for f in  files:
            file_listbox.insert(END, f)

    def upload_file():
        index = get_selected_index()
        if index is None:
            return
        path = filedialog.askopenfilename(
            title="Select Course File",
            filetypes=[("All files", "*.*")]
        )
        if not path:
            return
        
        course_db = db.load_data()
        target_course = course_db[index]["course_name"]
        file_name = os.path.basename(path)

        #Check if the file is already in the database
        if file_name in course_db[index].get("course_files",[]):
            messagebox.showwarning("Duplicate File", f"'{file_name} ' is already attached to this course.", parent=popup)

        # Update the database course entry with the new file path.

        try:
            db.add_file_to_course(target_course, path)

            selected_pos = course_list.curselection()[0]
            refresh_list()
            course_list.selection_set(selected_pos)
            update_file_display()
            show_courses()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=popup)

    def remove_file():
        index = get_selected_index()
        if index is None:
            return

        file_selected = file_listbox.curselection()
        if not file_selected:
            messagebox.showwarning("No File Selected", "Please select a file from the attached files list to remove.", parent=popup)
            return

        # Clear the file path from the database course entry.
        course_db = db.load_data()
        target_course = course_db[index]
        files = target_course.get("course_files", [])
        file_to_remove = files[file_selected[0]]

        if messagebox.askyesno("Confirm Removal", f"Are you sure to remove file '{file_to_remove}'?", parent=popup):

            try:
                db.delete_file_in_course(target_course["course_name"], file_to_remove)
                selected_pos = course_list.curselection()[0]
                refresh_list()
                course_list.selection_set(selected_pos)
                update_file_display()
                show_courses()
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=popup)

    def open_file():
        index = get_selected_index()
        if index is None:
            return
        
        file_selected = file_listbox.curselection()
        if not file_selected:
            messagebox.showwarning("No file selected", "Please select a file to open.", parent=popup)
            return

        course_db = db.load_data()
        files = course_db[index].get("course_files", [])
        target_file = files[file_selected[0]]
        
        path = os.path.join(db.FILE_DIR, target_file)
        if not os.path.exists(path):
            messagebox.showwarning("File not found", "The file could not be found")
            return
        
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    Button(detail, text="Upload File", bg="maroon", fg="white", relief="flat", font=("Inter", 10, "bold"), command=upload_file).pack(fill="x", pady=6, ipady=8)
    Button(detail, text="Open File", bg="#FAF9F6", relief="flat", font=("Inter", 10), command=open_file).pack(fill="x", pady=6, ipady=8)
    Button(detail, text="Remove File", bg="#FAF9F6", fg="red", relief="flat", font=("Inter", 10), command=remove_file).pack(fill="x", pady=6, ipady=8)
    Button(popup, text="Close", relief="flat", bg="#FAF9F6", command=popup.destroy).pack(pady=20)

    course_list.bind("<<ListboxSelect>>", update_file_display)

    refresh_list()
    if my_courses:
        course_list.selection_set(0)
        update_file_display()


# --- DASHBOARD PAGE ---
def show_dashboard():
    clear_content()

    cards_frame = Frame(content_frame, bg="#fdece6")
    cards_frame.pack(fill="x", pady=(20, 20), padx=20)

    # DASHBOARD CARD
    def dashboard_card(parent, icon, title, value, bg_color):
        card = Frame(parent, bg=bg_color, width=1200, height=180, highlightbackground="#D3D3D3", highlightthickness=1)
        card.pack(side="left", padx=10)
        card.pack_propagate(False)

        Label(card, text=icon, font=("Inter", 22), bg=bg_color).pack(anchor="w", padx=20, pady=(20, 10))
        Label(card, text=title, font=("Inter", 12), fg="#696969", bg=bg_color).pack(anchor="w", padx=20)
        Label(card, text=value, font=("Plus Jakarta Sans", 28, "bold"), fg="black", bg=bg_color).pack(anchor="w", padx=20, pady=(10, 0))

    courses_db = db.load_data()
    my_courses_count = sum(1 for c in courses_db if c.get("course_instructor") == prof_name)
    dashboard_card(cards_frame, "📚", "Total Courses", str(my_courses_count), "white")

    # QUICK ACTIONS TITLE
    Label(
        content_frame,
        text="Quick Actions",
        font=("Plus Jakarta Sans", 16, "bold"),
        bg="#fdece6",
        fg="black"
    ).pack(anchor="w", padx=40, pady=(10, 10))

    quick_frame = Frame(content_frame, bg="#fdece6")
    quick_frame.pack(fill="x", padx=20)
    quick_frame.grid_columnconfigure(0, weight=1)
    quick_frame.grid_columnconfigure(1, weight=1)

    # Creates a clickable quick-action card on the dashboard.
    def quick_card(parent, col, icon, title, desc, command=None):
        card = Frame(parent, bg="white", height=120, highlightbackground="#D3D3D3", highlightthickness=1, cursor="hand2")
        card.grid(row=0, column=col, sticky="nsew", padx=10, pady=5)

        def on_click(event):
            if command:
                command()

        card.bind("<Button-1>", on_click)
        # Bind children too so clicks register everywhere on the card.
        for child in card.winfo_children():
            child.bind("<Button-1>", on_click)

        Label(card, text=icon, font=("Inter", 18), bg="white").pack(anchor="w", padx=15, pady=(15, 5))
        Label(card, text=title, font=("Plus Jakarta Sans", 12, "bold"), bg="white").pack(anchor="w", padx=15)
        Label(card, text=desc, font=("Inter", 9), fg="#696969", bg="white").pack(anchor="w", padx=15, pady=(2, 10))

    quick_card(quick_frame, 0, "📖", "Manage Courses", "Add a new course", command=lambda: open_manage_courses())
    quick_card(quick_frame, 1, "📁", "Managing Files", "Upload and edit course files", command=open_manage_files)

    # BOTTOM PANEL
    bottom_panel = Frame(content_frame, bg="white", height=200, highlightbackground="#D3D3D3", highlightthickness=1)
    bottom_panel.pack(fill="both", expand=True, padx=30, pady=30)
    Label(bottom_panel, text="Select a section from the sidebar to get started", font=("Inter", 12), fg="gray", bg="white").pack(expand=True)


# --- COURSE MANAGEMENT PAGE ---

def create_course_card(parent, idx, title, description, instructor, files):
    # Creates a course card shown on the Course Management page.
    card = Frame(parent, bg="white", height=140, highlightbackground="#D3D3D3", highlightthickness=1)
    card.pack(fill="x", pady=10)
    card.pack_propagate(False)

    # TOP
    top = Frame(card, bg="white")
    top.pack(fill="x", padx=25, pady=(20, 0))

    Label(top, text=title, font=("Plus Jakarta Sans", 18, "bold"), bg="white", fg="black").pack(side="left")

    actions = Frame(top, bg="white")
    actions.pack(side="right")

    def edit_course():
        open_manage_courses(edit_idx=idx)

    def delete_course():
        if messagebox.askyesno("Delete Course", f"Are you sure you want to delete '{title}'?"):
            course_db = db.load_data()
            target_course = course_db[idx]
            for f in target_course.get("course_files", []):
                db.delete_file_in_storage(f)

            course_db.pop(idx)
            db.save_data(db.COURSES_DATABASE, course_db)
            show_courses() # Refresh view

    Button(actions, text="✎", font=("Inter", 12), bg="#FAF9F6", fg="maroon", relief="flat", width=3, cursor="hand2", command=edit_course).pack(side="left", padx=5)
    Button(actions, text="🗑️", font=("Inter", 12), bg="#FAF9F6", fg="red", relief="flat", width=3, cursor="hand2", command=delete_course).pack(side="left")

    # DESCRIPTION
    Label(card, text=description, font=("Inter", 11), fg="gray", bg="white").pack(anchor="w", padx=25, pady=(10, 0))

    # DETAILS
    details = Frame(card, bg="white")
    details.pack(anchor="w", padx=25, pady=(18, 0))

    file_label = files[0] if files else "No file attached"
    Label(details, text=f"📄 {file_label}", font=("Inter", 11), fg="gray", bg="white").pack(side="left", padx=(0, 20))
    Label(details, text=f"👤 Instructor: {instructor}", font=("Inter", 11, "italic"), fg="maroon", bg="white").pack(side="left")
    
def show_courses():
    clear_content()

    main_content = Frame(content_frame, bg="#fdece6")
    main_content.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    page_header = Frame(main_content, bg="#fdece6")
    page_header.pack(fill="x", pady=(20, 20))

    title_frame = Frame(page_header, bg="#fdece6")
    title_frame.pack(side="left")

    Label(title_frame, text="Course Management", font=("Plus Jakarta Sans", 24, "bold"), bg="#fdece6", fg="black").pack(anchor="w")
    Label(title_frame, text="Create, edit, and manage your courses", font=("Inter", 11), fg="gray", bg="#fdece6").pack(anchor="w", pady=(5, 0))

    # Right align an "Add Course" button at the top of the course list.
    Button(page_header, text="➕ Add Course", bg="maroon", fg="white", font=("Inter", 10, "bold"), relief="flat", padx=15, pady=8, cursor="hand2", command=lambda: open_manage_courses()).pack(side="right")

    courses_db = db.load_data()
    my_courses = [(idx, c) for idx, c in enumerate(courses_db) if c.get("course_instructor") == prof_name]

    # Render courses dynamically.
    if not my_courses:
        Label(main_content, text="No courses available. Click 'Add Course' to create one.", font=("Inter", 12), fg="gray", bg="#fdece6").pack(pady=50)
    else:
        for idx, course in my_courses:
            create_course_card(
                parent=main_content,
                idx=idx,
                title=course.get("course_name", "Untitled Course"),
                description=course.get("course_description", ""),
                instructor=course.get("course_instructor", "Unknown"),
                files=course.get("course_files", [])
            )

# SIDEBAR BUTTONS
menu_items = [
    ("🏠    Dashboard", show_dashboard),
    ("📖    My Courses", show_courses),
]

for text, cmd in menu_items:
    Button(
        sidebar,
        text=text,
        font=("Inter", 14),
        fg="white",
        bg="maroon",
        activebackground="#f7c948",
        relief="flat",
        width=60,
        height=2,
        anchor="w",
        padx=30,
        cursor="hand2",
        command=cmd
    ).pack(anchor="w", pady=5, padx=20)

# Confirms and closes the professor dashboard when logging out.
def logout():
    confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
    if confirm:
        session_file_path = os.path.join(db.BASE_DIR, "current_user.json")
        try:
            with open(session_file_path, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)
        except Exception as e:
            print(f"Error clearing session file: {e}")
        root.destroy()

Button(
    sidebar,
    text="→    Logout",
    font=("Inter", 14),
    fg="white",
    bg="maroon",
    activebackground="#f7c948",
    relief="flat",
    width=60,
    height=2,
    anchor="w",
    padx=30,
    cursor="hand2",
    command=logout
).pack(anchor="w", pady=(10, 0), padx=20)

# START PAGE
show_dashboard()

root.mainloop()