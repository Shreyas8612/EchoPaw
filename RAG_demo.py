<<<<<<< HEAD
=======
# RAG_demo.py
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
from RAG import EchoMemory
import time

def main():
<<<<<<< HEAD
    # Create a new memory instance for the demo
    mem = EchoMemory(path="demo_memory")
    time.sleep(1)  # Brief pause to let initialization complete
=======
    mem = EchoMemory(path="RAG_Demo_Memory")
    time.sleep(1)
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    
    # Phase 1: Adding memories
    print("\n" + "PHASE 1: STORING PERSONAL INFORMATION")
    print("-" * 50)
    
<<<<<<< HEAD
    # Sample personal facts to store in memory
=======
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    demo_facts = [
        "My sister Sarah works as a nurse at the NHS",
        "I love running on the beach",
        "My mother lives in Manchester and loves gardening",
        "I work as a software engineer at a tech startup",
        "My favorite food is Italian pasta, especially pizza",
        "I have a pet dog named Max who loves playing fetch"
    ]
    
<<<<<<< HEAD
    print(f"📥 Adding {len(demo_facts)} personal facts to memory...")
    success_count = 0  # Track how many facts were successfully stored
    
    # Store each fact one by one
    for i, fact in enumerate(demo_facts, 1):
        print(f"  {i:2d}. Storing: {fact}")
        # Add the fact with metadata tags
        if mem.add_fact(fact, {"category": "personal", "demo": True}):
            success_count += 1
        time.sleep(0.5)  # Pause for visual effect in demo
    
    print(f"\n✅ Successfully stored {success_count}/{len(demo_facts)} memories")
    
    # Show current memory statistics
=======
    print(f" Adding {len(demo_facts)} personal facts to memory...")
    success_count = 0
    for i, fact in enumerate(demo_facts, 1):
        print(f"  {i:2d}. Storing: {fact}")
        if mem.add_fact(fact, {"category": "personal", "demo": True}):
            success_count += 1
        time.sleep(0.5)  # Pause for visual effect
    
    print(f"\n Successfully stored {success_count}/{len(demo_facts)} memories")
    
    # Show memory statistics
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    print(f"\n📊 Memory Status:")
    stats = mem.get_memory_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Phase 2: Testing recall
    print("\n" + "PHASE 2: TESTING MEMORY RECALL")
    print("-" * 50)
    
<<<<<<< HEAD
    # Test queries to see what the memory system can recall
    test_queries = [
        "Family",
        "What work do people do?",
        "Hobbies and interests",
        "Pets"
    ]
    
    # Try each query and see what memories come back
=======
    test_queries = [
        "Family",
        "What work do people do?",
        "Hobbies and interests", 
        "Pets"
    ]
    
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: '{query}'")
        print("   Searching memory...")
        
<<<<<<< HEAD
        # Search for up to 3 relevant memories
        recalled_memories = mem.recall(query, k=3)
        
        if recalled_memories:
            print(f"   Found {len(recalled_memories)} relevant memories:")
            for j, memory in enumerate(recalled_memories, 1):
                print(f"     {j}. {memory}")
        else:
            print("   ❌ No relevant memories found")
        
        time.sleep(1)  # Pause between queries
=======
        recalled_memories = mem.recall(query, k=3)
        
        if recalled_memories:
            print(f"  Found {len(recalled_memories)} relevant memories:")
            for j, memory in enumerate(recalled_memories, 1):
                print(f"      {j}. {memory}")
        else:
            print("   ❌ No relevant memories found")
        
        time.sleep(1)
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    
    # Phase 3: Advanced search with similarity scores
    print("\n" + "PHASE 3: SIMILARITY SEARCH WITH SCORES")
    print("-" * 50)
    
<<<<<<< HEAD
    # More specific queries to test similarity matching
=======
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    advanced_queries = ["family relationships", "professional career", "pets and animals"]
    
    for query in advanced_queries:
        print(f"\n🔬 Advanced search: '{query}'")
<<<<<<< HEAD
        # Get results with similarity scores
=======
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
        results = mem.search_memories(query, k=5)
        
        if results:
            print("   📊 Results with similarity scores:")
            for result in results:
<<<<<<< HEAD
                score = result['similarity_score']  # How similar the memory is
                content = result['content']  # The actual memory text
                print(f"     Score: {score:.3f} | {content}")
=======
                score = result['similarity_score']
                content = result['content']
                print(f"      Score: {score:.3f} | {content}")
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
        else:
            print("   No results found")
    
    # Phase 4: Demonstrate conversation context
    print("\n" + "PHASE 4: CONVERSATION CONTEXT SIMULATION")
    print("-" * 50)
    
<<<<<<< HEAD
    # Simulate what a user might say in conversation
=======
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
    conversation_inputs = [
        "How is my sister doing?",
        "I'm thinking about getting another pet",
        "Tell me about my work situation",
        "What hobbies do I enjoy?"
    ]
    
<<<<<<< HEAD
    # For each input, show what memories would be recalled
    for conv_input in conversation_inputs:
        print(f"\n👤 User says: '{conv_input}'")
        
        # Simulate what EchoPaw would do - search for relevant context
=======
    for conv_input in conversation_inputs:
        print(f"\n User says: '{conv_input}'")
        
        # Simulate what EchoPaw would do
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
        context_memories = mem.recall(conv_input, k=2)
        
        if context_memories:
            print("   🐾 EchoPaw recalls:")
            for memory in context_memories:
<<<<<<< HEAD
                print(f"     • {memory}")
=======
                print(f"      • {memory}")
            
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
            print("   💭 EchoPaw could respond using this context...")
        else:
            print("   🐾 EchoPaw has no relevant memories for this topic")
    
    # Summary
<<<<<<< HEAD
    print("\n" + "=" * 50)
    print("📋 DEMO SUMMARY")
    print("=" * 50)
    
    # Count total memories using the proper method
    total_memories = mem._count_real_docs()
    print(f"   Total memories stored: {total_memories}")
    
    # Save the current memory state to disk
    mem.flush()
    print("   Memory state saved to disk ✅")
    
    return mem  # Return the memory object for further use

# Only run the demo if this file is executed directly
if __name__ == "__main__":
    main()
    # Keep terminal open so user can see results
    input("\n🎯 Demo complete! Press Enter to exit...")
=======
    print("-" * 50)
    
    # Use our proper counting method instead of len(docstore)
    total_memories = mem._count_real_docs()
    print(f" Total memories stored: {total_memories}")
    
    # Save memory state
    mem.flush()
    
    return mem

if __name__ == "__main__":
    main()
    
    # Keep terminal open for screenshots
    input(" ")
>>>>>>> 3ca2edab769a3797c454aea5c6a73e0ddce660cc
