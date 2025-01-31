import torch
from transformers import BertTokenizer, BertForSequenceClassification

class BertModel:
    def __init__(self, model_path):
        # Load the tokenizer
        self.tokenizer = BertTokenizer.from_pretrained('indobenchmark/indobert-base-p1')
        
        # Load the model architecture
        self.model = BertForSequenceClassification.from_pretrained('indobenchmark/indobert-base-p1', num_labels=2)
        
        # Load the trained weights
        self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))  
        self.model.eval()

    def preprocess_text(self, text):
        """Preprocess the input text into chunks of 512 tokens."""
        tokens = self.tokenizer.encode(text, truncation=False)
        chunks = [tokens[i:i + 512] for i in range(0, len(tokens), 512)]
        return chunks

    def predict(self, text):
        """Predict if the news is hoax or valid."""
        chunks = self.preprocess_text(text)
        predictions = []

        with torch.no_grad():
            for chunk in chunks:
                inputs = self.tokenizer(
                    text, 
                    padding="max_length", 
                    truncation=True, 
                    max_length=512, 
                    return_tensors="pt"
                )
                # Move inputs to the same device as the model
                for key in inputs:
                    inputs[key] = inputs[key].to(self.model.device)
                
                outputs = self.model(**inputs)
                logits = outputs.logits
                predictions.append(torch.argmax(logits, dim=1).item())

        # Voting mechanism
        final_prediction = max(set(predictions), key=predictions.count)
        return final_prediction