"""
GUI Launcher for Antigravity Slide-to-Video Pipeline
Allows users to select input/output folders and run the pipeline
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import time
from datetime import datetime
import pipeline
import config

class PipelineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Antigravity Slide-to-Video Pipeline")
        self.root.geometry("700x900")
        self.root.configure(bg='#f0f0f0')
        
        self.pdf_folder = tk.StringVar(value=config.BASE_DIR)
        self.video_folder = tk.StringVar(value=config.BASE_DIR)
        self.slides_folder = tk.StringVar(value=os.path.join(config.BASE_DIR, "SLIDES"))
        self.output_folder = tk.StringVar(value=os.path.join(config.BASE_DIR, "OUTPUT"))
        self.reports_folder = tk.StringVar(value=os.path.join(config.BASE_DIR, "REPORTS"))
        self.is_running = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI elements"""
        # Title
        title = tk.Label(self.root, text="Antigravity Pipeline", font=("Arial", 18, "bold"), bg='#f0f0f0')
        title.pack(pady=10)
        
        # Input section
        input_frame = tk.LabelFrame(self.root, text="Input Folders", font=("Arial", 12, "bold"), 
                                    padx=10, pady=10, bg='#f0f0f0')
        input_frame.pack(padx=10, pady=10, fill="x")
        
        # PDF Folder
        tk.Label(input_frame, text="PDF Source Folder:", bg='#f0f0f0').grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(input_frame, textvariable=self.pdf_folder, width=50).grid(row=0, column=1, padx=5)
        tk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.pdf_folder)).grid(row=0, column=2)
        
        # Video Folder
        tk.Label(input_frame, text="Video Source Folder:", bg='#f0f0f0').grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(input_frame, textvariable=self.video_folder, width=50).grid(row=1, column=1, padx=5)
        tk.Button(input_frame, text="Browse", command=lambda: self.browse_folder(self.video_folder)).grid(row=1, column=2)
        
        # Output section
        output_frame = tk.LabelFrame(self.root, text="Output Folders", font=("Arial", 12, "bold"), 
                                     padx=10, pady=10, bg='#f0f0f0')
        output_frame.pack(padx=10, pady=10, fill="x")
        
        # Slides Folder
        tk.Label(output_frame, text="Slides Output Folder:", bg='#f0f0f0').grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(output_frame, textvariable=self.slides_folder, width=50).grid(row=0, column=1, padx=5)
        tk.Button(output_frame, text="Browse", command=lambda: self.browse_folder(self.slides_folder)).grid(row=0, column=2)
        
        # Output Folder
        tk.Label(output_frame, text="Cleaned Video Output Folder:", bg='#f0f0f0').grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(output_frame, textvariable=self.output_folder, width=50).grid(row=1, column=1, padx=5)
        tk.Button(output_frame, text="Browse", command=lambda: self.browse_folder(self.output_folder)).grid(row=1, column=2)
        
        # Reports Folder
        tk.Label(output_frame, text="Reports Output Folder:", bg='#f0f0f0').grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(output_frame, textvariable=self.reports_folder, width=50).grid(row=2, column=1, padx=5)
        tk.Button(output_frame, text="Browse", command=lambda: self.browse_folder(self.reports_folder)).grid(row=2, column=2)
        
        # Buttons section
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        self.run_button = tk.Button(button_frame, text="Start Processing", command=self.run_pipeline, 
                                   bg='#4CAF50', fg='white', font=("Arial", 12), padx=20, pady=10)
        self.run_button.pack(side="left", padx=5)
        
        self.cancel_button = tk.Button(button_frame, text="Cancel", command=self.cancel_pipeline, 
                                      bg='#f44336', fg='white', font=("Arial", 12), padx=20, pady=10, state="disabled")
        self.cancel_button.pack(side="left", padx=5)
        
        # Log section
        log_frame = tk.LabelFrame(self.root, text="Processing Log", font=("Arial", 12, "bold"), 
                                 padx=10, pady=10, bg='#f0f0f0')
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70, state="disabled")
        self.log_text.pack(fill="both", expand=True)
    
    def browse_folder(self, var):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.config(state="normal")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update()
    
    def run_pipeline(self):
        """Run the pipeline in a separate thread"""
        if not self.validate_folders():
            return
        
        self.is_running = True
        self.run_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        
        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.execute_pipeline)
        thread.start()
    
    def validate_folders(self):
        """Validate that source folders exist"""
        pdf_folder = self.pdf_folder.get()
        video_folder = self.video_folder.get()
        
        if not os.path.exists(pdf_folder):
            messagebox.showerror("Error", f"PDF folder does not exist:\n{pdf_folder}")
            return False
        
        if not os.path.exists(video_folder):
            messagebox.showerror("Error", f"Video folder does not exist:\n{video_folder}")
            return False
        
        # Create output folders if they don't exist
        for folder in [self.slides_folder.get(), self.output_folder.get(), self.reports_folder.get()]:
            os.makedirs(folder, exist_ok=True)
        
        return True
    
    def execute_pipeline(self):
        """Execute the pipeline"""
        try:
            self.log_message("Pipeline started...")
            self.log_message(f"PDF Source: {self.pdf_folder.get()}")
            self.log_message(f"Video Source: {self.video_folder.get()}")
            self.log_message(f"Slides Output: {self.slides_folder.get()}")
            self.log_message(f"Video Output: {self.output_folder.get()}")
            self.log_message(f"Reports Output: {self.reports_folder.get()}")
            self.log_message("=" * 80)
            
            # Create args object
            class Args:
                workspace = None
                pdf_dir = self.pdf_folder.get()
                video_dir = self.video_folder.get()
                slides_dir = self.slides_folder.get()
                output_dir = self.output_folder.get()
                reports_dir = self.reports_folder.get()
                force = False
                no_clean_temp = False
            
            # Redirect pipeline logs to GUI
            original_log = pipeline.log_to_file
            def gui_log_to_file(log_path, message):
                self.log_message(message)
                original_log(log_path, message)
            
            pipeline.log_to_file = gui_log_to_file
            
            # Run pipeline
            start_time = time.time()
            pipeline.main(Args())
            elapsed = time.time() - start_time
            
            self.log_message("=" * 80)
            self.log_message(f"Pipeline completed in {elapsed:.2f} seconds")
            messagebox.showinfo("Success", "Pipeline processing completed!\nCheck the reports folder for details.")
            
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Pipeline failed:\n{str(e)}")
        
        finally:
            self.is_running = False
            self.run_button.config(state="normal")
            self.cancel_button.config(state="disabled")
    
    def cancel_pipeline(self):
        """Cancel the pipeline"""
        if self.is_running:
            self.log_message("Cancellation requested...")
            self.is_running = False
            messagebox.showinfo("Cancelled", "Pipeline will stop at the next opportunity.")

def main():
    root = tk.Tk()
    gui = PipelineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
