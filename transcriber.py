import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, Tk, ttk
from threading import Thread

"""
Availabe Whisper models:
    tiny.en
    tiny
    base.en
    base
    small.en
    small
    medium.en
    medium
    large-v1
    large-v2
    large-v3
    large-v3-turbo
"""

MODEL_CONFIG = {
    "name": "base",
    "language": "ro",
}


class WhisperTranscriber:
    def __init__(self, root: Tk, base_path: str):
        self.root = root
        self.root.title("Romanian Audio Transcriber")
        self.base_path = base_path

        self.file_path = ""
        self.temp_file = ""
        self.output_file = ""

        self.init_paths()
        self.create_widgets()
        self.verify_setup()

    def create_widgets(self):
        """Create GUI components with modern blue theme"""
        # Configure style
        style = ttk.Style()
        style.theme_use("clam")

        # Color palette
        primary_color = "#2A3F54"  # Dark blue
        secondary_color = "#3498db"  # Bright blue
        background_color = "#f0f4f7"  # Light gray-blue
        text_color = "#ffffff"  # White
        accent_color = "#2980b9"  # Darker blue

        self.root.minsize(500, 500)

        # Configure styles
        style.configure("TFrame", background=background_color)
        style.configure(
            "TLabel",
            background=background_color,
            foreground=primary_color,
            font=("Segoe UI", 10),
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            background=secondary_color,
            foreground=text_color,
            padding=8,
            width=0,
        )
        style.map(
            "TButton",
            background=[("active", accent_color), ("disabled", "#bdc3c7")],
            foreground=[("disabled", "#7f8c8d")],
        )

        style.configure("Header.TFrame", background=primary_color)
        style.configure(
            "Header.TLabel",
            background=primary_color,
            foreground=text_color,
            font=("Segoe UI", 14, "bold"),
        )

        style.configure(
            "Status.TLabel", font=("Segoe UI", 10, "italic"), foreground=accent_color
        )

        # Main container

        background = ttk.Frame(self.root)
        background.pack(fill=tk.BOTH, expand=True)

        main_frame = ttk.Frame(background)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=100, pady=20)

        # Header section
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(
            header_frame, text="Romanian Audio Transcriber", style="Header.TLabel"
        ).pack(pady=15, padx=20, anchor=tk.CENTER)

        # Content section
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # File selection section
        file_frame = ttk.Frame(content_frame)
        file_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            file_frame, text="1. Select Audio File:", font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.btn_select = ttk.Button(
            file_frame, text="Browse Audio File", command=self.select_file
        )
        self.btn_select.grid(row=1, column=0, sticky="ew", ipadx=20)

        self.lbl_selected_file = ttk.Label(
            file_frame, text="No file selected", foreground="#7f8c8d"
        )
        self.lbl_selected_file.grid(row=2, column=0, sticky=tk.W, pady=(5, 15))

        # Output section
        output_frame = ttk.Frame(content_frame)
        output_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            output_frame,
            text="2. Save Transcription As:",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.btn_choose_output = ttk.Button(
            output_frame, text="Choose Save Location", command=self.choose_output
        )
        self.btn_choose_output.grid(row=1, column=0, sticky="ew", ipadx=20)

        self.lbl_output_path = ttk.Label(
            output_frame, text="No location selected", foreground="#7f8c8d"
        )
        self.lbl_output_path.grid(row=2, column=0, sticky=tk.W, pady=(5, 15))

        # Progress section
        progress_frame = ttk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, pady=20)

        self.btn_transcribe = ttk.Button(
            progress_frame,
            text="Start Transcription",
            command=self.start_transcription,
            state=tk.DISABLED,
        )
        self.btn_transcribe.pack(pady=10, ipadx=30, fill=tk.X)

        self.lbl_status = ttk.Label(
            progress_frame, text="Status: Ready to begin", style="Status.TLabel"
        )
        self.lbl_status.pack()

        # Configure grid weights
        for frame in [file_frame, output_frame, progress_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)  # For button rows

        # Make main content frame responsive
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def init_paths(self):
        """Initialize the paths for the required files"""
        self.whisper_path = os.path.join(self.base_path, "whisper.cpp")
        self.ffmpeg_path = os.path.join(
            self.base_path, "vendor", "ffmpeg", "ffmpeg.exe"
        )
        self.model = MODEL_CONFIG["name"]

        self.model_path = os.path.join(
            self.whisper_path, "models", f"ggml-{self.model}.bin"
        )
        self.main_executable = os.path.join(
            self.whisper_path, "build", "bin", "Release", "whisper-cli.exe"
        )
        self.download_model_command_path = os.path.join(
            self.whisper_path, "models", "download-ggml-model.cmd"
        )

    def verify_setup(self):
        """Verify if the required files are present"""
        if not os.path.exists(self.model_path):
            self.update_status("Model not found")
            self.download_model()

        if not os.path.exists(self.main_executable):
            self.update_status("Whisper not found")
            self.build_whisper()

        if not os.path.exists(self.ffmpeg_path):
            self.update_status("FFmpeg not found")

    def download_model(self):
        """Download the required model"""
        if messagebox.askyesno(
            "Model not found", "Model not found. Do you want to download it?"
        ):
            self.update_status("Downloading model...")
            subprocess.run(
                f"cd {self.whisper_path} && {self.download_model_command_path} {self.model}",
                shell=True,
            )
            self.update_status("Model downloaded successfully")

    def build_whisper(self):
        """Build the whisper executable"""
        if messagebox.askyesno(
            "Whisper not found", "Whisper not found. Do you want to build it?"
        ):
            self.update_status("Building Whisper...")
            subprocess.run(
                f"cd {self.whisper_path} && cmake -B build && cmake --build build --config Release ",
                shell=True,
            )
            self.lbl_status.config(text="Whisper built successfully")

    def select_file(self):
        """Handle audio file selection"""
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.m4a")]
        )
        if self.file_path:
            self.lbl_selected_file.config(text=os.path.basename(self.file_path))
            self.output_file = os.path.splitext(self.file_path)[0] + ".txt"
            self.temp_file = self.file_path + ".wav"
            self.lbl_output_path.config(text=self.output_file)
            self.check_ready_state()

    def choose_output(self):
        """Handle output file selection"""
        initial_file = os.path.basename(self.file_path) if self.file_path else ""
        initial_file = os.path.splitext(initial_file)[0] + ".txt"

        self.output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile=initial_file,
        )

        if self.output_file:
            self.lbl_output_path.config(text=self.output_file)
            self.check_ready_state()

    def check_ready_state(self):
        """Enable transcribe button when ready"""
        if self.file_path and self.output_file:
            self.btn_transcribe.config(state=tk.NORMAL)
        else:
            self.btn_transcribe.config(state=tk.DISABLED)

    def start_transcription(self):
        """Start the transcription process in a separate thread"""
        self.btn_transcribe.config(state=tk.DISABLED)
        Thread(target=self.transcribe).start()

    def transcribe(self):
        """Main transcription workflow"""
        try:
            self.cleanup_temp_files()

            self.update_status("Converting audio to WAV...")
            self.convert_to_wav()

            self.update_status("Transcribing audio...")
            transcription = self.run_whisper()

            self.update_status("Saving results...")
            self.save_results(transcription)

            self.update_status("Transcription complete!")
            os.startfile(self.output_file)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error occurred")
        finally:
            self.cleanup_temp_files()
            self.root.after(0, lambda: self.btn_transcribe.config(state=tk.NORMAL))

    def convert_to_wav(self):
        """Convert input file to WAV format"""
        cmd = [
            self.ffmpeg_path,
            "-i",
            self.file_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            "-af",
            "highpass=f=150,lowpass=f=2800,afftdn=nf=-20",
            "-c:a",
            "pcm_s16le",
            "-y",
            self.temp_file,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def run_whisper(self) -> str:
        """Run whisper.cpp and return transcription"""
        cmd = [
            self.main_executable,
            "-m",
            self.model_path,
            "-f",
            self.temp_file,
            "-l",
            MODEL_CONFIG["language"],
            "--prompt",
            "Transcriere audio în limba română:",
            "-otxt",
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return open(self.temp_file + ".txt", "r", encoding="utf-8").read()

    def save_results(self, text: str):
        """Save transcription to output file"""
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(text)

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        if os.path.exists(self.temp_file + ".txt"):
            os.remove(self.temp_file + ".txt")

    def update_status(self, message: str):
        """Update the status label with the given message"""
        self.root.after(0, self.lbl_status.config, {"text": f"Status: {message}"})
