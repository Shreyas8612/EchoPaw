<<<<<<< HEAD
=======
# TTS.py
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
import torch
import time
import torchaudio
from transformers import CsmForConditionalGeneration, AutoProcessor
from pathlib import Path

def get_optimal_device():
<<<<<<< HEAD
    # Check if NVIDIA GPU is available first
    if torch.cuda.is_available():
        return "cuda"
    # Then check for Apple Silicon GPU
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    # Fall back to CPU if no GPU available
    else:
        return "cpu"

# Global variables for the TTS system
model_id = "sesame/csm-1b"  # The voice cloning model we're using
_device = get_optimal_device()  # Find the best device available
print(f"TTS using device: {_device}")

# These will hold our loaded model components
_processor = None  # Handles text and audio processing
_model = None  # The actual TTS model
_conversation = None  # Voice samples for cloning

# Voice sample data for Naomi Scott
Naomi_Scott = [
    {
        "path": "/Users/shreyasravi/Desktop/EchoPaw/paw/Naomi Scott.mp3",  # Audio file location
=======
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

# Global variables
model_id = "sesame/csm-1b"
_device = get_optimal_device()
print(f"TTS using device: {_device}")

_processor = None
_model = None
_conversation = None

# Naomi Scott voice files
Naomi_Scott = [
    {
        "path": "/Users/shreyasravi/Desktop/EchoPaw/paw/Naomi Scott.mp3",
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
        "text": """Here comes a wave meant to wash me away, 
a tide that is taking me under. Swallowing sand with nothing to say, my voice drowned out in the thunder. But I won't cry, and I won't start to crumble, whenever they try to shut me or cut me down.
I won't be silenced, you can't keep me quiet, won't tremble when you try it. All I know is I won't go speechless, cause I'll breathe when they try to suffocate me. Don't you underestimate me, cause I know that I won't go speechless.
Written in stone, every rule, every word, centuries old and unbending. Staking your place, better seen and not heard, but now that story is ending. Cause I, I cannot start to crumble.
So come on and try, try to shut me and cut me down. I won't be silenced, you can't keep me quiet, won't tremble when you try it. All I know is I won't go speechless.
Speechless of the summit, I cannot be broken. No, I won't live unspoken, cause I know that I won't go speechless. Try to lock me in this cage, I won't just lie me down inside.
I will take these broken wings and watch me burn. Can't get up to say I won't be silenced, so you won't see me tremble when you try it. All I know is I won't go speechless.
Speechless, cause I'm free when they try to suffocate me. Don't you underestimate me, cause I know that I won't go speechless. All I know is I won't go speechless.
<<<<<<< HEAD
Speechless."""  # The lyrics that match the audio file
=======
Speechless."""
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    }
]


def _load_audio_24khz(audio_path):
    try:
<<<<<<< HEAD
        # Load the audio file
        audio_tensor, sample_rate = torchaudio.load(audio_path)
        
        # Convert stereo to mono if needed
        if audio_tensor.shape[0] > 1:
            audio_tensor = torch.mean(audio_tensor, dim=0, keepdim=True)
        
        # Resample to 24kHz (required by the model)
        audio_tensor = torchaudio.functional.resample(
            audio_tensor.squeeze(0), orig_freq=sample_rate, new_freq=24000
        )
        
        # Convert to numpy array for the processor
        return audio_tensor.numpy()
    except Exception as e:
        print(f"Error loading {audio_path}: {e}")
        return None  # Return None if loading fails

def _initialize_model():
    # Access the global variables
    global _processor, _model, _conversation
    
    # Only initialize if not already loaded
    if _processor is None or _model is None:
        # Load the text and audio processor
        _processor = AutoProcessor.from_pretrained(model_id)
        
        # Load model with device-specific settings
        if _device == "cuda":
            # GPU loading with half precision for speed
            _model = CsmForConditionalGeneration.from_pretrained(
                model_id, 
                device_map="cuda",  # Automatic GPU memory management
                torch_dtype=torch.float16  # Half precision for speed
            )
        elif _device == "mps":
            # Apple Silicon loading
            _model = CsmForConditionalGeneration.from_pretrained(
                model_id, 
                torch_dtype=torch.float16  # Half precision
            ).to("mps")  # Move to Apple GPU
        else:
            # CPU loading with full precision
            _model = CsmForConditionalGeneration.from_pretrained(
                model_id, 
                torch_dtype=torch.float32  # Full precision for CPU
            ).to("cpu")
        
        # Build the voice context from sample files
        _conversation = []
        for file_info in Naomi_Scott:
            # Fix path separators for cross-platform compatibility
            audio_path = file_info["path"].replace("\\", "/")
            
            # Load and process the audio sample
            audio_array = _load_audio_24khz(audio_path)
            
            if audio_array is not None:
                # Add this voice sample to our context
                _conversation.append({
                    "role": "0",  # Speaker ID 0 for Naomi Scott
                    "content": [
                        {"type": "text", "text": file_info["text"]},  # The transcript
                        {"type": "audio", "path": audio_array}  # The audio data
=======
        audio_tensor, sample_rate = torchaudio.load(audio_path)
        # Convert to mono if stereo
        if audio_tensor.shape[0] > 1:
            audio_tensor = torch.mean(audio_tensor, dim=0, keepdim=True)
        # Resample to 24kHz
        audio_tensor = torchaudio.functional.resample(
            audio_tensor.squeeze(0), orig_freq=sample_rate, new_freq=24000
        )
        return audio_tensor.numpy()
    except Exception as e:
        print(f"Error loading {audio_path}: {e}")
        return None

def _initialize_model():
    global _processor, _model, _conversation
    if _processor is None or _model is None:
        _processor = AutoProcessor.from_pretrained(model_id)
        
        # Device-specific model loading
        if _device == "cuda":
            _model = CsmForConditionalGeneration.from_pretrained(
                model_id, 
                device_map="cuda",
                torch_dtype=torch.float16
            )
        elif _device == "mps":
            _model = CsmForConditionalGeneration.from_pretrained(
                model_id, 
                torch_dtype=torch.float16
            ).to("mps")
        else:
            _model = CsmForConditionalGeneration.from_pretrained(
                model_id, 
                torch_dtype=torch.float32
            ).to("cpu")
        
        _conversation = []
        for file_info in Naomi_Scott:
            # Use forward slashes for cross-platform compatibility
            audio_path = file_info["path"].replace("\\", "/")
            audio_array = _load_audio_24khz(audio_path)
            if audio_array is not None:
                _conversation.append({
                    "role": "0",  # Speaker ID 0 for Naomi Scott
                    "content": [
                        {"type": "text", "text": file_info["text"]},
                        {"type": "audio", "path": audio_array}
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
                    ]
                })
            else:
                print(f"Warning: Failed to load {audio_path}")

def speak(text: str, wav_path: str | Path = None) -> None:
<<<<<<< HEAD
    # Access global variables
    global _processor, _model, _conversation
    
    # Use default output path if none provided
    if wav_path is None:
        wav_path = Path.cwd() / "EchoPaw.wav"
    
    # Make sure the model is loaded
    _initialize_model()
    
    # Create conversation with voice context plus new text
    conversation = _conversation.copy()  # Start with voice samples
    conversation.append({
        "role": "0",  # Same speaker ID as context (Naomi Scott)
        "content": [{"type": "text", "text": text}]  # The text we want to speak
    })
    
    # Start timing the generation
    start = time.time()
    
    try:
        # Prepare inputs for the model
        inputs = _processor.apply_chat_template(
            conversation,
            tokenize=True,  # Convert text to tokens
            return_dict=True,  # Return as dictionary
        ).to(_device)  # Move to the right device
        
        # Generate the audio without storing gradients (saves memory)
        with torch.no_grad():
            audio = _model.generate(**inputs, output_audio=True)
        
        # Save the generated audio to file
        _processor.save_audio(audio, str(wav_path))
        
        # Show generation time
        print(f"(TTS → {wav_path} {time.time()-start:.2f}s)")
        
    except Exception as e:
        # Handle errors gracefully
        print(f"TTS generation failed: {e}")
        print("Continuing without audio...")  # Don't crash the whole program
=======
    global _processor, _model, _conversation
    if wav_path is None:
        wav_path = Path.cwd() / "EchoPaw.wav"
    
    # Initialize model if needed
    _initialize_model()
    
    # Build conversation with Naomi Scott's Voice
    conversation = _conversation.copy()
    conversation.append({
        "role": "0",  # Same speaker ID as context
        "content": [{"type": "text", "text": text}]
    })
    
    start = time.time()
    
    try:
        # Prepare inputs
        inputs = _processor.apply_chat_template(
            conversation,
            tokenize=True,
            return_dict=True,
        ).to(_device)
        
        # Generate audio
        with torch.no_grad():  # Save memory
            audio = _model.generate(**inputs, output_audio=True)
        
        # Save the audio
        _processor.save_audio(audio, str(wav_path))
        print(f"(TTS → {wav_path} {time.time()-start:.2f}s)")
        
    except Exception as e:
        print(f"TTS generation failed: {e}")
        # Fallback: create a simple beep or silence
        print("Continuing without audio...")
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
