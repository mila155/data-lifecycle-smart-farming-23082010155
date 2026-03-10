# 🌱 Data Lifecycle Management — Soil Moisture IoT Dashboard

🚀 **Live Dashboard:** https://appapppy-5tkqstyqsbtvlqiqby7grx.streamlit.app/

---

**Nama:** Jamila Farhana
**NIM:** 23082010155
**Mata Kuliah:** Data Lifecycle Management

---

## 📋 Deskripsi Proyek

Proyek ini mengimplementasikan konsep **Data Lifecycle Management** secara end-to-end menggunakan dataset sensor kelembaban tanah dari perangkat IoT. Seluruh siklus hidup data dicakup mulai dari akuisisi, penyimpanan, pemrosesan, analisis, visualisasi, hingga tata kelola data (governance).

Dataset yang digunakan adalah **Soil Moisture Dataset** dari Kaggle yang berisi rekaman sensor kelembaban tanah dari tiga pot tanaman yang dimonitor secara real-time, merepresentasikan skenario **Smart Village** — monitoring pertanian berbasis sensor IoT.

🔗 **Dataset:** [kaggle.com/datasets/amirmohammdjalili/soil-moisture-dataset](https://www.kaggle.com/datasets/amirmohammdjalili/soil-moisture-dataset)

---

## 🗂️ Struktur Repository

```
repo_github/
├── README.md                                          
├── data/
│   └── raw/
│       ├── plant_vase1.CSV                            
│       ├── plant_vase1(2).CSV                         
│       └── plant_vase2.CSV                            
├── data_lifecycle_soil_moisture_23082010155.ipynb     
├── dashboard/
│   └── streamlit_app.py                               
└── outputs/
    ├── cleaned_data.csv                               
    ├── analysis_report.pdf                           
    └── dashboard_screenshot.png                      
```

---

## 📊 Dataset

| Atribut | Detail |
|---|---|
| Sumber | Kaggle — amirmohammdjalili/soil-moisture-dataset |
| Format | CSV (3 file terpisah) |
| Jumlah sensor | 5 sensor kelembaban per pot (moisture0–moisture4) |
| Frekuensi | Rekaman time series per detik/menit |

**Tiga file CSV:**
- `plant_vase1.CSV` — Pot 1A berisi tanah dan bunga (periode pertama)
- `plant_vase1(2).CSV` — Pot 1B berisi tanah dan bunga (periode kedua / pengukuran ulang)
- `plant_vase2.CSV` — Pot 2 berisi tanah saja, digunakan sebagai kontrol

**Kolom utama:**

| Kolom | Keterangan |
|---|---|
| `moisture0`–`moisture4` | Nilai kelembaban di 5 kedalaman sensor (0 = paling dangkal) |
| `year`, `month`, `day`, `hour`, `minute`, `second` | Komponen waktu pengukuran |
| `irrgation` | Status irigasi (True/False) saat pengukuran berlangsung |

---

## 🔄 Tahapan Data Lifecycle

### 1. Perkenalan Dataset
Menjelaskan konteks dataset, asal-usul data, tiga pot yang digunakan, serta kolom-kolom utama yang akan dianalisis.

### 2. Import Library
Library yang digunakan: `numpy`, `pandas`, `matplotlib`, `seaborn`, `kagglehub`, dan `warnings`.

### 3. Data Loading
Dataset diunduh dari Kaggle menggunakan `kagglehub` API. File `kaggle.json` digunakan untuk autentikasi, kemudian ketiga file CSV diload, diberi label kolom `source`, dan digabung menjadi satu DataFrame `df_all`.

### 4. Exploratory Data Analysis (EDA)
- Melihat sampel data (`head`), tipe data (`info`), dan statistik deskriptif (`describe`)
- Mengecek missing values dan duplikat
- Visualisasi distribusi nilai moisture per sensor (histogram)
- Deteksi outlier menggunakan metode IQR per sensor

### 5. Data Preprocessing
- **Handling missing values** — diisi dengan median per grup `source` agar tidak bias
- **Menghapus duplikat** — berdasarkan kombinasi kolom `datetime` + `source`
- **Parsing datetime** — kolom year/month/day/hour/minute/second digabung menjadi satu kolom `datetime`
- **Rename kolom** — typo `irrgation` diperbaiki menjadi `irrigation`
- **Export** — hasil preprocessing disimpan sebagai `outputs/cleaned_data.csv`

### 6. Data Analysis
- Statistik deskriptif per sensor (mean, std, min, max)
- Perbandingan rata-rata moisture antar pot
- Persentase frekuensi irigasi aktif per pot
- Heatmap korelasi antar sensor per pot
- Rata-rata moisture per sensor vs kondisi pot (bar chart)
- Time series tren kelembaban `moisture0`–`moisture4` per CSV

### 7. Data Governance & Data Quality Score
Tiga dimensi kualitas data dihitung secara kuantitatif:

| Dimensi | Formula |
|---|---|
| **Accuracy** | `1 − (jumlah missing / total data)` |
| **Completeness** | `baris non-null / total baris` |
| **Timeliness** | `% data dalam 30 hari terakhir dari tanggal maksimum` |
| **Overall DQS** | Rata-rata ketiga dimensi di atas |

## 🛠️ Dependencies

```
pandas
numpy
matplotlib
seaborn
plotly
streamlit
```

---

## 📈 Fitur Dashboard

- **Filter** sumber sensor, rentang waktu (harian/mingguan/bulanan/custom), dan sensor yang ditampilkan
- **Threshold** kelembaban yang bisa disesuaikan via slider
- **Alert system** otomatis merah jika kondisi kering (di bawah threshold)
- **Log alert** 8 kejadian kering terbaru
- **Gauge meter** per pot untuk kondisi terkini
