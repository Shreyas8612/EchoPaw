# EchoPaw.py
from STT import transcribe_once
from LLM import generate_reply
from TTS import speak
from RAG import EchoMemory
import sys

# Initialize memory system
print("🚀 Initializing EchoPaw...")
mem = EchoMemory()

EXIT_WORDS = {"quit", "exit", "goodbye", "good-bye", "good bye", "Goodbye", "Good Bye", "Good bye"}

def main():
    history = []
    
    print("\n" + "="*60)
    print("🐾 EchoPaw AI Companion Ready!")
    print("="*60)
    print("Commands:")
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
                stats = mem.get_memory_stats()
                print(f"\n📊 Memory Statistics:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")
                continue
            elif user_input.lower() in EXIT_WORDS:
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

            system_prefix = (
                f"You are EchoPaw, a friendly AI companion. {memory_context}\n\n"
                "Respond naturally and empathetically. If you remember something specific "
                "about the user, reference it naturally in conversation. Keep responses "
                "concise but warm."
            )

            # Generate response
            print("🤔 Thinking...")
            assistant_text, history = generate_reply(
                user_text, history, system_prompt=system_prefix, max_new_tokens=150
            )

            print(f"🐾 ECHO ➜ {assistant_text}")
            
            # Text-to-speech (comment out if causing issues)
            try:
                print("🔊 Speaking...")
                speak(assistant_text)
            except Exception as e:
                print(f"⚠️  TTS failed: {e}")
                print("Continuing without audio...")

    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("\n💾 Saving memories...")
        mem.flush()
        print("👋 Goodbye! Thanks for chatting with EchoPaw!")

if __name__ == "__main__":
    # Quick system check
    print("🔧 System Check:")
    try:
        from STT import get_optimal_device as stt_device
        from LLM import _device as llm_device
        print(f"   STT Device: {stt_device()}")
        print(f"   LLM Device: {llm_device}")
        print(f"   Memory: {len(mem.vstore.docstore)} stored memories")
        print("✅ All systems ready!")
    except Exception as e:
        print(f"⚠️  System check warning: {e}")
    
    main()