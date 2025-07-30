import pyaudio  # For recording audio from microphone
import wave  # For saving audio files
import tempfile
import os
import torch
from faster_whisper import WhisperModel

def get_optimal_device():
    # Check if NVIDIA GPU is available first
    if torch.cuda.is_available():
        return "cuda"
    # Then check for Apple Silicon GPU
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    # Use CPU if no GPU is available
    else:
        return "cpu"

class SpeechToText:
    def __init__(self):
        # Audio recording settings
        self.chunk = 1024  # How many audio samples to read at once
        self.format = pyaudio.paInt16  # 16-bit audio format
        self.channels = 1  # Mono audio (single channel)
        self.rate = 16000  # Sample rate (16kHz is good for speech)
        self.record_seconds = 5  # How long to record by default
        
        # Initialize the microphone interface
        self.audio = pyaudio.PyAudio()
        
        # Find the best device for processing
        self.device = get_optimal_device()
        print(f"STT using device: {self.device}")
        
        # Load Whisper model with device-specific settings
        if self.device == "cuda":
            # Use GPU with mixed precision for speed
            self.model = WhisperModel("base", device="cuda", compute_type="int8_float16")
        elif self.device == "mps":
            # MPS has compatibility issues, so use CPU with int8
            self.model = WhisperModel("base", device="cpu", compute_type="int8")
        else:
            # CPU with int8 quantization for efficiency
            self.model = WhisperModel("base", device="cpu", compute_type="int8")
    
    def record_audio(self):
        print("\nRecording... Speak now!")
        
        # Open the microphone stream
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,  # We want to record, not play
            frames_per_buffer=self.chunk,
        )
        
        # List to store audio data
        frames = []
        
        try:
            # Record for the specified duration
            for i in range(int(self.rate / self.chunk * self.record_seconds)):
                frames.append(stream.read(self.chunk))  # Read audio chunk
        finally:
            # Always clean up the stream
            stream.stop_stream()
            stream.close()
        
        return frames
    
    def save_temp_audio(self, frames):
        # Create a temporary wav file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        # Open the file for writing audio
        wf = wave.open(temp_file.name, "wb")
        wf.setnchannels(self.channels)  # Set to mono
        wf.setsampwidth(self.audio.get_sample_size(self.format))  # Set bit depth
        wf.setframerate(self.rate)  # Set sample rate
        wf.writeframes(b"".join(frames))  # Write all audio data
        wf.close()
        
        # Return the path to the temporary file
        return temp_file.name
    
    def transcribe_audio(self, audio_file):
        try:
            # Use Whisper to convert speech to text
            segments, _ = self.model.transcribe(audio_file, beam_size=5)
            # Join all segments into one text string
            return "".join(segment.text for segment in segments).strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""  # Return empty string if transcription fails
    
    def listen_and_transcribe(self):
        # Record audio from microphone
        frames = self.record_audio()
        
        # If no audio was recorded, return empty string
        if not frames:
            return ""
        
        # Save the recorded audio to a temporary file
        audio_file = self.save_temp_audio(frames)
        
        # Convert the audio file to text
        text = self.transcribe_audio(audio_file)
        
        # Delete the temporary file to save space
        os.unlink(audio_file)
        
        return text
    
    def cleanup(self):
        # Properly close the audio interface
        self.audio.terminate()

def transcribe_once(record_seconds: int = 5, device: str = None) -> str:
    # Create a new STT instance
    stt = SpeechToText()
    
    # Override recording duration if specified
    stt.record_seconds = record_seconds
    
    # Override device if specified
    if device:
        stt.device = device
        # Reload model with the specified device
        if device == "cuda":
            stt.model = WhisperModel("base", device="cuda", compute_type="int8_float16")
        else:
            stt.model = WhisperModel("base", device="cpu", compute_type="int8")
    
    try:
        # Record and transcribe audio
        return stt.listen_and_transcribe() or ""
    finally:
        # Always clean up resources
        stt.cleanup()