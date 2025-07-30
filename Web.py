from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Allow cross-origin requests from web browsers
import os
import traceback
from pathlib import Path

# Import the EchoPaw core components
try:
    from LLM import generate_reply  # AI text generation
    from RAG import EchoMemory  # Memory storage and retrieval
    print("✅ Core modules loaded successfully")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    exit(1)  # Stop the server if core modules can't load

# Create the Flask web application
app = Flask(__name__)
CORS(app)  # Allow web browsers to access the API

# Initialize EchoPaw components when server starts
print("🚀 Initializing EchoPaw web server...")
try:
    mem = EchoMemory()  # Create memory system
    history = []  # Store conversation history
    print("✅ Memory system initialized")
except Exception as e:
    print(f"❌ Memory initialization failed: {e}")
    exit(1)  # Stop if memory system fails

@app.route('/')
def index():
    # Serve the main web interface
    try:
        # Look for HTML files in the current directory
        html_files = [f for f in os.listdir('.') if f.endswith('.html')]
        
        if not html_files:
            # If no HTML file exists, create a simple status page
            return """
            <!DOCTYPE html>
            <html><head><title>EchoPaw</title></head>
            <body>
                <h1>🐾 EchoPaw Server Running</h1>
                <p>Please create an HTML file for the interface.</p>
                <p>Available endpoints:</p>
                <ul>
                    <li>POST /listen - Speech to text</li>
                    <li>POST /chat - Chat with EchoPaw</li>
                    <li>GET /status - Server status</li>
                </ul>
            </body></html>
            """
        
        # Read and serve the first HTML file found
        html_file = html_files[0]
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"📄 Serving {html_file}")
            return content
        except Exception as e:
            return f"❌ Error reading {html_file}: {str(e)}", 500
    
    except Exception as e:
        return f"❌ Server error: {str(e)}", 500

@app.route('/status')
def status():
    # Return server status and statistics
    try:
        stats = mem.get_memory_stats()  # Get memory system stats
        
        # Check what devices each component is using
        try:
            from STT import get_optimal_device
            stt_device = get_optimal_device()
        except:
            stt_device = "unknown"
        
        try:
            from LLM import _device
            llm_device = _device
        except:
            llm_device = "unknown"
        
        # Return status information as JSON
        return jsonify({
            'status': 'running',
            'memory_stats': stats,
            'devices': {
                'stt': stt_device,  # Speech-to-text device
                'llm': llm_device   # Language model device
            },
            'conversation_length': len(history)  # How many turns in current chat
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/listen', methods=['POST'])
def listen():
    # Handle speech-to-text requests from the web interface
    try:
        print("🎤 Starting speech recognition...")
        
        # Import STT module with error handling
        try:
            from STT import transcribe_once
        except ImportError as e:
            print(f"❌ STT import failed: {e}")
            return jsonify({'error': 'Speech recognition not available'}), 500
        
        # Get recording duration from the request (default 5 seconds)
        data = request.get_json() or {}
        record_seconds = data.get('duration', 5)
        
        # Convert speech to text
        transcription = transcribe_once(record_seconds=record_seconds)
        
        if transcription:
            print(f"✅ Transcribed: '{transcription}'")
            return jsonify({
                'transcription': transcription,
                'success': True
            })
        else:
            print("⚠️ No speech detected")
            return jsonify({
                'transcription': '',
                'success': False,
                'message': 'No speech detected'
            })
    
    except Exception as e:
        error_msg = f"Speech recognition error: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())  # Show full error for debugging
        return jsonify({'error': error_msg}), 500

@app.route('/chat', methods=['POST'])
def chat():
    # Handle chat requests with EchoPaw AI
    try:
        # Get the message from the web request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"👤 User: {user_message}")
        
        # Words that trigger memory storage (important personal info)
        memory_triggers = [
            "sister", "brother", "mother", "father", "family", "parent",  # Family
            "work", "job", "career", "colleague", "boss", "office",  # Work
            "hobby", "interest", "like", "love", "enjoy", "favorite",  # Interests
            "pet", "dog", "cat", "animal", "friend", "live", "home", "son", "daughter"  # Personal
        ]
        
        # Store important information in memory
        if any(trigger in user_message.lower() for trigger in memory_triggers):
            mem.add_fact(user_message, {"source": "web_chat", "importance": "high"})
            print("💾 Added to memory")
        
        # Search for relevant memories to provide context
        memories = mem.recall(user_message, k=3)
        
        # Build the AI's context using stored memories
        if memories:
            memory_context = "Here's what I remember about you:\n" + "\n".join(f"• {m}" for m in memories)
            print(f"🧠 Using {len(memories)} memories")
        else:
            memory_context = "I don't have any specific memories about you yet."
            print("🧠 No relevant memories found")
        
        # Create the system prompt with memory context
        system_prefix = (
            f"You are EchoPaw, a friendly AI companion. {memory_context}\n\n"
            "Respond naturally and empathetically. Keep responses concise but warm. "
            "If you remember something specific about the user, reference it naturally."
        )
        
        # Generate AI response using the language model
        global history
        assistant_text, history = generate_reply(
            user_message,
            history,
            system_prompt=system_prefix,
            max_new_tokens=150  # Keep responses reasonably short
        )
        
        print(f"🐾 EchoPaw: {assistant_text}")
        
        # Generate speech audio from the text response
        audio_url = None
        try:
            from TTS import speak
            audio_filename = "echopaw_response.wav"
            audio_path = Path(audio_filename)
            
            # Convert text to speech and save as audio file
            speak(assistant_text, audio_path)
            
            if audio_path.exists():
                audio_url = f'/audio/{audio_filename}'  # URL to access the audio
                print(f"🔊 TTS audio generated: {audio_filename}")
            else:
                print("⚠️ TTS audio file not created")
        
        except Exception as tts_error:
            print(f"⚠️ TTS Error: {tts_error}")
            # Continue without audio if TTS fails
        
        # Save memory state to disk
        mem.flush()
        
        # Return the response to the web interface
        return jsonify({
            'response': assistant_text,  # The AI's text response
            'audio_url': audio_url,  # URL to the speech audio (if available)
            'memories_used': len(memories),  # How many memories were used for context
            'success': True
        })
    
    except Exception as e:
        error_msg = f"Chat processing error: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())  # Show full error for debugging
        return jsonify({'error': error_msg}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    # Serve audio files to the web interface
    try:
        # Security check - only allow .wav files
        if not filename.endswith('.wav'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Check if the audio file exists
        file_path = Path(filename)
        if file_path.exists():
            # Serve the audio file with proper MIME type
            return send_from_directory('.', filename, mimetype='audio/wav')
        else:
            print(f"❌ Audio file not found: {filename}")
            return jsonify({'error': 'Audio file not found'}), 404
    
    except Exception as e:
        print(f"❌ Audio serving error: {e}")
        return jsonify({'error': 'Audio serving failed'}), 500

@app.route('/memory')
def memory_info():
    # Return information about stored memories
    try:
        stats = mem.get_memory_stats()  # Get memory statistics
        all_memories = mem.get_all_memories()  # Get all stored memories
        
        return jsonify({
            'stats': stats,
            'total_memories': len(all_memories),
            'recent_memories': all_memories[-5:] if all_memories else []  # Last 5 memories
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Only run the server if this file is executed directly
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🐾 EchoPaw Web Server Starting...")
    print("="*50)
    
    # System check - show what devices are being used
    try:
        from STT import get_optimal_device
        from LLM import _device
        print(f"🔧 STT Device: {get_optimal_device()}")
        print(f"🔧 LLM Device: {_device}")
        print(f"🧠 Memory: {len(mem.vstore.docstore)} stored memories")
    except Exception as e:
        print(f"⚠️ System check warning: {e}")
    
    # Show connection information
    print("\n📡 Server will be available at:")
    print("   http://localhost:5000")
    print("\n🎤 Make sure your microphone is connected!")
    print("="*50)
    
    # Start the web server
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)  # Listen on all interfaces
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")