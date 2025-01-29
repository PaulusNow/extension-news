document.addEventListener("DOMContentLoaded", function () {
  const startButton = document.getElementById("start-button");
  const hiddenLink = document.getElementById("hidden-link");
  const buttonText = document.getElementById("button-text"); // Ambil elemen teks tombol
  const spinner = document.getElementById("spinner"); // Ambil elemen spinner

  if (startButton && hiddenLink && buttonText && spinner) {
    startButton.addEventListener("click", function (event) {
      event.preventDefault();

      // Sembunyikan teks "Mulai" dan tampilkan spinner
      buttonText.classList.add("visually-hidden");
      spinner.classList.remove("visually-hidden");

      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentUrl = tabs[0].url; // Dapatkan URL saat ini

        fetch('http://localhost:5000/get_content', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ url: currentUrl })
        })
        .then(response => {
          if (!response.ok) {
            return response.json().then(err => { throw err; });
          }
          return response.json();
        })
        .then(data => {
          if (data.status === "success") {
            console.log("Data berhasil diambil");
            hiddenLink.style.display = "block"; // Tampilkan link tersembunyi

            // Ambil prediksi dari `/get_content`
            const predictionResult = data.data.prediction === 'hoax' ? 'Hoax' : 'Valid';
            alert(`Prediction: ${predictionResult}`);
          } else {
            throw new Error(data.error || "Unknown error occurred");
          }
        })
        .catch(error => {
          console.error('Error fetching content:', error);
          alert(`Error: ${error.message}`);
        })
        .finally(() => {
          // Kembalikan teks "Mulai" dan sembunyikan spinner
          buttonText.classList.remove("visually-hidden");
          spinner.classList.add("visually-hidden");
        });
      });
    });
  }
});
