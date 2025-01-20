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
        fetch(`http://localhost:5000/get_content?url=${encodeURIComponent(currentUrl)}`)
          .then(response => response.json())
          .then(data => {
            // Handle the response data
            currentUrlElement.textContent = `Teks H1: ${data.data.title}`;
            bodyContentElement.textContent = `Body Content: ${data.data.content}`;
            hiddenLink.style.display = "block";
          })
          .catch(error => console.error('Error:', error));
      });
    });
  }
});
