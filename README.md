# STNK Monitoring Dashboard System

Sistem monitoring STNK dan Pajak kendaraan dengan dua versi dashboard.

## 📊 Dashboard Versi

### 1. Dashboard Sederhana (Port 8084)
- **Design**: Modern, clean, card-based layout
- **Fitur**: Statistik, warna status, responsive design
- **Teknologi**: Pure HTML/CSS/JS + Python server
- **Link**: http://localhost:8084

### 2. Dashboard Lengkap (Port 8085) 
- **Design**: Professional dengan Bootstrap 5
- **Fitur**: Chart.js, DataTables, Update Modal, Backup otomatis
- **Teknologi**: Bootstrap 5, Chart.js, DataTables, Python API
- **Link**: http://localhost:8085

## 🚀 Instalasi & Menjalankan

### Dashboard Sederhana (8084):
```bash
cd web_dashboard_simple
python3 server.py
```

### Dashboard Lengkap (8085):
```bash
cd web_dashboard_new
python3 server.py
```

## 📁 Struktur Proyek

```
stnk_monitoring/
├── web_dashboard_simple/    # Dashboard sederhana (port 8084)
│   ├── server.py           # Python server
│   ├── data.json           # Data kendaraan
│   └── (single HTML file embedded)
├── web_dashboard_new/      # Dashboard lengkap (port 8085)
│   ├── server.py           # Python server dengan API
│   ├── index.html          # Dashboard utama
│   ├── script.js           # JavaScript logic
│   ├── data.json           # Data kendaraan
│   ├── requirements.txt    # Dependencies
│   └── README.md           # Dokumentasi
├── data/                   # Data source
├── csv_data/              # CSV exports
├── extracted_data/        # Excel source
└── config.json            # Konfigurasi
```

## 🔧 API Endpoints

### Dashboard Lengkap (8085):
- `GET /api/data` - Data kendaraan lengkap
- `GET /api/stats` - Statistik dashboard
- `GET /api/backups` - List backup files
- `POST /api/update` - Update data kendaraan

### Dashboard Sederhana (8084):
- `GET /` - Halaman utama dengan data
- `GET /api/data` - Data JSON

## 📊 Data Structure

```json
{
  "id": 1,
  "merk": "HONDA CS 1",
  "no_polisi": "BK 2302 WAM",
  "kategori": "Roda Dua",
  "stnk_date": "2026-05-06",
  "pajak_date": "2026-05-06",
  "ktp": "LINGGO THIO PUTRO",
  "status": "priority",
  "hari_menuju_jatuh_tempo": 16,
  "warna_status": "danger",
  "catatan": "STNK dan Pajak sama tanggal"
}
```

## 🎨 Status Colors

| Hari | Status | Warna | Ikon |
|------|--------|-------|------|
| > 90 | AMAN | Hijau | ✅ |
| 31-90 | PERINGATAN | Kuning | ⚠️ |
| ≤ 30 | PRIORITAS | Merah | ⛔ |

## 🔒 Backup & Maintenance

### Backup Otomatis:
- Setiap update membuat backup di folder `backups/`
- Format: `backup_YYYYMMDD_HHMMSS.json`

### Backup Manual:
```bash
tar -czf stnk_dashboard_backup_$(date +%Y%m%d_%H%M%S).tar.gz web_dashboard_simple/ web_dashboard_new/
```

## 📱 Akses dari Device Lain

```
Dashboard Sederhana: http://[SERVER_IP]:8084
Dashboard Lengkap:   http://[SERVER_IP]:8085
```

## 📝 Catatan

- Dashboard lama (port 8082) sudah dihapus total
- Kedua dashboard tidak boleh diubah bentuknya
- Backup reguler ke NAS diperlukan
- Data sensitif sudah di-ignore di .gitignore

## 👥 Kontribusi

Proyek ini dikelola oleh Hermes Agent untuk monitoring STNK & Pajak kendaraan.

---
**Versi**: 2.0  
**Update Terakhir**: 20 April 2026  
**Status**: Produksi Ready