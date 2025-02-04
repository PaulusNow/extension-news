from flask import Flask, jsonify, request, render_template
import requests
from bs4 import BeautifulSoup
import logging
import re
import codecs
from bert_model import BertHoaxClassifier

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load model
model_path = "models/IndoBERT-Hoax-Detection.pth"
bert_model = BertHoaxClassifier(model_path)

# Fungsi-fungsi helper tetap sama
def decode_unicode_escapes(text):
    try:
        return codecs.decode(text, 'unicode_escape')
    except Exception as e:
        logging.error(f"Error decoding unicode escapes: {e}")
        return text

def clean_content(text):
    text = decode_unicode_escapes(text)
    unwanted_phrases = ["ADVERTISEMENT SCROLL TO CONTINUE WITH CONTENT"]
    for phrase in unwanted_phrases:
        text = text.replace(phrase, "")
    text = re.sub(r'[“"]?⚠️⚠️\s*PERHATIAN!!\s*⚠️⚠️', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_content', methods=['POST'])
def get_content():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url or not re.match(r'https?://[^\s]+', url):
            return jsonify({"error": "URL tidak valid"}), 400

        logging.info(f"Memproses URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Tidak ada judul"
        
        # Ekstraksi konten
        content = None
        if 'detik.com' in url:
            content = (
                soup.find('div', class_='detail__body-text itp_bodycontent') or
                soup.find('div', class_='detail__body flex-grow min-w-0 font-helvetica text-lg itp_bodycontent')
            )
        elif 'kompas.com' in url:
            content = soup.find('div', class_='col-bs9-7')
        elif 'cnnindonesia.com' in url:
            content = soup.find('div', class_='detail-wrap flex gap-4 relative')
        elif 'turnbackhoax.id' in url:
            content = soup.find('div', class_='entry-content mh-clearfix')
        else:
            return jsonify({"error": "URL tidak didukung"}), 400

        if not content:
            return jsonify({"error": "Konten tidak ditemukan"}), 404

        # Ekstraksi teks
        span_pf = content.find('span', string=re.compile("Pemeriksaan Fakta", re.IGNORECASE))
        if span_pf:
            subsequent_elements = span_pf.find_all_next()
            paragraphs = [
                element.get_text(strip=True)
                for element in subsequent_elements if element.name in ['p', 'strong', 'span']
            ]
            body_content = " ".join(paragraphs)
        else:
            paragraphs = content.find_all(['p', 'strong'])
            body_content = " ".join(p.text for p in paragraphs)

        # Pembersihan dan prediksi
        cleaned_content = clean_content(body_content)
        prediction_result = bert_model.predict(cleaned_content)
        
        response_data = {
            "data": {
                "title": title,
                "content": cleaned_content,
                "url": url,
                "prediction": prediction_result['prediction'].lower(),
                "confidence": round(prediction_result['confidence'] * 100, 2)
            },
            "status": "success"
        }

        return jsonify(response_data)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": "Gagal mengambil URL"}), 500
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": "Terjadi kesalahan server"}), 500

if __name__ == '__main__':
    app.run(debug=True)
