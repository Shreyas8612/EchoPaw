<<<<<<< HEAD
=======
# EchoPaw.py
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
from STT import transcribe_once
from LLM import generate_reply
from TTS import speak
from RAG import EchoMemory
import sys

<<<<<<< HEAD
# Initialize the memory system when EchoPaw starts
print("🚀 Initializing EchoPaw...")
mem = EchoMemory()

# Words that will end the conversation
EXIT_WORDS = {"quit", "exit", "goodbye", "good-bye", "good bye", "Goodbye", "Good Bye", "Good bye"}

def main():
    # Store conversation history for context
    history = []
    
    # Welcome message and instructions
=======
# Initialize memory system
print("🚀 Initializing EchoPaw...")
mem = EchoMemory()

EXIT_WORDS = {"quit", "exit", "goodbye", "good-bye", "good bye", "Goodbye", "Good Bye", "Good bye"}

def main():
    history = []
    
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    print("\n" + "="*60)
    print("🐾 EchoPaw AI Companion Ready!")
    print("="*60)
    print("Commands:")
<<<<<<< HEAD
    print(" • Press Enter to record audio")
    print(" • Say 'good-bye' to exit")
    print("="*60)
    
    try:
        # Main conversation loop
        while True:
            # Get user input (either text command or audio recording)
            user_input = input("\n💬 Hit Enter to record, or type command: ").strip()
            
            # Handle special text commands
            if user_input.lower() == 'demo':
                demonstrate_rag()  # Run memory demonstration
                continue
            elif user_input.lower() == 'stats':
                # Show memory statistics
=======
    print("  • Press Enter to record audio")
    print("  • Say 'good-bye' to exit")
    print("="*60)

    try:
        while True:
            user_input = input("\n💬 Hit Enter to record, or type command: ").strip()
            
            # Handle text commands
            if user_input.lower() == 'demo':
                demonstrate_rag()
                continue
            elif user_input.lower() == 'stats':
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
                stats = mem.get_memory_stats()
                print(f"\n📊 Memory Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                continue
            elif user_input.lower() in EXIT_WORDS:
<<<<<<< HEAD
                break  # Exit the conversation
            elif user_input:  # User typed something else
                user_text = user_input
                print(f"YOU (text) ➜ {user_text}")
            else:
                # No text input, so record audio instead
                print("\n🎤 Recording...")
                user_text = transcribe_once()  # Convert speech to text
                
                if not user_text:
                    print("❌ Sorry, I didn't catch that. Please try again.")
                    continue
                
                print(f"YOU (voice) ➜ {user_text}")
            
            # Check if user wants to exit
            if any(w in user_text.lower() for w in EXIT_WORDS):
                break
            
            # Smart memory detection - look for important personal information
            memory_triggers = [
                "sister", "brother", "mother", "father", "family", "parent",  # Family
                "work", "job", "career", "colleague", "boss",  # Work life
                "hobby", "interest", "like", "love", "enjoy",  # Interests
                "pet", "dog", "cat", "animal",  # Pets
                "live", "home", "house",  # Living situation
                "friend", "relationship", "partner", "son", "daughter"  # Relationships
            ]
            
            # If user mentions something important, store it in memory
            if any(trigger in user_text.lower() for trigger in memory_triggers):
                mem.add_fact(user_text, {"importance": "high"})
                print("💾 This seems important - I'll remember this!")
            
            # Search memory for relevant context
            memories = mem.recall(user_text, k=3)
            
            # Build context for the AI response
            if memories:
                # Include relevant memories in the context
                memory_context = "Here's what I remember about you:\n" + "\n".join(f"• {m}" for m in memories)
            else:
                # No relevant memories found
                memory_context = "I don't have any specific memories about you yet."
            
            # Create the system prompt with memory context
=======
                break
            elif user_input:  # If user typed something else
                user_text = user_input
                print(f"YOU (text) ➜ {user_text}")
            else:
                # Record audio
                print("\n🎤 Recording...")
                user_text = transcribe_once()
                if not user_text:
                    print("❌ Sorry, I didn't catch that. Please try again.")
                    continue
                print(f"YOU (voice) ➜ {user_text}")

            # Check for exit words
            if any(w in user_text.lower() for w in EXIT_WORDS):
                break

            # Smart memory detection - store important personal information
            memory_triggers = [
                "sister", "brother", "mother", "father", "family", "parent",
                "work", "job", "career", "colleague", "boss",
                "hobby", "interest", "like", "love", "enjoy",
                "pet", "dog", "cat", "animal",
                "live", "home", "house",
                "friend", "relationship", "partner", "son", "daughter"
            ]
            
            if any(trigger in user_text.lower() for trigger in memory_triggers):
                mem.add_fact(user_text, {"importance": "high"})
                print("💾 This seems important - I'll remember this!")

            # Retrieve relevant memories
            memories = mem.recall(user_text, k=3)
            
            # Build context for the LLM
            if memories:
                memory_context = "Here's what I remember about you:\n" + "\n".join(f"• {m}" for m in memories)
            else:
                memory_context = "I don't have any specific memories about you yet."

>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
            system_prefix = (
                f"You are EchoPaw, a friendly AI companion. {memory_context}\n\n"
                "Respond naturally and empathetically. If you remember something specific "
                "about the user, reference it naturally in conversation. Keep responses "
                "concise but warm."
            )
<<<<<<< HEAD
            
            # Generate AI response using the LLM
            print("🤔 Thinking...")
            assistant_text, history, metrics = generate_reply(
                user_text, 
                history, 
                system_prompt=system_prefix, 
                max_new_tokens=150  # Keep responses reasonably short
            )
            
            # Show the AI's response
            print(f"🐾 ECHO ➜ {assistant_text}")
            
            # Show performance metrics
            print(f"📊 Performance: {metrics['tokens_per_second']:.1f} tokens/sec on {metrics['device']} ({metrics['tokens_generated']} tokens in {metrics['generation_time']:.2f}s)")
            
            # Convert response to speech (with error handling)
=======

            # Generate response
            print("🤔 Thinking...")
            assistant_text, history = generate_reply(
                user_text, history, system_prompt=system_prefix, max_new_tokens=150
            )

            print(f"🐾 ECHO ➜ {assistant_text}")
            
            # Text-to-speech (comment out if causing issues)
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
            try:
                print("🔊 Speaking...")
                speak(assistant_text)
            except Exception as e:
<<<<<<< HEAD
                print(f"⚠️ TTS failed: {e}")
                print("Continuing without audio...")  # Don't crash if TTS fails
    
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n⏹️ Interrupted by user")
    except Exception as e:
        # Handle any other errors
        print(f"\n❌ Error: {e}")
    finally:
        # Always save memories before exiting
=======
                print(f"⚠️  TTS failed: {e}")
                print("Continuing without audio...")

    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
        print("\n💾 Saving memories...")
        mem.flush()
        print("👋 Goodbye! Thanks for chatting with EchoPaw!")

<<<<<<< HEAD
# Only run if this file is executed directly
if __name__ == "__main__":
    # Quick system check to make sure everything is working
=======
if __name__ == "__main__":
    # Quick system check
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    print("🔧 System Check:")
    try:
        from STT import get_optimal_device as stt_device
        from LLM import _device as llm_device
<<<<<<< HEAD
        
        # Show what devices each component is using
=======
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
        print(f"   STT Device: {stt_device()}")
        print(f"   LLM Device: {llm_device}")
        print(f"   Memory: {len(mem.vstore.docstore)} stored memories")
        print("✅ All systems ready!")
    except Exception as e:
<<<<<<< HEAD
        print(f"⚠️ System check warning: {e}")
    
    # Start the main conversation loop
=======
        print(f"⚠️  System check warning: {e}")
    
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    main()