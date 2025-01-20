from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/get_content', methods=['GET'])
def get_content():
    url = request.args.get('url')  # Get URL from query parameters
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    logging.debug(f"Fetching content from URL: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the URL: {e}")
        return jsonify({"error": str(e)}), 500

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title and content
        title = soup.find('h1').text
        content = soup.find('div', class_='detail__body-text itp_bodycontent')
        paragraphs = content.find_all('p') if content else []
        body_content = " ".join(p.text for p in paragraphs)

        return jsonify({
            "data": {
                "title": title,
                "content": body_content,
                "url": url  # Include the URL in the response
            },
            "status": "success"
        })
    else:
        return jsonify({
            "data": {},
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
