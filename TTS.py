# TTS.py
import torch
import time
import torchaudio
from transformers import CsmForConditionalGeneration, AutoProcessor
from pathlib import Path

def get_optimal_device():
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
        "text": """Here comes a wave meant to wash me away, 
a tide that is taking me under. Swallowing sand with nothing to say, my voice drowned out in the thunder. But I won't cry, and I won't start to crumble, whenever they try to shut me or cut me down.
I won't be silenced, you can't keep me quiet, won't tremble when you try it. All I know is I won't go speechless, cause I'll breathe when they try to suffocate me. Don't you underestimate me, cause I know that I won't go speechless.
Written in stone, every rule, every word, centuries old and unbending. Staking your place, better seen and not heard, but now that story is ending. Cause I, I cannot start to crumble.
So come on and try, try to shut me and cut me down. I won't be silenced, you can't keep me quiet, won't tremble when you try it. All I know is I won't go speechless.
Speechless of the summit, I cannot be broken. No, I won't live unspoken, cause I know that I won't go speechless. Try to lock me in this cage, I won't just lie me down inside.
I will take these broken wings and watch me burn. Can't get up to say I won't be silenced, so you won't see me tremble when you try it. All I know is I won't go speechless.
Speechless, cause I'm free when they try to suffocate me. Don't you underestimate me, cause I know that I won't go speechless. All I know is I won't go speechless.
Speechless."""
    }
]


def _load_audio_24khz(audio_path):
    try:
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
                    ]
                })
            else:
                print(f"Warning: Failed to load {audio_path}")

def speak(text: str, wav_path: str | Path = None) -> None:
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