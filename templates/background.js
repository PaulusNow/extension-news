chrome.action.onClicked.addListener(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const currentUrl = tabs[0].url;
      console.log("URL Tab Aktif: " + currentUrl);
    });
  });
  