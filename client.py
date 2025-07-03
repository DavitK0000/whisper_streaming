import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import requests
import json
import os
from datetime import datetime

class TranscriptionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcription")
        self.root.geometry("800x600")
        
        # API URL
        self.api_url = "http://localhost:8080"
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Status: Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # File frame
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File label
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT)
        
        # Text area for SRT content
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=20,
            font=("Courier New", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Select File button
        self.select_button = ttk.Button(
            button_frame,
            text="Select Audio File",
            command=self.select_file
        )
        self.select_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Transcribe button
        self.transcribe_button = ttk.Button(
            button_frame,
            text="Transcribe",
            command=self.transcribe_audio,
            state='disabled'
        )
        self.transcribe_button.pack(side=tk.LEFT, padx=5)
        
        # Save SRT button
        self.save_button = ttk.Button(
            button_frame,
            text="Save SRT",
            command=self.save_srt,
            state='disabled'
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_text
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
        self.save_button['state'] = 'disabled'
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.flac *.ogg *.m4a"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.file_label.configure(text=os.path.basename(file_path))
            self.transcribe_button['state'] = 'normal'
            self.audio_file_path = file_path
            self.update_status("File selected")
            
    def update_status(self, text, color="black"):
        self.status_label.configure(text=f"Status: {text}", foreground=color)
        
    def transcribe_audio(self):
        if not hasattr(self, 'audio_file_path'):
            self.update_status("Please select an audio file first", "red")
            return
            
        try:
            self.update_status("Transcribing...", "blue")
            self.transcribe_button['state'] = 'disabled'
            self.select_button['state'] = 'disabled'
            self.root.update()
            
            # Send file to API
            with open(self.audio_file_path, 'rb') as f:
                files = {'file': (os.path.basename(self.audio_file_path), f)}
                response = requests.post(f"{self.api_url}/transcribe/", files=files)
                
            if response.status_code == 200:
                result = response.json()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, result['srt_content'])
                
                status_msg = (
                    f"Transcription completed in {result['processing_time']:.2f}s "
                    f"(Language: {result['language']}, "
                    f"Probability: {result['language_probability']:.2f})"
                )
                self.update_status(status_msg, "green")
                self.save_button['state'] = 'normal'
            else:
                self.update_status(f"Error: {response.text}", "red")
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
            
        finally:
            self.transcribe_button['state'] = 'normal'
            self.select_button['state'] = 'normal'
            
    def save_srt(self):
        if not self.text_area.get(1.0, tk.END).strip():
            self.update_status("No content to save", "red")
            return
            
        # Get original filename without extension
        if hasattr(self, 'audio_file_path'):
            base_name = os.path.splitext(os.path.basename(self.audio_file_path))[0]
        else:
            base_name = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".srt",
            initialfile=f"{base_name}.srt",
            filetypes=[("SubRip Subtitle", "*.srt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_area.get(1.0, tk.END))
                self.update_status(f"Saved to {os.path.basename(file_path)}", "green")
            except Exception as e:
                self.update_status(f"Error saving file: {str(e)}", "red")

def main():
    root = tk.Tk()
    app = TranscriptionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 