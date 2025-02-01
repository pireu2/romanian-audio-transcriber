import os
import re
import tkinter as tk
from multiprocessing import cpu_count
from tkinter import filedialog, messagebox, Tk, ttk
from threading import Thread
from faster_whisper import WhisperModel

MODEL_CONFIG = {
    "name": "base",
    "language": "ro",
    "path": "models",
}

MODELS = [
    "tiny",
    "base",
    "small",
    "medium",
    "large",
    "large-v2",
    "large-v3",
]


class WhisperTranscriber:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.file_path = ""
        self.output_file = ""
        self.model = None
        self.model_download_root = os.path.join(self.base_path, MODEL_CONFIG["path"])

    def load_model(self, callback=None):
        """Initialize the Whisper model"""

        local_files = False

        if os.path.exists(self.model_download_root):
            for file in os.listdir(self.model_download_root):
                if MODEL_CONFIG["name"] in file:
                    local_files = True
                    if callback:
                        callback("Local model files deceted. Loading model...")
                    break
            if callback:
                callback("Downloading model files...")

        num_threads = self.get_thread_count()

        self.model = WhisperModel(
            MODEL_CONFIG["name"],
            device="auto",
            cpu_threads=num_threads,
            compute_type="int8",
            download_root=self.model_download_root,
            local_files_only=local_files,
        )
        if callback:
            callback("Model loaded successfully")

    def run_whisper(self) -> str:
        """Run whisper.cpp and return transcription"""

        transcription_lines = []
        segments, info = self.model.transcribe(self.file_path, beam_size=8)

        print(
            "Detected language '%s' with probability %f"
            % (info.language, info.language_probability)
        )
        for segment in segments:
            text_line = segment.text.strip()
            transcription_lines.append(text_line)

            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        return "\n".join(transcription_lines)

    def save_results(self, text: str):
        """Save transcription to output file"""
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(self.post_process(text))

    def post_process(self, text: str) -> str:
        """
        Post-process the text to remove unnecessary newlines and ensure
        newlines only appear after . ! ?
        """
        # Step 1: Replace all newlines with spaces
        text = text.replace("\n", " ")

        # Step 2: Add newlines after . ! ?
        text = re.sub(r"([.!?])", r"\1\n", text)

        # Step 3: Remove extra spaces around newlines
        text = re.sub(r"\s*\n\s*", "\n", text)

        # Step 4: Remove leading/trailing whitespace
        text = text.strip()

        return text

    def get_thread_count(self) -> int:
        """
        Get the number of threads to use
        """
        return os.cpu_count() or cpu_count()


class TranscriberGUI:
    def __init__(self, root: Tk, transcriber: WhisperTranscriber):
        self.root = root
        self.transcriber = transcriber
        self.root.title("Romanian Audio Transcriber")
        self.create_widgets()
        self.start_model_loading_thread()

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

        style.configure(
            "Custom.TCombobox",
            fieldbackground=secondary_color,
            background=secondary_color,
            foreground=text_color,
            selectbackground=accent_color,
            selectforeground=text_color,
            borderwidth=1,
            bordercolor=accent_color,
            arrowsize=12,
            arrowcolor=text_color,
            padding=5,
            font=("Segoe UI", 11),
        )

        style.map(
            "Custom.TCombobox",
            fieldbackground=[("readonly", secondary_color)],
            background=[("readonly", secondary_color)],
            bordercolor=[("focus", accent_color), ("!focus", accent_color)],
            lightcolor=[("focus", accent_color), ("!focus", accent_color)],
            darkcolor=[("focus", accent_color), ("!focus", accent_color)],
        )

        # Configure the combobox popdown style
        style.configure(
            "Custom.TCombobox.Listbox",
            background=background_color,
            foreground=primary_color,
            selectbackground=accent_color,
            selectforeground=text_color,
            borderwidth=1,
            relief="flat",
            font=("Segoe UI", 11),
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

        # Model selection section
        model_frame = ttk.Frame(content_frame)
        model_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            model_frame, text="Change Model:", font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.model_var = tk.StringVar(value=MODEL_CONFIG["name"])
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=MODELS,
            state="readonly",
            style="Custom.TCombobox",
        )
        self.model_combobox.grid(row=1, column=0, sticky="ew", pady=5)
        self.model_combobox.bind("<<ComboboxSelected>>", self.on_model_selected)

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
        for frame in [model_frame, file_frame, output_frame, progress_frame]:
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)  # For button rows

        # Make main content frame responsive
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def on_model_selected(self, event):
        """Handle model selection event"""
        selected_model = self.model_var.get()
        MODEL_CONFIG["name"] = selected_model
        self.btn_transcribe.config(state=tk.DISABLED)
        self.start_model_loading_thread()

    def select_file(self):
        """Handle audio file selection"""
        self.transcriber.file_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.m4a")]
        )
        if self.transcriber.file_path:
            self.lbl_selected_file.config(
                text=os.path.basename(self.transcriber.file_path)
            )
            self.transcriber.output_file = (
                os.path.splitext(self.transcriber.file_path)[0] + ".txt"
            )
            self.lbl_output_path.config(text=self.transcriber.output_file)
            self.check_ready_state()

    def choose_output(self):
        """Handle output file selection"""
        initial_file = (
            os.path.basename(self.transcriber.file_path)
            if self.transcriber.file_path
            else ""
        )
        initial_file = os.path.splitext(initial_file)[0] + ".txt"

        self.transcriber.output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialfile=initial_file,
        )

        if self.transcriber.output_file:
            self.lbl_output_path.config(text=self.transcriber.output_file)
            self.check_ready_state()

    def check_ready_state(self):
        """Enable transcribe button when ready"""
        if self.transcriber.file_path and self.transcriber.output_file:
            self.btn_transcribe.config(state=tk.NORMAL)
        else:
            self.btn_transcribe.config(state=tk.DISABLED)

    def start_transcription(self):
        """Start the transcription process in a separate thread"""
        self.btn_transcribe.config(state=tk.DISABLED)
        Thread(target=self.transcribe).start()

    def start_model_loading_thread(self):
        """Start a thread to load (or download) the model and update status."""
        Thread(target=self.load_model_thread, daemon=True).start()

    def load_model_thread(self):
        self.transcriber.load_model(callback=lambda msg: self.update_status(msg))
        self.root.after(0, lambda: self.btn_transcribe.config(state=tk.NORMAL))

    def transcribe(self):
        """Main transcription workflow."""
        try:
            self.update_status("Transcribing audio...")
            transcription = self.transcriber.run_whisper()

            self.update_status("Saving results...")
            self.transcriber.save_results(transcription)

            self.update_status("Transcription complete!")
            os.startfile(self.transcriber.output_file)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_status("Error occurred")
        finally:
            self.root.after(0, lambda: self.btn_transcribe.config(state=tk.NORMAL))

    def update_status(self, message: str):
        """Update the status label with the given message"""
        self.root.after(0, self.lbl_status.config, {"text": f"Status: {message}"})
