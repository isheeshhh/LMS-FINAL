# Import modules used for JSON file storage, file paths, and email validation.
import json
import os
import re

# Set the location of the JSON database file.
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")

# Regular expression pattern used to check if an email address is valid.
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def initialize_database():
    """Creates users.json if it does not exist or is invalid."""
    # Create a new database file when one is not found.
    if not os.path.exists(DATABASE_FILE):
        save_users({"users": []})
        return

    # Reset the database structure if the JSON file is broken or incomplete.
    try:
        data = load_users()
    except (json.JSONDecodeError, OSError):
        data = {"users": []}

    if "users" not in data or not isinstance(data["users"], list):
        save_users({"users": []})


def load_users():
    """Loads and returns all user records from users.json."""
    with open(DATABASE_FILE, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def save_users(data):
    """Saves updated user records to users.json."""
    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def is_valid_email(email):
    """Checks if the provided email follows a valid email format."""
    return bool(EMAIL_PATTERN.match(email.strip()))


def email_exists(email):
    """Checks if an email address is already registered."""
    data = load_users()
    email = email.strip().lower()

    for user in data["users"]:
        if user.get("email", "").strip().lower() == email:
            return True

    return False


def username_exists(username):
    """Checks if a username already exists. Kept for older user records."""
    data = load_users()
    username = username.strip().lower()

    for user in data["users"]:
        if user.get("username", "").strip().lower() == username:
            return True

    return False


def register_user(fullname, email, password, role):
    """Creates a new account using email as the login ID."""
    # Clean and normalize user input before saving it.
    fullname = fullname.strip()
    email = email.strip().lower()
    password = password.strip()
    role = role.strip().lower()

    # Validate required fields and role selection.
    if not fullname or not is_valid_email(email) or not password or role not in ("student", "professor"):
        return False

    # Prevent duplicate account registration with the same email.
    if email_exists(email):
        return False

    # Save the new user account to the JSON database.
    data = load_users()
    data["users"].append({
        "fullname": fullname,
        "email": email,
        "username": email,
        "password": password,
        "role": role
    })
    save_users(data)
    return True


def login_user(email, password, role=None):
    """Verifies login credentials and selected role."""
    data = load_users()
    email = email.strip().lower()
    password = password.strip()
    role = role.strip().lower() if role else None

    # Search for a matching account using email, password, and optional role.
    for user in data["users"]:
        user_email = user.get("email", user.get("username", "")).strip().lower()
        user_role = user.get("role", "").strip().lower()

        if user_email == email and user.get("password") == password:
            if role and user_role != role:
                return None
            return user

    return None


def get_user(email):
    """Returns a user record by email."""
    data = load_users()
    email = email.strip().lower()

    # Support both new email accounts and older username-only records.
    for user in data["users"]:
        user_email = user.get("email", user.get("username", "")).strip().lower()
        if user_email == email:
            return user

    return None


def update_password(email, new_password):
    """Updates a user's password after OTP verification."""
    email = email.strip().lower()
    new_password = new_password.strip()

    if not new_password:
        return False

    # Load saved users and create a cleaned list.
    data = load_users()
    updated = False
    cleaned_users = []

    # Find the matching account and keep only one updated version.
    for user in data["users"]:
        user_email = user.get("email", user.get("username", "")).strip().lower()

        if user_email == email:
            if not updated:
                user["password"] = new_password
                cleaned_users.append(user)
                updated = True
            # Ignore duplicate entries with old passwords.
        else:
            cleaned_users.append(user)

    # Save the updated list after removing old credentials.
    if updated:
        data["users"] = cleaned_users
        save_users(data)
        return True

    return False


# Make sure the database file exists when this module is imported.
initialize_database()
