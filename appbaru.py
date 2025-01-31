import logging
import json
import re
from bert_model import BertModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load the trained IndoBERT model
model_path = "models/indobert_hoax_model.pth"  # Path to your .pth file
bert_model = BertModel(model_path)  # Initialize the BertModel

text = "Mahasiswi UNJ Meninggal Karena Kehabisan Oksigen Terkena Gas Air Mata"
text = "Mahasiswa UNJ meninggal karena kehabisan obat paracetamol dan kekurangan oksigen akibat gas kentut dan gas air mata."
# text = "Baru-baru ini beredar kabar bahwa pemerintah akan mengganti seluruh uang kertas Rupiah dengan mata uang digital pada akhir tahun ini tanpa pemberitahuan resmi. Masyarakat diimbau untuk segera menukarkan uang tunai mereka karena setelah tanggal 31 Desember 2025, seluruh uang kertas akan dianggap tidak berlaku. Informasi ini pertama kali muncul di beberapa grup WhatsApp dan telah dikonfirmasi oleh sumber anonim yang mengaku bekerja di Bank Indonesia."
prediction = bert_model.predict(text)
logging.debug(f"Prediction value: {prediction}")
prediction_label = 'hoax' if prediction == 1 else 'valid'

# Prepare response
response_data = {
    "data": {
        "text": text,
        "prediction": prediction_label
    },
    "status": "success"
}

print(json.dumps(response_data, indent=4))