import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class BertHoaxClassifier:
    def __init__(self, model_path, device="cpu"):
        self.device = torch.device(device)
        
        # Gunakan local_files_only untuk model yang sudah di-download
        self.tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
        
        # Load model dengan config yang sesuai
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "indobenchmark/indobert-base-p1",
            num_labels=2,
            trust_remote_code=True
        )
        
        # Load weights dengan pengecekan versi
        state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        
        self.model.to(self.device)
        self.model.eval()

        # Konfigurasi
        self.max_length = 512
        self.chunk_size = 510
        self.overlap_ratio = 0.2  # Parameter bisa diadjust

    def clean_text(self, text):
        """Pembersihan teks yang lebih hati-hati"""
        text = re.sub(r'[^\w\s]', ' ', text)  # Pertahankan karakter unicode
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()

    def chunk_text(self, text):
        """Optimasi chunking dengan sliding window"""
        cleaned_text = self.clean_text(text)
        tokens = self.tokenizer.tokenize(cleaned_text)
        
        chunk_step = int(self.chunk_size * (1 - self.overlap_ratio))
        chunks = []
        
        for i in range(0, len(tokens), chunk_step):
            chunk = tokens[i:i+self.chunk_size]
            chunks.append(self.tokenizer.convert_tokens_to_string(chunk))
            
            if i + self.chunk_size >= len(tokens):  # Hentikan jika mencapai akhir
                break
                
        return chunks

    def predict(self, text):
        """Prediksi dengan batch processing"""
        if not text.strip():
            return {"error": "Invalid input"}
            
        chunks = self.chunk_text(text)
        if not chunks:
            return {"error": "No valid content"}
            
        batch = self.tokenizer(
            chunks,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**batch)
            probs = torch.softmax(outputs.logits, dim=1)
        
        # Agregasi hasil dengan weighting
        hoax_conf = probs[:, 1].sum().item()
        valid_conf = probs[:, 0].sum().item()
        
        total_chunks = len(chunks)
        return {
            'prediction': 'Hoax' if hoax_conf > valid_conf else 'Valid',
            'confidence': max(hoax_conf, valid_conf) / total_chunks,
            'chunks_processed': total_chunks
        }
