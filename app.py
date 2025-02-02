from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import logging
import json
import re
import codecs  # Modul untuk melakukan decoding string
from bert_model import BertHoaxClassifier

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)  # Change to INFO for production

# Load the trained IndoBERT model
model_path = "models\Model_Bert\indobert_hoax_model.pth"
bert_model = BertHoaxClassifier(model_path)  # Initialize the BertModel

def decode_unicode_escapes(text):
    try:
        return codecs.decode(text, 'unicode_escape')
    except Exception as e:
        logging.error(f"Error decoding unicode escapes: {e}")
        return text

def clean_content(text):
    # Ubah escape sequence Unicode menjadi karakter asli
    text = decode_unicode_escapes(text)

    # Hapus frasa yang tidak diinginkan
    unwanted_phrases = [
        "ADVERTISEMENT SCROLL TO CONTINUE WITH CONTENT",
    ]
    for phrase in unwanted_phrases:
        text = text.replace(phrase, "")

    # Hapus bagian "⚠️⚠️ PERHATIAN!! ⚠️⚠️" (dengan atau tanpa tanda kutip di depannya)
    text = re.sub(r'[“"]?⚠️⚠️\s*PERHATIAN!!\s*⚠️⚠️', '', text)

    # Bersihkan spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/get_content', methods=['POST'])
def get_content():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url or not re.match(r'https?://[^\s]+', url):
            return jsonify({"error": "A valid URL parameter is required"}), 400

        logging.info(f"Fetching content from URL: {url}")

        response = requests.get(url)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "No title found"

        # Ekstrak konten berdasarkan website
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
            return jsonify({"error": "Unsupported URL. Please provide a detik.com, kompas.com, or cnnindonesia.com URL."}), 400

        if not content:
            return jsonify({"error": "Content tidak ditemukan pada halaman tersebut."}), 404

        # Cari elemen <span> yang mengandung teks "Pemeriksaan Fakta"
        span_pf = content.find('span', string=re.compile("Pemeriksaan Fakta", re.IGNORECASE))
        
        if span_pf:
            # Ambil seluruh konten (teks) setelah elemen <span> tersebut
            subsequent_elements = span_pf.find_all_next()
            paragraphs = [
                element.get_text(strip=True)
                for element in subsequent_elements if element.name in ['p', 'strong', 'span']
            ]
            body_content = " ".join(paragraphs)
        else:
            # Jika tidak ditemukan, ambil seluruh <p> dan <strong> seperti sebelumnya
            paragraphs = content.find_all(['p', 'strong'])
            body_content = " ".join(p.text for p in paragraphs)

        # Bersihkan konten
        body_content = clean_content(body_content)

        # Lakukan prediksi dengan model BERT
        prediction_result = bert_model.predict(body_content)
        prediction_label = prediction_result['prediction'].lower() 
        confidence = prediction_result['confidence'] 

        if confidence < 0.65:
            prediction_label = 'hoax'

        response_data = {
            "data": {
                "title": title,
                "content": body_content,
                "url": url,
                "prediction": prediction_label,
                "confidence": confidence
            },
            "status": "success"
        }

        logging.info(json.dumps(response_data, indent=4))
        return jsonify(response_data)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the URL: {e}")
        return jsonify({"error": f"Failed to fetch URL: {str(e)}"}), 500
    except json.JSONDecodeError:
        logging.error("Invalid JSON payload")
        return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
