import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
from PIL import Image, ImageTk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(SCRIPT_DIR, "assets")

def asset(name):
    return os.path.join(ASSET_DIR, name)

# CORE CLASS & INHERITANCE
class MemberCard(tk.Frame):
    
    def __init__(self, parent, name, role, photo_path=None):
        super().__init__(parent, bg="#FDF1ED", bd=0, highlightthickness=0)
        
        self.name = name
        self.role = role
        self.photo_path = photo_path
        
        self.create_widgets()

    def create_widgets(self):
    
        # UNIVERSITY LOGO POSITION 
        self.logo_label = tk.Label(self, bg="#FDF1ED")
        self.logo_label.place(x=25, y=10)
        self.load_university_logo()

        # LEFT COLUMN: Photo Frame (FLUSH CODES)
        # Completely zeroed out default borders to eliminate canvas leakage
        self.canvas = tk.Canvas(self, width=170, height=240, bg="#FFFFFF", 
                               bd=2, highlightthickness=0, relief="solid", highlightbackground="#212529")
        self.canvas.place(x=25, y=65) 
        
        # Load and display the profile photo
        self.load_profile_image()

        # RIGHT COLUMN: Main Maroon Info Panel Card
        info_panel = tk.Frame(self, bg="#7A151A", bd=0, highlightthickness=0)
        info_panel.place(x=225, y=65, width=310, height=240)
        
        # Name Display Panel Group
        tk.Label(info_panel, text="NAME", font=("Inter Black", 10, "bold"), 
                 fg="#FFFFFF", bg="#7A151A", anchor="w").place(x=15, y=10, width=280)
        name_box = tk.Label(info_panel, text=self.name, font=("Inter Medium", 11, "bold"), 
                            fg="#7A151A", bg="#FFD000", bd=0, anchor="center")
        name_box.place(x=15, y=32, width=280, height=35)
        
        # Section Display Panel Group
        tk.Label(info_panel, text="SECTION", font=("Inter Black", 10, "bold"), 
                 fg="#FFFFFF", bg="#7A151A", anchor="w").place(x=15, y=82, width=280)
        section_box = tk.Label(info_panel, text="BSCPE 1-5", font=("Inter Medium", 11, "bold"), 
                               fg="#7A151A", bg="#FFD000", bd=0, anchor="center")
        section_box.place(x=15, y=104, width=280, height=35)
        
        # Assigned Task Display Panel Group
        tk.Label(info_panel, text="ASSIGNED TASK", font=("Inter Black", 10, "bold"), 
                 fg="#FFFFFF", bg="#7A151A", anchor="w").place(x=15, y=154, width=280)
        role_box = tk.Label(info_panel, text=self.role, font=("Inter Medium", 11, "bold"), 
                            fg="#7A151A", bg="#FFD000", bd=0, anchor="center")
        role_box.place(x=15, y=176, width=280, height=35)

    def load_university_logo(self):
        # Loads the official university badge icon
        try:
            logo_img = Image.open(asset("pup_logo.png"))
            logo_img = logo_img.resize((45, 45), Image.Resampling.LANCZOS)
            self.tk_logo = ImageTk.PhotoImage(logo_img)
            self.logo_label.config(image=self.tk_logo)
        except Exception:
            self.logo_label.config(text="(PUP LOGO)", fg="#7A151A", font=("Inter Bold", 10), bg="#FDF1ED")

    def load_profile_image(self):
        # photo 
        try:
            if self.photo_path:
                img = Image.open(asset(self.photo_path))
                
                # target height slightly to completely over-saturate and clip white gaps
                target_w = 170
                target_h = 241
                
                orig_w, orig_h = img.size
                
                # Force maximum coverage using scale factor evaluation
                scale_w = target_w / orig_w
                scale_h = target_h / orig_h
                scale = max(scale_w, scale_h) 
                
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Integer casting coordinates prevents fractional sub-pixel background rendering leaking
                left = int((new_w - target_w) / 2)
                top = int((new_h - target_h) / 2)
                right = left + target_w
                bottom = top + target_h
                img = img.crop((left, top, right, bottom))
                
                self.tk_img = ImageTk.PhotoImage(img)
                self.canvas.create_image(85, 120, image=self.tk_img)
            else:
                raise FileNotFoundError
        except Exception:
            self.canvas.delete("all")
            self.canvas.create_text(85, 120, text="[ Insert Photo ]", fill="#868E96", font=("Inter Medium", 10))


# MAIN APPLICATION MANAGEMENT
class PortfolioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LMS Group Portfolio")
        
        self.root.geometry("590x460")
        self.root.configure(bg="#FDF1ED")
        
        # FIXED: Enforced strict window locking layout parameters
        self.root.resizable(False, False)
        
        # group Team Dictionary List Setup
        self.members_data = {
            "AEROLD AFABLE": {"role": "DOCUMENTATION", "photo": "aerold.jpg"},
            "CHRISTIAN BERGOLA": {"role": "UI DESIGNER", "photo": "christian.jpg"}, 
            "EUNICE BLANCO": {"role": "LEADER, FRONTEND DEVELOPER", "photo": "eunice.jpg"},
            "ANGEL ZAINA CUASAY": {"role": "UI DESIGNER", "photo": "zaina.jpg"},
            "IRISH DE GUZMAN": {"role": " BACKEND DEVELOPER", "photo": "irish.jpg"},
            "LIRAH MOLLEDA": {"role": "DOCUMENTATION ", "photo": "lirah.jpg"},
            "JANA MIKAELA SAET": {"role": "FRONTEND DEVELOPER", "photo": "jana.jpg"},
            "ANNA SHARLENE TORIO": {"role": "DOCUMENTATION", "photo": "anna.jpg"},
            "YAEL TORREGOZA": {"role": "DOCUMENTATION", "photo": "yael.jpg"},
            "KIV ZEIMER CRUZ": {"role": "BACKEND DEVELOPER", "photo": "kiv.jpg"}
        }
        
        self.current_display = None
        self.create_window_menu()
        self.setup_layout_containers()

    def create_window_menu(self):
        # drop down menu
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="View Portfolios", command=lambda: messagebox.showinfo("LMS Notice", "Portfolio module active!"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit Component", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def setup_layout_containers(self):
        # Top Bar Graphic Sim Accent Element Panel
        top_bar = tk.Canvas(self.root, bg="#FFFFFF", height=40, bd=0, highlightthickness=0)
        top_bar.pack(fill="x", side="top")
        
        top_bar.create_oval(15, 14, 27, 26, fill="#FF7B54", outline="")
        top_bar.create_oval(34, 14, 46, 26, fill="#FFD000", outline="")
        top_bar.create_oval(53, 14, 65, 26, fill="#10B981", outline="")
        top_bar.create_text(295, 20, text="PROFILE", font=("Inter Black", 13, "bold"), fill="#212529")
        
        divider = tk.Frame(self.root, bg="#7A151A", height=2)
        divider.pack(fill="x")
        
        # Control Layout Nav Dropdown Component Row Strip
        nav_frame = tk.Frame(self.root, bg="#FDF1ED", pady=8)
        nav_frame.pack(fill="x")
        
        tk.Label(nav_frame, text="Select Member:", font=("Inter Bold", 9), fg="#212529", bg="#FDF1ED").pack(side="left", padx=(25, 5))
        
        sorted_names = sorted(list(self.members_data.keys()), key=lambda name: name.split()[-1])
        
        self.member_select = ttk.Combobox(nav_frame, values=sorted_names, state="readonly", font=("Inter", 9), width=22)
        self.member_select.pack(side="left", padx=5)
        
        try:
            eunice_index = sorted_names.index("Eunice Blanco")
            self.member_select.current(eunice_index)
        except ValueError:
            self.member_select.current(0)
        
        self.member_select.bind("<<ComboboxSelected>>", lambda event: self.update_view())
        
        # Outer Frame Container Border Bounds Display Area Panel
        self.display_area = tk.Frame(self.root, bg="#FDF1ED", bd=1.5, relief="solid")
        self.display_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.update_view()

    def update_view(self):
        if self.current_display is not None:
            self.current_display.pack_forget()
            self.current_display.destroy()
            
        selected_name = self.member_select.get()
        info = self.members_data[selected_name]
        
        self.current_display = MemberCard(
            parent=self.display_area, 
            name=selected_name, 
            role=info["role"], 
            photo_path=info["photo"]
        )
        self.current_display.pack(fill="both", expand=True)

def open_portfolio_window():
    root = tk.Toplevel()
    app = PortfolioApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioApp(root)
    root.mainloop()