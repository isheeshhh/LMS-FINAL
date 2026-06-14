# Import modules needed for file handling, OTP email sending, launching pages, and Tkinter UI.
import json
import os
import random
import smtplib
import ssl
import subprocess
import sys
import profile_page
from email.message import EmailMessage
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

# Store important project folder paths used by the application.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = SCRIPT_DIR
SESSION_FILE = os.path.join(SCRIPT_DIR, "current_user.json")
ASSET_DIR = os.path.join(SCRIPT_DIR, "assets")

# Add the project folder to the Python path so backend modules can be imported.
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Import backend functions for account registration, login, and password reset.
from database_for_users import get_user, is_valid_email, login_user, register_user, update_password
from email_config import SMTP_APP_PASSWORD, SMTP_EMAIL, SMTP_PORT, SMTP_SERVER

# Placeholder values are ignored when reading entry fields.
PLACEHOLDERS = {"Enter name", "Enter email", "Enter password", "Enter OTP", "New password", "Confirm password"}


# Returns the complete path of an image or icon inside the assets folder.
def asset(name):
    return os.path.join(ASSET_DIR, name)


# Gets text from an entry field and removes placeholder text.
def clean(entry):
    value = entry.get().strip()
    return "" if value in PLACEHOLDERS else value


# Saves the currently logged-in user for the homepage windows.
def save_session(user):
    with open(SESSION_FILE, "w", encoding="utf-8") as file:
        json.dump(user, file, indent=4)


# Opens the correct homepage based on the logged-in user role.
def open_homepage(user):
    save_session(user)
    target = "professor.py" if user.get("role", "").lower() == "professor" else "student.py"
    subprocess.Popen([sys.executable, os.path.join(SCRIPT_DIR, target)], cwd=SCRIPT_DIR)
    window.destroy()


# Sends the generated OTP code to the user email using SMTP.
def send_reset_otp(receiver_email, otp):
    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        raise ValueError("Please fill in SMTP_EMAIL and SMTP_APP_PASSWORD in email_config.py first.")

    message = EmailMessage()
    message["Subject"] = "EduLearn Password Reset OTP"
    message["From"] = SMTP_EMAIL
    message["To"] = receiver_email
    message.set_content(
        "Your EduLearn password reset OTP is: " + otp + "\n\n"
        "If you did not request this, you can ignore this email."
    )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(message)


# Create the main login and signup window.
window = Tk()
window.title("Learning Management System")
try:
    window.iconbitmap(asset("puplogo.ico"))
except TclError:
    pass
window.geometry("1200x800")
window.minsize(1000, 700)

# Divide the window into the left branding panel and right form panel.
left_frame = Frame(window, bg="maroon")
left_frame.pack(side="left", fill="both", expand=True)
right_frame = Frame(window, bg="#fdece6")
right_frame.pack(side="right", fill="both", expand=True)


# Loads and resizes an image asset for Tkinter.
def load(name, size):
    return ImageTk.PhotoImage(Image.open(asset(name)).resize(size))


# Creates a label at a fixed position inside a parent frame.
def txt(parent, text, x, y, **kw):
    Label(parent, text=text, bg=parent["bg"], **kw).place(x=x, y=y)


# Adds placeholder behavior to text and password entry fields.
def placeholder(entry, text, password=False):
    entry.insert(0, text)
    entry.config(fg="gray", show="")

    def focus_in(_):
        if entry.get() == text:
            entry.delete(0, END)
            entry.config(fg="black")
            if password:
                entry.config(show="*")

    def focus_out(_):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg="gray", show="")

    entry.bind("<FocusIn>", focus_in)
    entry.bind("<FocusOut>", focus_out)


# Creates a reusable labeled input box.
def entry_box(parent, y, label, ph, password=False):
    txt(parent, label, 20, y, font=("Inter", 12))
    frame = Frame(parent, bg="#FAF9F6", highlightbackground="#D3D3D3", highlightthickness=1)
    frame.place(x=30, y=y + 25, width=340, height=40)
    entry = Entry(frame, bg="#FAF9F6", bd=0)
    entry.place(x=10, y=7, width=320, height=25)
    placeholder(entry, ph, password=password)
    return entry


# Places an image label on the left branding panel.
def put_img(parent, img, x, y):
    lbl = Label(parent, image=img, bg="maroon", bd=0)
    lbl.image = img
    lbl.place(x=x, y=y)


try:
    pup = Image.open(asset("pupbg.ico")).convert("RGBA").resize((800, 800))
    pup.putalpha(pup.getchannel("A").point(lambda p: int(p * 0.20)))
    pup_logo = ImageTk.PhotoImage(pup)
    bg_logo = Label(left_frame, image=pup_logo, bg="maroon", bd=0)
    bg_logo.image = pup_logo
    bg_logo.place(relx=0.5, rely=0.5, anchor="center")
    bg_logo.lower()
except FileNotFoundError:
    pass

put_img(left_frame, load("hatlogo.ico", (45, 45)), 60, 60)
txt(left_frame, "EduLearn", 110, 55, font=("Plus Jakarta Sans", 18, "bold"), fg="white")
txt(left_frame, "Learning Management System", 110, 90, font=("Inter", 11), fg="#FFFFF0")
txt(left_frame, "Learn.\nGrow.", 60, 130, font=("Plus Jakarta Sans", 40, "bold"), fg="white")
canvas = Canvas(left_frame, bg="maroon", highlightthickness=0, width=400, height=120)
canvas.place(x=60, y=250)
canvas.create_text(0, 30, text="Succeed.", font=("Plus Jakarta Sans", 40, "bold"), fill="#f7c948", anchor="w")
canvas.create_line(0, 70, 25, 70, fill="#f7c948", width=3)
txt(left_frame, "Your all-in-one learning platform.\nAccess courses, track progress,\nand achieve your goals anytime.", 60, 340, font=("Inter", 14), fg="#FFFFF0")


# Displays one feature item on the left branding panel.
def feature(icon, title, desc, y):
    put_img(left_frame, load(icon, (45, 45)), 60, y)
    txt(left_frame, title, 110, y, font=("Plus Jakarta Sans", 14, "bold"), fg="#f8f8f8")
    txt(left_frame, desc, 110, y + 25, font=("Inter", 11), fg="#FFFFF0")


feature("access.ico", "ACCESS QUALITY COURSES", "Explore thousands of courses", 430)
feature("track.ico", "TRACK YOUR PROGRESS", "Monitor learning achievements", 500)
feature("engage.ico", "ENGAGE & COLLABORATE", "Connect with peers and instructors", 570)


btn_profiles = Button(
    left_frame, 
    text="GO TO PROFILES", 
    font=("Courier", 12, "bold"),   
    bg="#ffea00",                    
    fg="black",                      
    bd=5,                            
    relief="raised",                 
    highlightbackground="black",     
    highlightthickness=2,
    activebackground="#e5d200",      
    cursor="hand2",
    command=profile_page.open_portfolio_window                  
)
btn_profiles.place(x=60, y=660, width=200, height=45)


# Container where login, signup, and reset-password forms are displayed.
inner = Frame(right_frame, bg="white", width=400, height=600)
inner.place(relx=0.5, rely=0.5, anchor="center")
inner.pack_propagate(False)
Label(right_frame, text="(c) 2026 EduLearn LMS. All rights reserved.", font=("Inter", 10), fg="gray", bg="#fdece6").place(relx=0.5, rely=0.95, anchor="center")


# Clears the form container before showing another screen.
def clear_inner():
    for widget in inner.winfo_children():
        widget.destroy()


# Creates selectable Student and Professor role cards.
def role_selector(parent, y, role_var):
    txt(parent, "I am a", 20, y, font=("Inter", 12))
    boxes = {}

    def choose(role):
        role_var.set(role)
        for key, frame in boxes.items():
            active = key == role
            frame.config(bg="#fff7f7" if active else "white", highlightbackground="maroon" if active else "#D3D3D3", highlightthickness=2 if active else 1)
            for child in frame.winfo_children():
                child.config(bg="#fff7f7" if active else "white")

    def role_box(x, role, label, icon):
        frame = Frame(parent, bg="white", width=150, height=100, highlightbackground="#D3D3D3", highlightthickness=1)
        frame.place(x=x, y=y + 30)
        boxes[role] = frame
        img = load(icon, (40, 40))
        btn = Button(frame, image=img, text=label, compound="top", bg="white", bd=0, cursor="hand2", command=lambda: choose(role))
        btn.image = img
        btn.place(relx=0.5, rely=0.5, anchor="center")
        frame.bind("<Button-1>", lambda _event: choose(role))

    role_box(35, "student", "Student", "Student.ico")
    role_box(215, "professor", "Professor", "Professor.ico")
    choose(role_var.get())


# Shows the OTP verification screen and lets the user create a new password.
def reset_password_screen(email, otp):
    clear_inner()
    txt(inner, "Verify OTP", 20, 20, font=("Inter", 20), fg="black")
    txt(inner, "Enter the OTP sent to your email.", 20, 60, font=("Inter", 12), fg="#696969")

    otp_entry = entry_box(inner, 105, "OTP", "Enter OTP")
    new_password_entry = entry_box(inner, 180, "New Password", "New password", password=True)
    confirm_password_entry = entry_box(inner, 255, "Confirm Password", "Confirm password", password=True)

    def submit_new_password():
        entered_otp = clean(otp_entry)
        new_password = clean(new_password_entry)
        confirm_password = clean(confirm_password_entry)

        if entered_otp != otp:
            messagebox.showerror("Invalid OTP", "The OTP you entered is incorrect.")
            return
        if len(new_password) < 4:
            messagebox.showwarning("Weak Password", "Password must be at least 4 characters long.")
            return
        if new_password != confirm_password:
            messagebox.showwarning("Password Mismatch", "The new passwords do not match.")
            return
        if not update_password(email, new_password):
            messagebox.showerror("Reset Failed", "Unable to update the password for this account.")
            return

        messagebox.showinfo("Password Updated", "Your password has been reset. Please sign in.")
        login_screen()

    Button(inner, text="Reset Password", bg="maroon", fg="white", bd=0, font=("Inter", 14), width=30, command=submit_new_password).place(x=32, y=360)
    Button(inner, text="<- Back to Login", bg="white", fg="maroon", bd=0, cursor="hand2", command=login_screen).place(x=30, y=430)


# Shows the forgot-password screen and sends an OTP to the registered email.
def forgot_password_screen():
    clear_inner()
    txt(inner, "Forgot Password", 20, 20, font=("Inter", 20), fg="black")
    txt(inner, "Enter your account email to receive an OTP.", 20, 60, font=("Inter", 12), fg="#696969")
    email_entry = entry_box(inner, 115, "Email", "Enter email")

    def send_otp():
        email = clean(email_entry).lower()
        if not is_valid_email(email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
        if not get_user(email):
            messagebox.showerror("Not Found", "No account was found for that email.")
            return

        otp = str(random.randint(100000, 999999))
        try:
            send_reset_otp(email, otp)
        except Exception as error:
            messagebox.showerror("Email Error", str(error))
            return

        messagebox.showinfo("OTP Sent", "A reset OTP was sent to your email.")
        reset_password_screen(email, otp)

    Button(inner, text="Send OTP", bg="maroon", fg="white", bd=0, font=("Inter", 14), width=30, command=send_otp).place(x=32, y=205)
    Button(inner, text="<- Back to Login", bg="white", fg="maroon", bd=0, cursor="hand2", command=login_screen).place(x=30, y=275)


# Shows the email login screen.
def login_screen():
    clear_inner()
    role_var = StringVar(value="student")

    txt(inner, "Welcome Back Iskolar!", 20, 20, font=("Inter", 20), fg="black")
    txt(inner, "Sign in using your email", 20, 60, font=("Inter", 12), fg="#696969")

    email_entry = entry_box(inner, 100, "Email", "Enter email")

    txt(inner, "Password", 20, 190, font=("Inter", 12))
    Button(inner, text="Forgot Password?", bg="white", fg="maroon", bd=0, font=("Inter", 12, "underline"), cursor="hand2", command=forgot_password_screen).place(x=245, y=190)
    password_frame = Frame(inner, bg="#FAF9F6", highlightbackground="#D3D3D3", highlightthickness=1)
    password_frame.place(x=30, y=220, width=340, height=40)
    password_entry = Entry(password_frame, bg="#FAF9F6", bd=0)
    password_entry.place(x=10, y=7, width=320, height=25)
    placeholder(password_entry, "Enter password", password=True)

    role_selector(inner, 295, role_var)

    def submit_login():
        email = clean(email_entry).lower()
        password = clean(password_entry)
        if not email or not password:
            messagebox.showwarning("Missing Information", "Please enter your email and password.")
            return
        if not is_valid_email(email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
        user = login_user(email, password, role_var.get())
        if not user:
            messagebox.showerror("Login Failed", "Invalid email, password, or selected role.")
            return
        messagebox.showinfo("Login Successful", f"Welcome, {user.get('fullname', email)}!")
        open_homepage(user)

    Button(inner, text="Sign In ->", bg="maroon", fg="white", bd=0, font=("Inter", 14), width=30, command=submit_login).place(x=32, y=455)
    Label(inner, text="Don't have an account?", bg="white", fg="gray", font=("Inter", 12)).place(x=80, y=535)
    Button(inner, text="Sign Up", bg="white", fg="maroon", bd=0, font=("Inter", 12, "underline"), cursor="hand2", command=signup_screen).place(x=245, y=533)


# Shows the account registration screen.
def signup_screen():
    clear_inner()
    role_var = StringVar(value="student")
    txt(inner, "Create Account", 20, 18, font=("Inter", 20), fg="black")
    txt(inner, "Sign up to start your learning journey", 20, 55, font=("Inter", 12), fg="#696969")

    fullname_entry = entry_box(inner, 88, "Full Name", "Enter name")
    email_entry = entry_box(inner, 158, "Email", "Enter email")
    password_entry = entry_box(inner, 228, "Password", "Enter password", password=True)
    role_selector(inner, 300, role_var)

    def submit_signup():
        fullname = clean(fullname_entry)
        email = clean(email_entry).lower()
        password = clean(password_entry)
        if not fullname or not email or not password:
            messagebox.showwarning("Missing Information", "Please fill in all fields.")
            return
        if not is_valid_email(email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
        if len(password) < 4:
            messagebox.showwarning("Weak Password", "Password must be at least 4 characters long.")
            return
        if not register_user(fullname, email, password, role_var.get()):
            messagebox.showerror("Sign Up Failed", "Email already exists or the details are invalid.")
            return
        messagebox.showinfo("Account Created", "Your account has been created. Please sign in.")
        login_screen()

    Button(inner, text="Create Account ->", bg="maroon", fg="white", bd=0, font=("Inter", 14), width=30, command=submit_signup).place(x=32, y=465)
    Label(inner, text="Already have an account?", bg="white", fg="gray", font=("Inter", 12)).place(x=70, y=542)
    Button(inner, text="Sign In", bg="white", fg="maroon", bd=0, font=("Inter", 12, "underline"), cursor="hand2", command=login_screen).place(x=250, y=540)


login_screen()
window.mainloop()

