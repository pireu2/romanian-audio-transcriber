import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, Tk, ttk
from threading import Thread


class WhisperTranscriber:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Romanian Audio Transcriber")

        self.file_path = ""
        self.temp_file = ""
        self.output_file = ""

        self.init_paths()
        self.create_widgets()
        self.verify_setup()


    def create_widgets(self):
        """Create GUI components"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File selection section
        ttk.Label(main_frame, text="Select Audio File:").grid(row=0, column=0, sticky=tk.W)
        self.btn_select = ttk.Button(main_frame, text="Browse...", command=self.select_file)
        self.btn_select.grid(row=0, column=1, padx=5)

        self.lbl_selected_file = ttk.Label(main_frame, text="No file selected")
        self.lbl_selected_file.grid(row=1, column=0, columnspan=2, sticky=tk.W)

        # Output selection section
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=(10,0))
        self.btn_choose_output = ttk.Button(main_frame, text="Choose Location...", command=self.choose_output)
        self.btn_choose_output.grid(row=2, column=1, padx=5, pady=(10,0))

        self.lbl_output_path = ttk.Label(main_frame, text="No output path selected")
        self.lbl_output_path.grid(row=3, column=0, columnspan=2, sticky=tk.W)

        # Status and actions
        self.btn_transcribe = ttk.Button(main_frame, text="Transcribe", command=self.start_transcription, state=tk.DISABLED)
        self.btn_transcribe.grid(row=4, column=0, columnspan=2, pady=10)

        self.lbl_status = ttk.Label(main_frame, text="Status: Ready")
        self.lbl_status.grid(row=5, column=0, columnspan=2, sticky=tk.W)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)

    def init_paths(self):
        """ Initialize the paths for the required files """
        self.whisper_path = os.path.join(os.path.dirname(__file__), "whisper.cpp")
        self.ffmpeg_path = os.path.join(os.path.dirname(__file__), "vendor", "ffmpeg","ffmpeg.exe")
        self.model = "base"

        self.model_path = os.path.join(self.whisper_path, "models", f"ggml-{self.model}.bin")
        self.main_executable = os.path.join(self.whisper_path, "build", "bin", "Release", "whisper-cli.exe")
        self.download_model_command_path = os.path.join(self.whisper_path, "models", "download-ggml-model.cmd")

    def verify_setup(self):
        """ Verify if the required files are present """
        if not os.path.exists(self.model_path):
            self.lbl_status.config(text="Model not found")
            self.download_model()

        if not os.path.exists(self.main_executable):
            self.lbl_status.config(text="Whisper not found")
            self.build_whisper()

        if not os.path.exists(self.ffmpeg_path):
            self.lbl_status.config(text="FFmpeg not found")

    def download_model(self):
        """ Download the required model """
        if messagebox.askyesno(
            "Model not found", "Model not found. Do you want to download it?"
        ):
            self.lbl_status.config(text="Downloading model...")
            subprocess.run(
                f"cd {self.whisper_path} && {self.download_model_command_path} {self.model}",
                shell=True,
            )

    def build_whisper(self):
        """ Build the whisper executable """
        if messagebox.askyesno(
            "Whisper not found", "Whisper not found. Do you want to build it?"
        ):
            self.lbl_status.config(text="Building Whisper...")
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
            initialfile=initial_file
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
        """ Start the transcription process in a separate thread """
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
            "-i", self.file_path,
            "-ar", "16000",
            "-ac", "1",
            "-af", "highpass=f=150,lowpass=f=2800,afftdn=nf=-20",
            "-c:a", "pcm_s16le",
            "-y", self.temp_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def run_whisper(self) -> str:
        """Run whisper.cpp and return transcription"""
        cmd = [
            self.main_executable,
            "-m", self.model_path,
            "-f", self.temp_file,
            "-l", "ro",
            "--prompt", "Transcriere audio în limba română:",
            "-otxt"
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
        """ Update the status label with the given message """
        self.root.after(0, self.lbl_status.config, {"text": message})



if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperTranscriber(root)
    root.mainloop()
