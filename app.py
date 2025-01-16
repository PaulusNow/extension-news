import requests
from bs4 import BeautifulSoup

# URL artikel
url = "https://news.detik.com/berita/d-7735714/terekam-cctv-begini-aksi-maling-bobol-mobil-artis-yuki-kato-di-bogor"

# Ambil konten HTML dari URL
response = requests.get(url)

if response.status_code == 200:  # Pastikan request berhasil
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Ambil judul artikel
    title = soup.find('h1').text
    print("Judul Artikel:", title)

    # Ambil isi artikel (contoh: semua paragraf di dalam div dengan class 'article-content')
    content = soup.find('div', class_='detail__body-text itp_bodycontent')
    paragraphs = content.find_all('p') if content else []

    print("Isi Artikel:")
    for p in paragraphs:
        print(p.text)
else:
    print(f"Gagal mengambil halaman. Status code: {response.status_code}")
