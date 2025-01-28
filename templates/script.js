document.addEventListener("DOMContentLoaded", function () {
  const startButton = document.getElementById("start-button");
  const hiddenLink = document.getElementById("hidden-link");
  const currentUrlElement = document.getElementById("current-url");
  const bodyContentElement = document.getElementById("itp_bodycontent");

  if (startButton && hiddenLink && currentUrlElement && bodyContentElement) {
    startButton.addEventListener("click", function (event) {
      event.preventDefault();
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentUrl = tabs[0].url;  // Get the current URL
        fetch('http://localhost:5000/get_content', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ url: currentUrl })
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          // Handle the response data
          console.log("Data berhasil diambil");
          hiddenLink.style.display = "block";

          // Send the body content for hoax detection
          const bodyContent = data.data.content; // Use the fetched content directly
          fetch('http://localhost:5000/detect_hoax', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: bodyContent })
          })
          .then(response => response.json())
          .then(data => {
            // Display the prediction result
            const predictionResult = data.prediction[0] === 1 ? 'Hoax' : 'Valid';
            alert(`Prediction: ${predictionResult}`);
          })
          .catch(error => console.error('Error:', error));
        })
        .catch(error => console.error('Error fetching content:', error));
      });
    });
  }
});
