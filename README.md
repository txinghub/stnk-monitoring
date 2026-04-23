# STNK Monitoring Dashboard System

Sistem monitoring STNK dan Pajak kendaraan dengan dashboard modern.

## 📊 Dashboard Versi

### 1. Dashboard Modern (Port 8087)
- **Design**: TIDAL-style premium dashboard
- **Fitur**: Dark/light mode, animations, export CSV, responsive
- **Teknologi**: Modern CSS, JavaScript, Python server
- **Link**: http://localhost:8087

### 2. Dashboard Portal (Port 8099)
- **Design**: Portal untuk semua dashboard links
- **Fitur**: Semua link dalam satu halaman
- **Link**: http://localhost:8099

## 🚀 Instalasi & Menjalankan

### Dashboard Modern (8087):
```bash
cd modern_dashboard
python3 server.py
```

### Dashboard Portal (8099):
```bash
cd modern_dashboard
python3 simple_server_8099.py
```

## 📁 Struktur Proyek

```
stnk_monitoring/
├── modern_dashboard/      # Dashboard modern (port 8087 & 8099)
│   ├── server.py           # Python server untuk 8087
│   ├── simple_server_8099.py # Python server untuk 8099
│   ├── index.html          # Dashboard utama
│   ├── portal.html         # Portal semua links
│   ├── script.js           # JavaScript logic
│   ├── data.json           # Data kendaraan
│   └── README.md           # Dokumentasi
├── data/                   # Data source
├── csv_data/              # CSV exports
├── extracted_data/        # Excel source
├── scripts/               # Utility scripts
└── config.json            # Konfigurasi sistem
```

## 🔧 API Endpoints

### Dashboard Modern (8087):
- `GET /` - Dashboard utama
- `GET /data` - Data kendaraan (JSON)
- `GET /export` - Export data ke CSV

### Dashboard Portal (8099):
- `GET /` - Portal semua dashboard links

## 📱 Fitur Utama

1. **Monitoring Real-time**: Pantau status STNK dan pajak kendaraan
2. **Notifikasi Warna**: Status berdasarkan waktu jatuh tempo
3. **Export Data**: Download data dalam format CSV
4. **Responsive Design**: Optimal di semua device
5. **Dark/Light Mode**: Toggle tema gelap/terang

## 🛠️ Teknologi

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.11 (http.server)
- **Design**: TIDAL-style, Bootstrap 5 components
- **Data**: JSON format dengan struktur terstandarisasi

## 🔐 Keamanan

- Semua dashboard hanya bisa diakses via Tailscale VPN
- IP Tailscale: `100.121.49.116`
- Domain Tailscale: `openclaw-hermes.ts.net`
- Data dienkripsi end-to-end via Tailscale

## 🆘 Troubleshooting

1. **Dashboard tidak bisa diakses**:
   - Pastikan Tailscale terhubung
   - Cek status server: `ss -tlnp | grep :8087`
   - Restart server jika perlu

2. **Data tidak muncul**:
   - Cek file `data.json` ada dan valid
   - Restart server untuk reload data

3. **WhatsApp link tidak terkirim**:
   - Pastikan WhatsApp Bridge berjalan di port 3000
   - Cek nomor yang diizinkan di script

## 📞 Kontak & Dukungan

- **Developer**: Hermes Agent
- **WhatsApp**: +628****3720 (User)
- **Owner**: +628****9099
- **Backup**: GitHub repo & NAS storage