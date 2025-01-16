document.addEventListener("DOMContentLoaded", function () {
    const startButton = document.getElementById("start-button");
    const hiddenLink = document.getElementById("hidden-link");
    const currentUrlElement = document.getElementById("current-url");

    // Cek apakah elemen ada
    if (startButton && hiddenLink && currentUrlElement) {
      startButton.addEventListener("click", function (event) {
        event.preventDefault(); // Mencegah default aksi klik tombol

        // Mengambil URL tab aktif menggunakan API ekstensi Chrome
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          const currentUrl = tabs[0].url; // Ambil URL tab aktif
          currentUrlElement.textContent = `URL Website: ${currentUrl}`; // Tampilkan URL

          // Tampilkan elemen link
          hiddenLink.style.display = "block";
        });
      });
    }
  });