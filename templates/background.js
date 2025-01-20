chrome.action.onClicked.addListener(() => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const currentUrl = tabs[0].url;
    console.log("URL Tab Aktif: " + currentUrl);
  });
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("Ekstensi terinstal!");
});

chrome.action.onClicked.addListener((tab) => {
  if (tab.id) {
    chrome.scripting.executeScript(
      {
        target: { tabId: tab.id },
        files: ["templates/ambil_h1.js"], // Jalankan content script
      },
      (results) => {
        if (chrome.runtime.lastError) {
          console.error("Error saat eksekusi:", chrome.runtime.lastError.message);
        } else {
          console.log("Hasil:", results[0]?.result);
        }
      }
    );
  } else {
    console.error("Tab ID tidak valid");
  }
});

