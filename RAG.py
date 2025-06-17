# RAG.py - Final working version
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path
import json
from datetime import datetime
import uuid

class EchoMemory:
    def __init__(self, path="memory"):
        self.path = Path(path)
        self.path.mkdir(exist_ok=True)
        
        # Initialize embeddings
        try:
            self.embed = HuggingFaceEmbeddings(model_name="intfloat/e5-small-v2")
            print("Embeddings model loaded successfully")
        except Exception as e:
            print(f"Error loading embeddings model: {e}")
            # Fallback to a smaller model
            self.embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Memory statistics file
        self.stats_file = self.path / "memory_stats.json"
        self.load_stats()
        
        # Check if existing FAISS index exists
        if (self.path / "index.faiss").exists() and (self.path / "index.pkl").exists():
            try:
                self.vstore = FAISS.load_local(
                    str(self.path), 
                    self.embed, 
                    allow_dangerous_deserialization=True
                )
                print(f"✅ Loaded existing memory with {self._count_real_docs()} memories")
            except Exception as e:
                print(f"Failed to load existing memory: {e}")
                self._create_new_store()
        else:
            # Create new store
            self._create_new_store()
        
        self.retriever = self.vstore.as_retriever(search_kwargs={"k": 5})
    
    def load_stats(self):
        """Load memory statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except:
                self.stats = {"total_memories": 0, "created": str(datetime.now())}
        else:
            self.stats = {"total_memories": 0, "created": str(datetime.now())}
    
    def save_stats(self):
        """Save memory statistics"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Failed to save stats: {e}")
    
    def _count_real_docs(self):
        """Count real documents (excluding dummy ones)"""
        try:
            count = 0
            if hasattr(self.vstore.docstore, '_dict'):
                # For InMemoryDocstore
                for doc in self.vstore.docstore._dict.values():
                    if not doc.metadata.get("temp", False):
                        count += 1
            elif hasattr(self.vstore.docstore, 'search'):
                # Alternative access method
                try:
                    # Try to get all doc IDs
                    for doc_id in self.vstore.index_to_docstore_id.values():
                        doc = self.vstore.docstore.search(doc_id)
                        if doc and not doc.metadata.get("temp", False):
                            count += 1
                except:
                    pass
            return count
        except Exception as e:
            print(f"Error counting docs: {e}")
            return 0
    
    def _get_real_docs(self):
        """Get all real documents (excluding dummy ones)"""
        try:
            real_docs = []
            if hasattr(self.vstore.docstore, '_dict'):
                # For InMemoryDocstore
                for doc in self.vstore.docstore._dict.values():
                    if not doc.metadata.get("temp", False):
                        real_docs.append(doc)
            elif hasattr(self.vstore.docstore, 'search'):
                # Alternative access method
                try:
                    for doc_id in self.vstore.index_to_docstore_id.values():
                        doc = self.vstore.docstore.search(doc_id)
                        if doc and not doc.metadata.get("temp", False):
                            real_docs.append(doc)
                except:
                    pass
            return real_docs
        except Exception as e:
            print(f"Error getting docs: {e}")
            return []
    
    def _create_new_store(self):
        """Create a new FAISS store with a dummy document"""
        try:
            print("Creating new memory store")
            
            # Create with a dummy document first (FAISS needs at least one document)
            dummy_doc = Document(
                page_content="This is a temporary initialization document", 
                metadata={"temp": True, "id": "dummy"}
            )
            
            self.vstore = FAISS.from_documents([dummy_doc], self.embed)
            print("✅ Created new empty memory store")
            
        except Exception as e:
            print(f"Error creating new store: {e}")
            raise

    def add_fact(self, fact: str, metadata: dict | None = None):
        """Add a new fact to memory"""
        try:
            if not fact.strip():
                return False
            
            # Add timestamp and unique ID to metadata
            if metadata is None:
                metadata = {}
            metadata.update({
                "timestamp": str(datetime.now()),
                "source": "conversation",
                "id": str(uuid.uuid4())
            })
            
            # Create document
            doc = Document(page_content=fact.strip(), metadata=metadata)
            
            # Check if this is the first real document
            real_count = self._count_real_docs()
            
            if real_count == 0:
                # Replace the dummy document with the first real one
                self.vstore = FAISS.from_documents([doc], self.embed)
            else:
                # Add to existing store
                self.vstore.add_documents([doc])
            
            # Save immediately
            self.vstore.save_local(str(self.path))
            
            # Update stats
            new_count = self._count_real_docs()
            self.stats["total_memories"] = new_count
            self.stats["last_updated"] = str(datetime.now())
            self.save_stats()
            
            print(f"💾 Remembered: {fact[:50]}... (Total: {new_count})")
            return True
            
        except Exception as e:
            print(f"Failed to add memory: {e}")
            import traceback
            traceback.print_exc()
            return False

    def recall(self, query: str, k=5) -> list[str]:
        """Retrieve relevant memories"""
        try:
            # Check if store has any real documents
            real_count = self._count_real_docs()
            
            if real_count == 0:
                print("🧠 No memories stored yet")
                return []
            
            # Use similarity search instead of retriever for more control
            docs_and_scores = self.vstore.similarity_search_with_score(query, k=k*2)
            
            # Filter out dummy documents and get the best matches
            real_memories = []
            for doc, score in docs_and_scores:
                if not doc.metadata.get("temp", False):
                    real_memories.append(doc.page_content)
                if len(real_memories) >= k:
                    break
            
            if real_memories:
                print(f"🔍 Recalled {len(real_memories)} relevant memories")
                # For demonstration, show what was recalled
                for i, memory in enumerate(real_memories, 1):
                    print(f"  {i}. {memory[:60]}...")
            else:
                print("🧠 No relevant memories found")
            
            return real_memories
            
        except Exception as e:
            print(f"Memory recall failed: {e}")
            return []

    def get_all_memories(self) -> list[dict]:
        """Get all stored memories with metadata"""
        try:
            all_memories = []
            real_docs = self._get_real_docs()
            
            for doc in real_docs:
                all_memories.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            return all_memories
        except Exception as e:
            print(f"Failed to retrieve all memories: {e}")
            return []

    def search_memories(self, query: str, k=10) -> list[dict]:
        """Search memories and return with similarity scores"""
        try:
            real_count = self._count_real_docs()
            
            if real_count == 0:
                return []
            
            # Use similarity search with scores
            docs_and_scores = self.vstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_and_scores:
                # Skip dummy documents
                if not doc.metadata.get("temp", False):
                    results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": float(score)
                    })
            
            return results
            
        except Exception as e:
            print(f"Memory search failed: {e}")
            return []

    def get_memory_stats(self) -> dict:
        """Get memory statistics"""
        current_count = self._count_real_docs()
        self.stats["current_memories"] = current_count
        return self.stats

    def flush(self):
        """Save memory to disk"""
        try:
            self.vstore.save_local(str(self.path))
            self.save_stats()
            real_count = self._count_real_docs()
            print(f"💾 Memory saved ({real_count} memories)")
        except Exception as e:
            print(f"Failed to save memory: {e}")