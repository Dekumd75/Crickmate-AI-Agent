import os
import re
# You must run: pip install pypdf
from pypdf import PdfReader 

class RagEngine:
    def __init__(self):
        # 1. Find the Library Folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.kb_path = os.path.join(base_dir, "knowledge_base")
        
        self.library = {}
        self._load_library()

    def _load_library(self):
        """Reads all .txt and .pdf files from the knowledge_base folder."""
        if not os.path.exists(self.kb_path):
            print(f"[RAG] ❌ Warning: Library folder not found at {self.kb_path}")
            return

        print(f"[RAG] 📚 Loading Library from: {self.kb_path}...")

        for filename in os.listdir(self.kb_path):
            file_path = os.path.join(self.kb_path, filename)
            
            # --- CASE A: TEXT FILES ---
            if filename.endswith(".txt"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.library[filename] = f.read()
                    print(f"[RAG] ✅ Loaded Book: {filename}")
                except Exception as e:
                    print(f"[RAG] ⚠️ Error reading {filename}: {e}")

            # --- CASE B: PDF FILES ---
            elif filename.endswith(".pdf"):
                try:
                    reader = PdfReader(file_path)
                    text_content = ""
                    # Merge all pages into one text block
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_content += extracted + "\n"
                    
                    self.library[filename] = text_content
                    print(f"[RAG] ✅ Loaded PDF: {filename}")
                except Exception as e:
                    print(f"[RAG] ⚠️ Error reading PDF {filename}: {e}")

    def search(self, query):
        """
        Searches the library for keywords and returns the most relevant paragraphs.
        """
        query_words = query.lower().split()
        found_chunks = []

        # Search every book in the library
        for filename, content in self.library.items():
            
            # Simple scoring: How many keywords appear in this book?
            if any(word in content.lower() for word in query_words):
                
                # Find the best match position
                # (We look for the first occurrence of the main keyword)
                index = -1
                for word in query_words:
                    if len(word) > 3: # Ignore small words like 'the', 'how'
                        idx = content.lower().find(word)
                        if idx != -1:
                            index = idx
                            break
                
                if index != -1:
                    # Grab 1000 characters of context around the keyword
                    start = max(0, index - 300)
                    end = min(len(content), index + 1000)
                    snippet = content[start:end].replace("\n", " ")
                    
                    found_chunks.append(f"\n📘 SOURCE: {filename}\n...{snippet}...\n")

        if not found_chunks:
            return None

        # Return top 3 results
        return "\n".join(found_chunks[:3])