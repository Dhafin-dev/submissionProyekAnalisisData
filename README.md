# E-Commerce Public Dataset Dashboard

Dashboard interaktif berbasis Streamlit untuk menganalisis performa penjualan kategori produk, pengaruh ketepatan pengiriman terhadap ulasan pelanggan, serta segmentasi pelanggan menggunakan metode RFM (*Recency, Frequency, Monetary*).

## Struktur Direktori
- `dashboard/`: Berisi script utama `dashboard.py` dan dataset bersih `main_data.csv`.
- `data/`: Berisi dataset mentah E-Commerce Public Dataset (`.csv`).
- `notebook.ipynb`: File Jupyter/Colab Notebook yang memuat seluruh proses analisis data.
- `requirements.txt`: Daftar library Python yang dibutuhkan untuk menjalankan proyek.

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.12
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
```bash
cd dashboard
streamlit run dashboard.py
```