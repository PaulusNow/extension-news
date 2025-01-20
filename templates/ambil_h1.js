try {
  const pElements = document.querySelectorAll("p");
  const pTexts = Array.from(pElements).map(p => p.textContent);
  pTexts.length > 0 ? pTexts : ["Tidak ada <p> ditemukan."];
} catch (error) {
  console.error("Error di content script:", error.message);
}
