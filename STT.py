# STT.py
import pyaudio
import wave
import tempfile
import os
import torch
from faster_whisper import WhisperModel

def get_optimal_device():
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

class SpeechToText:
    def __init__(self):
        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds = 5
        
        # Mic
        self.audio = pyaudio.PyAudio()
        
        # Device detection
        self.device = get_optimal_device()
        print(f"STT using device: {self.device}")
        
        # Whisper STT model with optimal settings
        if self.device == "cuda":
            self.model = WhisperModel("base", device="cuda", compute_type="int8_float16")
        elif self.device == "mps":
            # MPS doesn't support int8, use float16
            self.model = WhisperModel("base", device="cpu", compute_type="int8")  # Fallback to CPU for MPS
        else:
            self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def record_audio(self):
        print("\nRecording... Speak now!")
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )
        frames = []
        try:
            for i in range(int(self.rate / self.chunk * self.record_seconds)):
                frames.append(stream.read(self.chunk))
        finally:
            stream.stop_stream()
            stream.close()
        return frames

    def save_temp_audio(self, frames):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wf = wave.open(temp_file.name, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(frames))
        wf.close()
        return temp_file.name

    def transcribe_audio(self, audio_file):
        try:
            segments, _ = self.model.transcribe(audio_file, beam_size=5)
            return "".join(segment.text for segment in segments).strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def listen_and_transcribe(self):
        frames = self.record_audio()
        if not frames:
            return ""
        audio_file = self.save_temp_audio(frames)
        text = self.transcribe_audio(audio_file)
        os.unlink(audio_file)
        return text

    def cleanup(self):
        self.audio.terminate()

def transcribe_once(record_seconds: int = 5, device: str = None) -> str:
    stt = SpeechToText()
    stt.record_seconds = record_seconds
    
    # Override device if specified
    if device:
        stt.device = device
        if device == "cuda":
            stt.model = WhisperModel("base", device="cuda", compute_type="int8_float16")
        else:
            stt.model = WhisperModel("base", device="cpu", compute_type="int8")
    
    try:
        return stt.listen_and_transcribe() or ""
    finally:
        stt.cleanup()