from langchain_core.documents import Document  # For storing text with metadata
from langchain_community.vectorstores import FAISS  # Vector database for similarity search
from langchain_huggingface import HuggingFaceEmbeddings  # Converts text to vectors
from pathlib import Path
import json
from datetime import datetime
import uuid  # For generating unique IDs

class EchoMemory:
    def __init__(self, path="memory"):
        # Create the memory folder if it doesn't exist
        self.path = Path(path)
        self.path.mkdir(exist_ok=True)
        
        # Initialize the text-to-vector converter
        try:
            # Try the main embeddings model first
            self.embed = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")
            print("Embeddings model loaded successfully")
        except Exception as e:
            print(f"Error loading embeddings model: {e}")
            # Use a backup model if the main one fails
            self.embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # File to store memory statistics
        self.stats_file = self.path / "memory_stats.json"
        self.load_stats()  # Load existing stats or create new ones
        
        # Check if we have an existing memory database
        if (self.path / "index.faiss").exists() and (self.path / "index.pkl").exists():
            try:
                # Load the existing vector database
                self.vstore = FAISS.load_local(
                    str(self.path), 
                    self.embed, 
                    allow_dangerous_deserialization=True  # We trust our own files
                )
                print(f"✅ Loaded existing memory with {self._count_real_docs()} memories")
            except Exception as e:
                print(f"Failed to load existing memory: {e}")
                self._create_new_store()  # Create new if loading fails
        else:
            # No existing database, create a new one
            self._create_new_store()
        
        # Set up the retriever for searching memories
        self.retriever = self.vstore.as_retriever(search_kwargs={"k": 5})
    
    def load_stats(self):
        # Load memory statistics from file
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                # Create default stats if file is corrupted
                self.stats = {"total_memories": 0, "created": str(datetime.now())}
        else:
            # Create new stats file
            self.stats = {"total_memories": 0, "created": str(datetime.now())}
    
    def save_stats(self):
        # Save current statistics to file
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Failed to save stats: {e}")
    
    def _count_real_docs(self):
        # Count actual memories (not dummy initialization documents)
        try:
            count = 0
            if hasattr(self.vstore.docstore, '_dict'):
                # For InMemoryDocstore - check each document
                for doc in self.vstore.docstore._dict.values():
                    if not doc.metadata.get("temp", False):  # Skip temporary docs
                        count += 1
            elif hasattr(self.vstore.docstore, 'search'):
                # Alternative method for different docstore types
                try:
                    # Go through all document IDs
                    for doc_id in self.vstore.index_to_docstore_id.values():
                        doc = self.vstore.docstore.search(doc_id)
                        if doc and not doc.metadata.get("temp", False):
                            count += 1
                except:
                    pass  # Ignore errors in counting
            return count
        except Exception as e:
            print(f"Error counting docs: {e}")
            return 0
    
    def _get_real_docs(self):
        # Get all actual memory documents (excluding dummy ones)
        try:
            real_docs = []
            if hasattr(self.vstore.docstore, '_dict'):
                # For InMemoryDocstore
                for doc in self.vstore.docstore._dict.values():
                    if not doc.metadata.get("temp", False):  # Skip temporary docs
                        real_docs.append(doc)
            elif hasattr(self.vstore.docstore, 'search'):
                # Alternative access method
                try:
                    for doc_id in self.vstore.index_to_docstore_id.values():
                        doc = self.vstore.docstore.search(doc_id)
                        if doc and not doc.metadata.get("temp", False):
                            real_docs.append(doc)
                except:
                    pass  # Ignore errors
            return real_docs
        except Exception as e:
            print(f"Error getting docs: {e}")
            return []
    
    def _create_new_store(self):
        # Create a new empty vector database
        try:
            print("Creating new memory store")
            
            # FAISS needs at least one document to initialize, so we create a dummy one
            dummy_doc = Document(
                page_content="This is a temporary initialization document", 
                metadata={"temp": True, "id": "dummy"}  # Mark as temporary
            )
            
            # Create the vector store with the dummy document
            self.vstore = FAISS.from_documents([dummy_doc], self.embed)
            print("✅ Created new empty memory store")
            
        except Exception as e:
            print(f"Error creating new store: {e}")
            raise

    def add_fact(self, fact: str, metadata: dict | None = None):
        # Add a new memory to the database
        try:
            # Don't store empty facts
            if not fact.strip():
                return False
            
            # Add timestamp and unique ID to the metadata
            if metadata is None:
                metadata = {}
            metadata.update({
                "timestamp": str(datetime.now()),  # When this was stored
                "source": "conversation",  # Where it came from
                "id": str(uuid.uuid4())  # Unique identifier
            })
            
            # Create a document object
            doc = Document(page_content=fact.strip(), metadata=metadata)
            
            # Check if this is our first real memory
            real_count = self._count_real_docs()
            
            if real_count == 0:
                # Replace the dummy document with the first real memory
                self.vstore = FAISS.from_documents([doc], self.embed)
            else:
                # Add to the existing store
                self.vstore.add_documents([doc])
            
            # Save the database to disk immediately
            self.vstore.save_local(str(self.path))
            
            # Update our statistics
            new_count = self._count_real_docs()
            self.stats["total_memories"] = new_count
            self.stats["last_updated"] = str(datetime.now())
            self.save_stats()
            
            # Show confirmation message
            print(f"💾 Remembered: {fact[:50]}... (Total: {new_count})")
            return True
            
        except Exception as e:
            print(f"Failed to add memory: {e}")
            import traceback
            traceback.print_exc()  # Show full error for debugging
            return False

    def recall(self, query: str, k=5) -> list[str]:
        # Search for relevant memories based on a query
        try:
            # Check if we have any real memories stored
            real_count = self._count_real_docs()
            
            if real_count == 0:
                print("🧠 No memories stored yet")
                return []
            
            # Search for similar memories (get extra results to filter out dummy docs)
            docs_and_scores = self.vstore.similarity_search_with_score(query, k=k*2)
            
            # Filter out dummy documents and keep the best matches
            real_memories = []
            for doc, score in docs_and_scores:
                if not doc.metadata.get("temp", False):  # Skip temporary docs
                    real_memories.append(doc.page_content)
                if len(real_memories) >= k:  # Stop when we have enough
                    break
            
            if real_memories:
                print(f"🔍 Recalled {len(real_memories)} relevant memories")
                # Show what was found (for demonstration)
                for i, memory in enumerate(real_memories, 1):
                    print(f"  {i}. {memory[:60]}...")
            else:
                print("🧠 No relevant memories found")
            
            return real_memories
            
        except Exception as e:
            print(f"Memory recall failed: {e}")
            return []

    def get_all_memories(self) -> list[dict]:
        # Return all stored memories with their metadata
        try:
            all_memories = []
            real_docs = self._get_real_docs()  # Get all real documents
            
            # Convert each document to a dictionary
            for doc in real_docs:
                all_memories.append({
                    "content": doc.page_content,  # The actual memory text
                    "metadata": doc.metadata  # Additional information
                })
            return all_memories
        except Exception as e:
            print(f"Failed to retrieve all memories: {e}")
            return []

    def search_memories(self, query: str, k=10) -> list[dict]:
        # Search memories and return results with similarity scores
        try:
            real_count = self._count_real_docs()
            
            # Return empty if no memories exist
            if real_count == 0:
                return []
            
            # Search with similarity scores
            docs_and_scores = self.vstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_and_scores:
                # Skip dummy documents
                if not doc.metadata.get("temp", False):
                    results.append({
                        "content": doc.page_content,  # The memory text
                        "metadata": doc.metadata,  # Additional info
                        "similarity_score": float(score)  # How relevant it is
                    })
            
            return results
            
        except Exception as e:
            print(f"Memory search failed: {e}")
            return []

    def get_memory_stats(self) -> dict:
        # Get current statistics about the memory system
        current_count = self._count_real_docs()
        self.stats["current_memories"] = current_count
        return self.stats

    def flush(self):
        # Force save everything to disk
        try:
            self.vstore.save_local(str(self.path))  # Save vector database
            self.save_stats()  # Save statistics
            real_count = self._count_real_docs()
            print(f"💾 Memory saved ({real_count} memories)")
        except Exception as e:
            print(f"Failed to save memory: {e}")