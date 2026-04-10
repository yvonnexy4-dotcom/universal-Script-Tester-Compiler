import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import sys

class VisualCodingSoftware:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Script Tester & Compiler")
        self.root.geometry("11000x800")

        # UI Styling
        self.bg_color = "#1e1e1e"  # VS Code dark grey
        self.btn_color = "#333333"
        self.text_color = "#d4d4d4"
        self.accent_blue = "#007acc"
        
        self.root.configure(bg=self.bg_color)
        self.current_file_path = None
        self.setup_ui()

    def setup_ui(self):
        # --- Toolbar ---
        toolbar = tk.Frame(self.root, bg="#2d2d2d", pady=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Buttons
        btn_config = {"bg": self.btn_color, "fg": "white", "relief": tk.FLAT, "padx": 10}
        
        tk.Button(toolbar, text="📁 Open File", command=self.open_file, **btn_config).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📋 Paste Script", command=self.paste_code, bg=self.accent_blue, fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="▶ Run Script", command=self.run_script, bg="#28a745", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📦 Build EXE", command=self.convert_to_exe, **btn_config).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🗑 Clear", command=self.clear_all, **btn_config).pack(side=tk.RIGHT, padx=5)

        # --- Editor Window ---
        self.editor = scrolledtext.ScrolledText(
            self.root, 
            font=("Consolas", 12), 
            bg=self.bg_color, 
            fg=self.text_color, 
            insertbackground="white",
            undo=True
        )
        self.editor.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # --- Console Output ---
        self.output = scrolledtext.ScrolledText(
            self.root, 
            height=12, 
            font=("Consolas", 10), 
            bg="black", 
            fg="#80ff80"
        )
        self.output.pack(fill=tk.X, padx=10, pady=10)
        self.output.insert(tk.END, ">>> Console initialized. Ready for input.\n")

    def paste_code(self):
        """Fetches content from the system clipboard and inserts it at the cursor."""
        try:
            clipboard_content = self.root.clipboard_get()
            # If there is already text, ask to overwrite or append
            if self.editor.get(1.0, tk.END).strip():
                if messagebox.askyesno("Paste", "Overwrite existing code?"):
                    self.editor.delete(1.0, tk.END)
            
            self.editor.insert(tk.INSERT, clipboard_content)
            self.output.insert(tk.END, "[System]: Script pasted from clipboard.\n")
        except tk.TclError:
            messagebox.showerror("Error", "Clipboard is empty or contains non-text data.")

    def open_file(self):
        file_types = [
            ("All Scripts", "*.py *.js *.cs *.ts *.tsx *.ps1 *.bat *.cmd *.vbs"),
            ("Python", "*.py"),
            ("JavaScript", "*.js"),
            ("Batch/CMD", "*.bat *.cmd"),
            ("PowerShell", "*.ps1")
        ]
        path = filedialog.askopenfilename(filetypes=file_types)
        if path:
            self.current_file_path = path
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                self.editor.delete(1.0, tk.END)
                self.editor.insert(tk.END, f.read())
            self.output.insert(tk.END, f"[Loaded]: {path}\n")

    def clear_all(self):
        self.editor.delete(1.0, tk.END)
        self.output.delete(1.0, tk.END)
        self.current_file_path = None

    def run_script(self):
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            return

        # Determine extension (default to .py if pasted/new)
        ext = ".py"
        if self.current_file_path:
            ext = os.path.splitext(self.current_file_path)[1].lower()
        
        temp_file = f"temp_runtime{ext}"
        with open(temp_file, "w", encoding='utf-8') as f:
            f.write(code)

        self.output.insert(tk.END, f"\n--- Executing {ext} ---\n")
        
        try:
            cmd = []
            if ext == ".py": cmd = ["python", temp_file]
            elif ext == ".js": cmd = ["node", temp_file]
            elif ext in [".bat", ".cmd"]: cmd = [temp_file]
            elif ext == ".ps1": cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", temp_file]
            elif ext == ".vbs": cmd = ["cscript", "//Nologo", temp_file]
            
            if cmd:
                # shell=True is needed for Windows native scripts (bat/vbs)
                process = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if process.stdout: self.output.insert(tk.END, process.stdout)
                if process.stderr: self.output.insert(tk.END, f"STDERR: {process.stderr}", "error")
            else:
                self.output.insert(tk.END, "No execution rule for this file type.\n")
        except Exception as e:
            self.output.insert(tk.END, f"Error: {str(e)}\n")

    def convert_to_exe(self):
        """Converts Python script to EXE."""
        code = self.editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Editor is empty.")
            return

        # Save as a real file first if it's just pasted code
        if not self.current_file_path or not self.current_file_path.endswith(".py"):
            path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python", "*.py")])
            if not path: return
            self.current_file_path = path
            with open(path, 'w') as f: f.write(code)

        self.output.insert(tk.END, "\n[Build]: Installing dependencies and building EXE...\n")
        try:
            # Install PyInstaller if missing, then build
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole", self.current_file_path], shell=True)
            self.output.insert(tk.END, f"[Success]: EXE created in /dist folder.\n")
            os.startfile("dist") # Opens the folder automatically
        except Exception as e:
            self.output.insert(tk.END, f"[Build Error]: {str(e)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualCodingSoftware(root)
    root.mainloop()