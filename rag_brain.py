import ollama
import json
import os
import torch
from sentence_transformers import SentenceTransformer, util

class RAGBrain:
    def __init__(self, db):
        self.db = db
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧠 RAG Brain (Few-Shot) on {self.device}...")
        
        self.embedder = SentenceTransformer('BAAI/bge-small-en-v1.5', device=self.device)
        
        # Initial Load
        self.reload_index()

        try:
            ollama.chat(model='phi3:mini', messages=[{'role': 'user', 'content': 'hi'}])
            self.online = True
        except:
            self.online = False

    def reload_index(self):
        """
        Builds the vector database from (Merchant + Explanation).
        """
        self.knowledge = self.db.get_knowledge_base()
        if not self.knowledge:
            self.vectors = None
            return

        # THE CORE LOGIC: Embed the "Meaning", not just the name
        # Example: "Starbucks (Coffee and breakfast)"
        corpus = [f"{row['merchant']} ({row['explanation']})" for row in self.knowledge]
        
        self.vectors = self.embedder.encode(corpus, convert_to_tensor=True, device=self.device)
        print(f"✅ Vector DB Updated: {len(corpus)} entries.")

    def _load_prompt(self, filename, **kwargs):
        try:
            with open(os.path.join("prompts", filename), "r") as f:
                return f.read().format(**kwargs)
        except: return ""

    def retrieve_candidates(self, merchant_query, k=10):
        """
        1. Vector Search for similar past transactions.
        2. Return the LABELS associated with them.
        """
        if self.vectors is None: return []
        
        # Embed just the merchant description
        query_vec = self.embedder.encode(merchant_query, convert_to_tensor=True, device=self.device)
        
        scores = util.cos_sim(query_vec, self.vectors)[0]
        top_k = min(k, len(self.knowledge))
        
        results = torch.topk(scores, top_k)
        
        candidates = []
        for idx in results.indices:
            item = self.knowledge[idx]
            # Format: "Starbucks" was "Fast_Food"
            candidates.append(f"- Example: '{item['merchant']}' -> Label: {item['label']}")
            
        return candidates

    def process_transaction(self, merchant):
        if not self.online: return {"label": "System_Offline", "explanation": "Check Ollama"}

        # 1. Retrieve Top 10
        candidates = self.retrieve_candidates(merchant)
        candidates_str = "\n".join(candidates) if candidates else "None (No history)"
        
        # 2. Prompt
        prompt = self._load_prompt("rag_categorize.txt", merchant=merchant, candidates=candidates_str)
        
        # 3. LLM Inference
        try:
            res = ollama.chat(model='phi3:mini', messages=[{'role': 'user', 'content': prompt}])
            clean_json = res['message']['content'].replace("```json", "").replace("```", "").strip()
            start = clean_json.find('{')
            end = clean_json.rfind('}') + 1
            data = json.loads(clean_json[start:end])
            
            return {
                "label": data.get("label", "Unknown_Label"),
                "explanation": data.get("explanation", "AI Generated"),
                "status": "AI-Labeled"
            }
        except:
            return {"label": "Error_Label", "explanation": "JSON Parse Fail", "status": "Error"}

    def generate_advisory(self, df):
        if not self.online or df.empty: return "No Data"
        summary = df.groupby('Label')['Amount'].sum().to_string()
        prompt = self._load_prompt("advisory.txt", total_spend=df['Amount'].sum(), breakdown=summary)
        try:
            return ollama.chat(model='phi3:mini', messages=[{'role': 'user', 'content': prompt}])['message']['content']
        except: return "Advisory Error"