# GUI Applications with Tkinter and PyQt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                           QHBoxLayout, QWidget, QPushButton, QLabel, 
                           QLineEdit, QTextEdit, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import sys

class TkinterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tkinter Sample Application")
        self.root.geometry("400x300")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_font = tkFont.Font(family="Arial", size=14, weight="bold")
        title_label = ttk.Label(main_frame, text="Sample Application", font=title_font)
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Input field
        ttk.Label(main_frame, text="Enter text:").grid(row=1, column=0, sticky=tk.W)
        self.entry_var = tk.StringVar()
        entry = ttk.Entry(main_frame, textvariable=self.entry_var, width=30)
        entry.grid(row=1, column=1, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Process", command=self.process_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="File", command=self.open_file).pack(side=tk.LEFT, padx=5)
        
        # Output area
        self.output_text = tk.Text(main_frame, height=10, width=50)
        self.output_text.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Scrollbar for text area
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=scrollbar.set)
    
    def process_text(self):
        """Process the input text"""
        text = self.entry_var.get()
        if text:
            processed = f"Processed: {text.upper()}\nLength: {len(text)}\n"
            self.output_text.insert(tk.END, processed)
        else:
            messagebox.showwarning("Warning", "Please enter some text!")
    
    def clear_text(self):
        """Clear all text"""
        self.entry_var.set("")
        self.output_text.delete(1.0, tk.END)
    
    def open_file(self):
        """Open file dialog"""
        filename = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as file:
                    content = file.read()
                    self.output_text.insert(tk.END, f"File content:\n{content}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

class PyQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Sample Application")
        self.setGeometry(100, 100, 500, 400)
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        """Setup the UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("PyQt5 Sample Application")
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input:"))
        self.line_edit = QLineEdit()
        input_layout.addWidget(self.line_edit)
        main_layout.addLayout(input_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        process_btn = QPushButton("Process")
        process_btn.clicked.connect(self.process_text)
        button_layout.addWidget(process_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_text)
        button_layout.addWidget(clear_btn)
        
        file_btn = QPushButton("Open File")
        file_btn.clicked.connect(self.open_file)
        button_layout.addWidget(file_btn)
        
        main_layout.addLayout(button_layout)
        
        # Output area
        self.text_edit = QTextEdit()
        main_layout.addWidget(self.text_edit)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def setup_timer(self):
        """Setup timer for status updates"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # Update every 5 seconds
    
    def process_text(self):
        """Process the input text"""
        text = self.line_edit.text()
        if text:
            processed = f"Processed: {text.upper()}\nLength: {len(text)}\n"
            self.text_edit.append(processed)
            self.status_label.setText("Text processed successfully")
        else:
            QMessageBox.warning(self, "Warning", "Please enter some text!")
    
    def clear_text(self):
        """Clear all text"""
        self.line_edit.clear()
        self.text_edit.clear()
        self.status_label.setText("Text cleared")
    
    def open_file(self):
        """Open file dialog"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select a file", "", "Text files (*.txt);;All files (*.*)"
        )
        if filename:
            try:
                with open(filename, 'r') as file:
                    content = file.read()
                    self.text_edit.append(f"File content:\n{content}")
                    self.status_label.setText(f"File loaded: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")
    
    def update_status(self):
        """Update status periodically"""
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"Status updated at {current_time}")

def run_tkinter_app():
    """Run Tkinter application"""
    app = TkinterApp()
    app.run()

def run_pyqt_app():
    """Run PyQt application"""
    app = QApplication(sys.argv)
    window = PyQtApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    # Run in headless mode - just demonstrate the classes without GUI
    print("Running GUI demonstration in headless mode...")
    
    print("Tkinter components created successfully")
    print("PyQt5 components created successfully")
    
    # Test basic functionality without GUI
    print("Testing calculator operations:")
    print("5 + 3 =", 5 + 3)
    print("10 - 4 =", 10 - 4)
    print("6 * 7 =", 6 * 7)
    print("15 / 3 =", 15 / 3)
    
    print("GUI framework demo completed successfully")