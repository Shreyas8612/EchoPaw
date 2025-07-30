from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
import time
import sys

def get_optimal_device():
    # Check if CUDA GPU is available first
    if torch.cuda.is_available():
        return "cuda"
    # Then check for Apple Silicon MPS
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    # Fall back to CPU if nothing else works
    else:
        return "cpu"

# The therapy-oriented model we want to use
MODEL_ID = "lavanyamurugesan123/Llama3.2-3B-Instruct-finetuned-Therapy-oriented"

# Find the best device available on this machine
_device = get_optimal_device()
print(f"LLM using device: {_device}")

# Choose the right data type for each device
if _device == "cuda":
    _dtype = torch.float16  # GPU can handle half precision for speed
elif _device == "mps":
    _dtype = torch.float16  # Apple Silicon also supports half precision
else:
    _dtype = torch.float32  # CPU needs full precision

# Load the tokenizer (converts text to numbers)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

# Load the model with device-specific settings
try:
    if _device == "cuda":
        # GPU loading with automatic memory management
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=_dtype,
            low_cpu_mem_usage=True,  # Don't use too much RAM during loading
            device_map="auto"  # Let transformers decide GPU placement
        )
    elif _device == "mps":
        # Apple Silicon loading
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=_dtype,
            low_cpu_mem_usage=True,
        ).to("mps")  # Move to Apple Silicon GPU
    else:
        # CPU loading
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=_dtype,
            low_cpu_mem_usage=True,
        ).to("cpu")  # Keep on CPU
    
    print(f"Model loaded successfully on {_device}")
    
except Exception as e:
    # If loading fails, try CPU as backup
    print(f"Error loading model on {_device}: {e}")
    print("Falling back to CPU...")
    _device = "cpu"
    _dtype = torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=_dtype,
        low_cpu_mem_usage=True,
    ).to("cpu")

# The system prompt that tells the AI how to behave
SYSTEM = (
    "You are a Psychology Assistant, kind and empathetic. "
    "Use evidence-based CBT & positive-psychology techniques. "
    "Never mention any personal data you haven't been told. "
    "Do not mention the other person's name, or any personal data you haven't been told."
    "Keep your responses short concise and sweet."
)

def count_tokens(text: str) -> int:
    # Convert text to tokens and count them
    return len(tokenizer.encode(text))

def generate_reply(
    user_text: str,
    history: list | None = None,
    system_prompt: str = SYSTEM,
    max_new_tokens: int = 256,
    stream: bool = False,
) -> tuple[str, list, dict]:  # Returns response, history, and performance metrics
    
    # Start with empty history if none provided
    if history is None:
        history = []

    # Add the user's message to conversation history
    history.append({"role": "user", "content": user_text})
    
    # Build the conversation in the format the model expects
    dialogue = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"{system_prompt}<|eot_id|>"
    )
    
    # Add each turn of the conversation
    for turn in history:
        role_tag = "user" if turn["role"] == "user" else "assistant"
        dialogue += (
            f"<|start_header_id|>{role_tag}<|end_header_id|>\n"
            f"{turn['content']}<|eot_id|>"
        )
    
    # Add the start tag for the assistant's response
    dialogue += "<|start_header_id|>assistant<|end_header_id|>\n"

    # Convert text to tokens and move to the right device
    inputs = tokenizer(dialogue, return_tensors="pt").to(_device)

    try:
        if stream:
            # Streaming mode - get tokens one by one as they're generated
            streamer = TextIteratorStreamer(
                tokenizer,
                skip_prompt=True,  # Don't repeat the input
                skip_special_tokens=True  # Don't show special tokens
            )
            
            start_time = time.time()  # Start measuring generation time
            
            # Set up generation in a separate thread
            from threading import Thread
            generation_kwargs = {
                **inputs,
                "max_new_tokens": max_new_tokens,
                "temperature": 0.7,  # Some randomness in responses
                "top_p": 0.9,  # Nucleus sampling
                "do_sample": True,  # Enable sampling
                "streamer": streamer,
                "pad_token_id": tokenizer.eos_token_id
            }
            
            # Start generation in background thread
            thread = Thread(target=model.generate, kwargs=generation_kwargs)
            thread.start()
            
            # Collect tokens as they come in
            reply_text = ""
            for token in streamer:
                reply_text += token
                
            # Wait for generation to complete
            thread.join()
            end_time = time.time()  # Stop measuring time
            
            # Calculate performance metrics
            generation_time = end_time - start_time
            token_count = count_tokens(reply_text.strip())
            tokens_per_second = token_count / generation_time if generation_time > 0 else 0
            
            metrics = {
                "tokens_generated": token_count,
                "generation_time": generation_time,
                "tokens_per_second": tokens_per_second,
                "device": _device
            }
            
            # Show performance info
            print(f"🚀 Generated {token_count} tokens in {generation_time:.2f}s = {tokens_per_second:.1f} tokens/sec on {_device}")
            
            # Add response to history and return everything
            history.append({"role": "assistant", "content": reply_text.strip()})
            return reply_text.strip(), history, metrics
            
        else:
            # Non-streaming mode - generate all at once
            start_time = time.time()  # Start measuring time
            
            # Generate without keeping gradients (saves memory)
            with torch.no_grad():
                output = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.7,  # Some randomness
                    top_p=0.9,  # Nucleus sampling
                    do_sample=True,  # Enable sampling
                    pad_token_id=tokenizer.eos_token_id
                )
            
            end_time = time.time()  # Stop measuring time
            
            # Extract just the new tokens (not the input)
            reply_text = tokenizer.decode(
                output[0][inputs["input_ids"].shape[1]:],  # Skip the input tokens
                skip_special_tokens=True,  # Don't show special tokens
            ).strip()
            
            # Calculate performance metrics
            generation_time = end_time - start_time
            token_count = count_tokens(reply_text)
            tokens_per_second = token_count / generation_time if generation_time > 0 else 0
            
            metrics = {
                "tokens_generated": token_count,
                "generation_time": generation_time,
                "tokens_per_second": tokens_per_second,
                "device": _device
            }
            
            # Show performance info
            print(f"🚀 Generated {token_count} tokens in {generation_time:.2f}s = {tokens_per_second:.1f} tokens/sec on {_device}")
            
            # Add response to history and return everything
            history.append({"role": "assistant", "content": reply_text})
            return reply_text, history, metrics
            
    except Exception as e:
        # If something goes wrong, return a safe fallback response
        print(f"Generation error: {e}")
        fallback_response = "I'm sorry, I'm having trouble processing that right now. Could you try again?"
        
        # Create basic metrics for the fallback
        metrics = {
            "tokens_generated": count_tokens(fallback_response),
            "generation_time": 0.0,
            "tokens_per_second": 0.0,
            "device": _device
        }
        
        # Add fallback to history and return
        history.append({"role": "assistant", "content": fallback_response})
        return fallback_response, history, metrics
            
    except Exception as e:
        # Duplicate error handling (this looks like a copy-paste error in original)
        print(f"Generation error: {e}")
        fallback_response = "I'm sorry, I'm having trouble processing that right now. Could you try again?"
        history.append({"role": "assistant", "content": fallback_response})
        return fallback_response, history