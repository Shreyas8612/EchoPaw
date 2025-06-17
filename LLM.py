# LLM.py
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
import time
import sys

def get_optimal_device():
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

MODEL_ID = "lavanyamurugesan123/Llama3.2-3B-Instruct-finetuned-Therapy-oriented"

# Device detection
_device = get_optimal_device()
print(f"LLM using device: {_device}")

# Optimal dtype based on device
if _device == "cuda":
    _dtype = torch.float16
elif _device == "mps":
    _dtype = torch.float16  # MPS supports float16
else:
    _dtype = torch.float32  # CPU fallback

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

# Load model with device-specific optimizations
try:
    if _device == "cuda":
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=_dtype,
            low_cpu_mem_usage=True,
            device_map="auto"  # Let transformers handle GPU placement
        )
    elif _device == "mps":
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=_dtype,
            low_cpu_mem_usage=True,
        ).to("mps")
    else:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=_dtype,
            low_cpu_mem_usage=True,
        ).to("cpu")
    
    print(f"Model loaded successfully on {_device}")
    
except Exception as e:
    print(f"Error loading model on {_device}: {e}")
    print("Falling back to CPU...")
    _device = "cpu"
    _dtype = torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=_dtype,
        low_cpu_mem_usage=True,
    ).to("cpu")

SYSTEM = (
    "You are a Psychology Assistant, kind and empathetic. "
    "Use evidence-based CBT & positive-psychology techniques. "
    "Never mention any personal data you haven't been told. "
    "Do not mention the other person's name, or any personal data you haven't been told."
    "Keep your responses short concise and sweet."
)

def generate_reply(
    user_text: str,
    history: list | None = None,
    system_prompt: str = SYSTEM,
    max_new_tokens: int = 256,
    stream: bool = False,
) -> tuple[str, list]:
    if history is None:
        history = []

    history.append({"role": "user", "content": user_text})
    dialogue = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"{system_prompt}<|eot_id|>"
    )
    for turn in history:
        role_tag = "user" if turn["role"] == "user" else "assistant"
        dialogue += (
            f"<|start_header_id|>{role_tag}<|end_header_id|>\n"
            f"{turn['content']}<|eot_id|>"
        )
    dialogue += "<|start_header_id|>assistant<|end_header_id|>\n"

    inputs = tokenizer(dialogue, return_tensors="pt").to(_device)

    try:
        if stream:
            streamer = TextIteratorStreamer(
                tokenizer,
                skip_prompt=True,
                skip_special_tokens=True
            )
            
            # Use threading for streaming
            from threading import Thread
            generation_kwargs = {
                **inputs,
                "max_new_tokens": max_new_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "streamer": streamer,
                "pad_token_id": tokenizer.eos_token_id
            }
            
            thread = Thread(target=model.generate, kwargs=generation_kwargs)
            thread.start()
            
            reply_text = ""
            for token in streamer:
                reply_text += token
                
            thread.join()
            history.append({"role": "assistant", "content": reply_text.strip()})
            return reply_text.strip(), history
        else:
            with torch.no_grad():  # Save memory
                output = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            reply_text = tokenizer.decode(
                output[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True,
            ).strip()
            
            history.append({"role": "assistant", "content": reply_text})
            return reply_text, history
            
    except Exception as e:
        print(f"Generation error: {e}")
        fallback_response = "I'm sorry, I'm having trouble processing that right now. Could you try again?"
        history.append({"role": "assistant", "content": fallback_response})
        return fallback_response, history