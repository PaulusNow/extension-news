# Deteksi Hoax Menggunakan BERT

## Deskripsi
Proyek ini mengimplementasikan sistem deteksi hoax menggunakan model BERT yang telah dilatih sebelumnya. Model ini mengklasifikasikan artikel berita sebagai hoax atau valid berdasarkan teks input.

## Instalasi
Untuk menjalankan proyek ini, Anda perlu menginstal Python beserta paket-paket berikut:
- torch
- transformers

Anda dapat menginstal paket yang diperlukan menggunakan pip:

```bash
pip install torch transformers
```

## Model Indobert
Anda dapat mendownload model [di sini](https://drive.google.com/drive/folders/1C-fA8jzozmfB0Ixy-zyuN2c2W8zb7vP0?usp=sharing).

## Penggunaan
1. Impor kelas `BertModel` dari `bert_model.py`.
2. Inisialisasi model dengan token Hugging Face Anda.
3. Gunakan metode `predict` untuk mengklasifikasikan artikel berita.

Contoh:
```python
from bert_model import BertModel

# Inisialisasi model dengan token Hugging Face Anda
model = BertModel(token='your_huggingface_token')

# Prediksi apakah berita adalah hoax atau valid
result = model.predict("Teks artikel berita Anda di sini.")
print("Prediksi:", "Hoax" if result == 1 else "Valid")
```

## Detail Model
- **Model yang Digunakan**: indobenchmark/indobert-base-p1
- **Fungsi**: Model ini memproses teks input, memprediksi klasifikasi, dan menggunakan mekanisme voting untuk prediksi akhir.

## Lisensi
Proyek ini dilisensikan di bawah Lisensi MIT.
