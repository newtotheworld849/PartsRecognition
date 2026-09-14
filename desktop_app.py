import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sqlite3
import os
import shutil

# -----------------------------------------------------------------------------
# DATABASE SETUP
# -----------------------------------------------------------------------------
DB_FILE = "archive.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS drawings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                drawing_type TEXT,
                medium TEXT,
                style_era TEXT,
                elements TEXT,
                description TEXT
            )
        ''')
        conn.commit()

def save_to_db(filename, drawing_type, medium, style_era, elements, description):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO drawings (filename, drawing_type, medium, style_era, elements, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, drawing_type, medium, style_era, elements, description))
        conn.commit()

def fetch_drawings():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM drawings ORDER BY id DESC")
        rows = c.fetchall()
    return rows

init_db()

# -----------------------------------------------------------------------------
# CORE APP LOGIC
# -----------------------------------------------------------------------------
class PartsRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📐 PartsRecognition - Desktop Archive Explorer")
        self.root.geometry("900x550")
        self.root.configure(bg="#ffffff")
        
        self.selected_file_path = None
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # Window Title Accent
        title = tk.Label(self.root, text="📐 PartsRecognition", font=("Helvetica Neue", 18, "bold"), bg="#ffffff", fg="#111111")
        title.pack(anchor="w", padx=20, pady=(15, 2))
        
        caption = tk.Label(self.root, text="Digital Infrastructure Prototype // Automated System Ledger", font=("Helvetica Neue", 10), bg="#ffffff", fg="#666666")
        caption.pack(anchor="w", padx=20, pady=(0, 15))

        # Main Layout: Left Column (Upload) & Right Column (Database View)
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        left_col = tk.Frame(main_frame, bg="#ffffff", width=250)
        left_col.pack(side="left", fill="y", padx=(0, 20))
        left_col.pack_propagate(False)
        
        right_col = tk.Frame(main_frame, bg="#ffffff")
        right_col.pack(side="right", fill="both", expand=True)

        # --- LEFT COLUMN COMPONENTS ---
        tk.Label(left_col, text="1. Ingest Asset", font=("Helvetica Neue", 12, "bold"), bg="#ffffff", fg="#111111").pack(anchor="w", pady=5)
        
        self.btn_select = tk.Button(left_col, text="Select Drawing (JPG/PNG)", command=self.select_file, bg="#111111", fg="white", activebackground="#333333", activeforeground="white", relief="flat", font=("Helvetica Neue", 10))
        self.btn_select.pack(fill="x", pady=5)
        
        self.lbl_file = tk.Label(left_col, text="No file selected", font=("Helvetica Neue", 9, "italic"), bg="#ffffff", fg="#888888", wraplength=220, justify="left")
        self.lbl_file.pack(anchor="w", pady=5)
        
        self.btn_run = tk.Button(left_col, text="Run AI Digitisation & Save", command=self.process_asset, bg="#111111", fg="white", activebackground="#333333", activeforeground="white", relief="flat", font=("Helvetica Neue", 10, "bold"), state="disabled")
        self.btn_run.pack(fill="x", pady=(20, 5))

        # --- RIGHT COLUMN COMPONENTS ---
        tk.Label(right_col, text="2. Central Digital Archive Explorer", font=("Helvetica Neue", 12, "bold"), bg="#ffffff", fg="#111111").pack(anchor="w", pady=5)
        
        # Database Table Data Frame View
        table_frame = tk.Frame(right_col)
        table_frame.pack(fill="both", expand=True, pady=5)
        
        columns = ("id", "filename", "type", "medium", "era")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("filename", text="Filename")
        self.tree.heading("type", text="Type")
        self.tree.heading("medium", text="Medium")
        self.tree.heading("era", text="Era/Style")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("filename", width=150)
        self.tree.column("type", width=120)
        self.tree.column("medium", width=120)
        self.tree.column("era", width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    # --- ACTION HANDLERS ---
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            self.lbl_file.config(text=f"Staged: {filename}", fg="#111111", font=("Helvetica Neue", 9, "normal"))
            self.btn_run.config(state="normal")

    def process_asset(self):
        if not self.selected_file_path:
            return
        
        filename = os.path.basename(self.selected_file_path)
        
        # Simulated AI metadata parsing values
        drawing_type = "Assembly Drawing"
        medium = "Digital CAD Export"
        style_era = "Modern Compact Grid System"
        elements = "Transformer, Circuit Breaker, Busbar, Isolator"
        description = f"A desktop-processed architectural layout asset logging structural components for {filename}."

        # Simulate digital vaults file archiving
        os.makedirs("archive_vault", exist_ok=True)
        dest_path = os.path.join("archive_vault", filename)
        try:
            shutil.copy(self.selected_file_path, dest_path)
            save_to_db(filename, drawing_type, medium, style_era, elements, description)
            
            messagebox.showinfo("Success", "Asset parsed by Mock AI and written to SQLite Archive Ledger!")
            
            # Reset view states
            self.selected_file_path = None
            self.lbl_file.config(text="No file selected", fg="#888888", font=("Helvetica Neue", 9, "italic"))
            self.btn_run.config(state="disabled")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Could not archive asset: {e}")

    def refresh_table(self):
        # Clear existing data rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Pull rows out from DB ledger
        for r in fetch_drawings():
            self.tree.insert("", "end", values=(r["id"], r["filename"], r["drawing_type"], r["medium"], r["style_era"]))

# -----------------------------------------------------------------------------
# APPLICATION ENTRY
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PartsRecognitionApp(root)
    root.mainloop()
