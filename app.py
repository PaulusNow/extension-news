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
        text = data.get('text', '')

        if not url:
            return jsonify({"error": "URL parameter is required"}), 400

        logging.debug(f"Fetching content from URL: {url}")

        # Fetch HTML content
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad HTTP responses
        html = response.text

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "No title found"
        content = soup.find('div', class_='detail__body-text itp_bodycontent')
        paragraphs = content.find_all('p') if content else []
        body_content = " ".join(p.text for p in paragraphs)

        # Clean up the body content
        body_content = body_content.replace('\\', '')  # Remove backslashes
        body_content = body_content.replace('ADVERTISEMENT', '')  # Remove unwanted phrases
        body_content = body_content.replace('SCROLL TO CONTINUE WITH CONTENT', '')  # Remove unwanted phrases
        body_content = body_content.replace('\r\n', '')  # Remove newline characters
        body_content = re.sub(r'\s+', ' ', body_content)  # Replace multiple spaces with a single space
        body_content = body_content.strip()  # Trim whitespace

        # Predict using the BERT model
        prediction = bert_model.predict(text)
        prediction_label = 'hoax' if prediction == 1 else 'valid'

        # Prepare the response data
        response_data = {
            "data": {
                "title": title,
                "content": body_content,
                "url": url,
                "prediction": prediction_label
            },
            "status": "success"
        }

        # Print the response data to the terminal
        print(json.dumps(response_data, indent=4))  # Pretty-print the JSON

        # Return the JSON response
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


@app.route('/detect_hoax', methods=['POST'])
def detect_hoax():
    try:
        data = request.get_json()
        content = data.get('content', '')

        # Perform prediction using the BERT model
        prediction = bert_model.predict(content)
        prediction_label = 'hoax' if prediction == 1 else 'valid'

        return jsonify({
            "prediction": prediction_label,
            "status": "success"
        })

    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return jsonify({"error": "Prediction failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
