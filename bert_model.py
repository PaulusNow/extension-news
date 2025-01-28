import torch
from transformers import BertTokenizer, BertForSequenceClassification

class BertModel:
    def __init__(self, token):
        self.token = token
        # Load the tokenizer and model from the new pretrained model
        self.tokenizer = BertTokenizer.from_pretrained('indobenchmark/indobert-base-p1', use_auth_token=self.token)
        self.model = BertForSequenceClassification.from_pretrained('indobenchmark/indobert-base-p1', use_auth_token=self.token)
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
                input_ids = torch.tensor([chunk])
                outputs = self.model(input_ids)
                logits = outputs.logits
                predictions.append(torch.argmax(logits, dim=1).item())

        # Voting mechanism
        final_prediction = max(set(predictions), key=predictions.count)
        return final_prediction
