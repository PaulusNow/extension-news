import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class BertHoaxClassifier:
    def __init__(self, model_path, device="cpu"):
        self.device = torch.device(device)
        
        # Inisialisasi model dan tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "indobenchmark/indobert-base-p1", 
            num_labels=2
        )
        
        # Muat weights dengan weights_only=True untuk keamanan
        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device, weights_only=True)
        )
        self.model.to(self.device)
        self.model.eval()

        # Konfigurasi
        self.max_length = 512  # Harus sama dengan saat training
        self.chunk_size = 510

    def clean_text(self, text):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text.lower().strip()


    def chunk_text(self, text):
        """Membagi teks menjadi chunk dengan batasan token"""
        cleaned_text = self.clean_text(text)
        tokens = self.tokenizer.tokenize(cleaned_text)
        
        # Split tokens menjadi chunk dengan overlap 20%
        chunks = []
        for i in range(0, len(tokens), self.chunk_size - int(0.2*self.chunk_size)):
            chunk = tokens[i:i+self.chunk_size]
            chunks.append(self.tokenizer.convert_tokens_to_string(chunk))
        return chunks

    def predict(self, text):
        """Prediksi dengan handling teks panjang"""
        if not text.strip():
            return "Invalid input"
            
        chunks = self.chunk_text(text)
        if not chunks:
            return "No valid content"
            
        predictions = []
        confidence_scores = []

        with torch.no_grad():
            for chunk in chunks:
                inputs = self.tokenizer(
                    chunk,
                    padding="max_length",
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt"
                ).to(self.device)
                
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=1)
                predictions.append(torch.argmax(probs).item())
                confidence_scores.append(probs.max().item())

        # Weighted voting berdasarkan confidence score
        hoax_score = sum(cs for p, cs in zip(predictions, confidence_scores) if p == 1)
        valid_score = sum(cs for p, cs in zip(predictions, confidence_scores) if p == 0)
        
        return {
            'prediction': 'Hoax' if hoax_score > valid_score else 'Valid',
            'confidence': max(hoax_score, valid_score) / len(chunks),
            'chunks_processed': len(chunks)
        }

    def __call__(self, text):
        return self.predict(text)