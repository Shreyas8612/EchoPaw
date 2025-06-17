# RAG_demo.py
from RAG import EchoMemory
import time

def main():
    mem = EchoMemory(path="RAG_Demo_Memory")
    time.sleep(1)
    
    # Phase 1: Adding memories
    print("\n" + "PHASE 1: STORING PERSONAL INFORMATION")
    print("-" * 50)
    
    demo_facts = [
        "My sister Sarah works as a nurse at the NHS",
        "I love running on the beach",
        "My mother lives in Manchester and loves gardening",
        "I work as a software engineer at a tech startup",
        "My favorite food is Italian pasta, especially pizza",
        "I have a pet dog named Max who loves playing fetch"
    ]
    
    print(f" Adding {len(demo_facts)} personal facts to memory...")
    success_count = 0
    for i, fact in enumerate(demo_facts, 1):
        print(f"  {i:2d}. Storing: {fact}")
        if mem.add_fact(fact, {"category": "personal", "demo": True}):
            success_count += 1
        time.sleep(0.5)  # Pause for visual effect
    
    print(f"\n Successfully stored {success_count}/{len(demo_facts)} memories")
    
    # Show memory statistics
    print(f"\n📊 Memory Status:")
    stats = mem.get_memory_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Phase 2: Testing recall
    print("\n" + "PHASE 2: TESTING MEMORY RECALL")
    print("-" * 50)
    
    test_queries = [
        "Family",
        "What work do people do?",
        "Hobbies and interests", 
        "Pets"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: '{query}'")
        print("   Searching memory...")
        
        recalled_memories = mem.recall(query, k=3)
        
        if recalled_memories:
            print(f"  Found {len(recalled_memories)} relevant memories:")
            for j, memory in enumerate(recalled_memories, 1):
                print(f"      {j}. {memory}")
        else:
            print("   ❌ No relevant memories found")
        
        time.sleep(1)
    
    # Phase 3: Advanced search with similarity scores
    print("\n" + "PHASE 3: SIMILARITY SEARCH WITH SCORES")
    print("-" * 50)
    
    advanced_queries = ["family relationships", "professional career", "pets and animals"]
    
    for query in advanced_queries:
        print(f"\n🔬 Advanced search: '{query}'")
        results = mem.search_memories(query, k=5)
        
        if results:
            print("   📊 Results with similarity scores:")
            for result in results:
                score = result['similarity_score']
                content = result['content']
                print(f"      Score: {score:.3f} | {content}")
        else:
            print("   No results found")
    
    # Phase 4: Demonstrate conversation context
    print("\n" + "PHASE 4: CONVERSATION CONTEXT SIMULATION")
    print("-" * 50)
    
    conversation_inputs = [
        "How is my sister doing?",
        "I'm thinking about getting another pet",
        "Tell me about my work situation",
        "What hobbies do I enjoy?"
    ]
    
    for conv_input in conversation_inputs:
        print(f"\n User says: '{conv_input}'")
        
        # Simulate what EchoPaw would do
        context_memories = mem.recall(conv_input, k=2)
        
        if context_memories:
            print("   🐾 EchoPaw recalls:")
            for memory in context_memories:
                print(f"      • {memory}")
            
            print("   💭 EchoPaw could respond using this context...")
        else:
            print("   🐾 EchoPaw has no relevant memories for this topic")
    
    # Summary
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