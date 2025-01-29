from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import logging
import json
import re
from bert_model import BertModel

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load the BERT model
token = "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"
bert_model = BertModel(token)

@app.route('/get_content', methods=['POST'])
def get_content():
    try:
        # Parse JSON payload
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "URL parameter is required"}), 400

        logging.debug(f"Fetching content from URL: {url}")

        # Fetch HTML content
        response = requests.get(url)
        response.raise_for_status()
        html = response.text

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "No title found"

        if 'detik.com' in url:
            content = soup.find('div', class_='detail__body-text itp_bodycontent')
        elif 'kompas.com' in url:
            content = soup.find('div', class_='col-bs9-7')
        elif 'cnnindonesia.com' in url:
            content = soup.find('div', class_='detail-wrap flex gap-4 relative')
        else:
            return jsonify({"error": "Unsupported URL. Please provide a detik.com or kompas.com URL."}), 400

        paragraphs = content.find_all('p') if content else []
        body_content = " ".join(p.text for p in paragraphs)

        # Clean up the body content
        body_content = re.sub(r'\s+', ' ', body_content).strip()

        # Predict using the BERT model
        prediction = bert_model.predict(body_content)
        logging.debug(f"Prediction value: {prediction}")
        prediction_label = 'hoax' if prediction == 1 else 'valid'

        # Prepare response
        response_data = {
            "data": {
                "title": title,
                "content": body_content,
                "url": url,
                "prediction": prediction_label
            },
            "status": "success"
        }

        print(json.dumps(response_data, indent=4))
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
