# YOLO Safety Detection Dashboard

Dashboard web untuk deteksi keselamatan menggunakan model YOLOv12 dengan 4 kelas: **no helmet**, **no jacket**, **safe**, dan **unsafe**.

## 🚀 Fitur

- **Upload Gambar**: Drag & drop atau klik untuk upload gambar
- **Upload Video**: Upload dan proses video dengan deteksi objek
- **Live Streaming**: Deteksi real-time menggunakan kamera
- **Confidence Threshold**: Atur threshold confidence untuk deteksi
- **Deteksi Real-time**: Deteksi objek menggunakan model YOLOv12
- **Visualisasi Hasil**: Tampilkan bounding box dan label pada gambar/video
- **Statistik Real-time**: Dashboard statistik dengan update otomatis
- **Reset Functionality**: Reset statistik dan bersihkan file dengan satu klik
- **Responsive Design**: Tampilan yang responsif untuk desktop dan mobile
- **Modern UI**: Interface yang modern dan user-friendly

## 📋 Kelas Deteksi

| Kelas | Deskripsi | Warna |
|-------|-----------|-------|
| `no helmet` | Tidak menggunakan helm | Merah |
| `no jacket` | Tidak menggunakan jaket | Orange |
| `safe` | Kondisi aman | Hijau |
| `unsafe` | Kondisi tidak aman | Magenta |

## 🛠️ Instalasi

### Prerequisites

- Python 3.8 atau lebih baru
- Model YOLO (`best.pt`) sudah dilatih

### Langkah Instalasi

1. **Clone atau download project ini**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Pastikan model YOLO ada di folder `model/`**
   ```
   model/
   └── best.pt
   ```

4. **Jalankan aplikasi**
   ```bash
   python app.py
   ```

5. **Buka browser dan akses**
   ```
   http://localhost:5000
   ```

## 📁 Struktur Project

```
├── app.py                 # Flask application utama
├── requirements.txt       # Python dependencies
├── README.md             # Dokumentasi
├── model/
│   └── best.pt           # Model YOLO yang sudah dilatih
├── templates/
│   └── dashboard.html    # Template HTML dashboard
├── static/
│   ├── style.css         # CSS styling
│   └── script.js         # JavaScript functionality
├── uploads/              # Folder untuk file upload (auto-created)
└── results/              # Folder untuk hasil deteksi (auto-created)
```

## 🔧 Konfigurasi

### Mengubah Port
Edit file `app.py` pada baris terakhir:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Ganti port sesuai kebutuhan
```

### Mengubah Ukuran File Maksimal
Edit di `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### Mengubah Kelas Deteksi
Edit di `app.py`:
```python
CLASSES = ['no helmet', 'no jacket', 'safe', 'unsafe']
```

## 🎯 Cara Penggunaan

### Image Detection
1. **Upload Gambar**
   - Drag & drop gambar ke area upload, atau
   - Klik area upload untuk memilih file

2. **Atur Confidence Threshold**
   - Gunakan slider untuk mengatur threshold confidence (0-100%)

3. **Deteksi**
   - Klik tombol "Deteksi" setelah memilih gambar
   - Tunggu proses deteksi selesai

4. **Lihat Hasil**
   - Hasil deteksi akan ditampilkan dengan bounding box
   - Daftar deteksi akan muncul di sidebar
   - Statistik akan terupdate otomatis

### Video Detection
1. **Upload Video**
   - Pilih tab "Video Detection"
   - Drag & drop video atau klik untuk memilih file
   - Format yang didukung: MP4, AVI, MOV, MKV, WMV, FLV

2. **Process Video**
   - Atur confidence threshold
   - Klik "Process Video" untuk memulai processing
   - Video hasil akan disimpan di folder results

### Live Streaming
1. **Start Stream**
   - Pilih tab "Live Stream"
   - Klik "Start Stream" untuk memulai deteksi real-time
   - Pastikan kamera terhubung dan diizinkan

2. **Stop Stream**
   - Klik "Stop Stream" untuk menghentikan streaming

## 📊 API Endpoints

### POST `/upload`
Upload dan deteksi gambar
- **Input**: Form data dengan field `file` dan `confidence_threshold`
- **Output**: JSON dengan hasil deteksi dan gambar base64

### POST `/video-inference`
Upload dan deteksi video
- **Input**: Form data dengan field `video` dan `confidence_threshold`
- **Output**: JSON dengan hasil deteksi dan preview gambar

### GET `/stream`
Halaman streaming real-time
- **Output**: HTML page untuk live streaming

### GET `/video_feed`
Video streaming endpoint
- **Output**: MJPEG stream dari kamera dengan deteksi

### POST `/reset`
Reset statistik dan bersihkan file
- **Output**: JSON dengan status reset

### GET `/stats`
Mendapatkan statistik real-time
- **Output**: JSON dengan statistik deteksi

### GET `/results/<filename>`
Serve hasil deteksi
- **Output**: Gambar/video hasil deteksi

### GET `/uploads/<filename>`
Serve file upload
- **Output**: File upload original

## 🔍 Troubleshooting

### Error: "Failed to load model"
- Pastikan file `model/best.pt` ada
- Pastikan model kompatibel dengan ultralytics

### Error: "No module named 'ultralytics'"
- Install ultralytics: `pip install ultralytics`

### Error: "No module named 'cv2'"
- Install opencv: `pip install opencv-python`

### Performance Issues
- Gunakan GPU jika tersedia
- Kurangi ukuran gambar input
- Tutup aplikasi lain yang menggunakan GPU

## 🎨 Customization

### Mengubah Warna
Edit `CLASS_COLORS` di `app.py`:
```python
CLASS_COLORS = {
    'no helmet': (255, 0, 0),    # RGB values
    'no jacket': (255, 165, 0),
    'safe': (0, 255, 0),
    'unsafe': (255, 0, 255)
}
```

### Mengubah Styling
Edit file `static/style.css` untuk mengubah tampilan

### Mengubah Behavior
Edit file `static/script.js` untuk mengubah interaksi

## 📝 License

Project ini dibuat untuk tujuan edukasi dan pengembangan.

## 🤝 Contributing

Silakan buat pull request atau issue untuk kontribusi.

## 📞 Support

Jika ada pertanyaan atau masalah, silakan buat issue di repository ini.
