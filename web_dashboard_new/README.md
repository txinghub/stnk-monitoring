# STNK Monitoring Dashboard

Dashboard modern untuk monitoring STNK dan Pajak kendaraan dengan fitur lengkap.

## Fitur Utama

✅ **Dashboard Modern** - Bootstrap 5 + Chart.js + DataTables  
✅ **Monitoring Real-time** - Status otomatis berdasarkan tanggal kadaluarsa  
✅ **Warna Status** - Hijau (aman), Kuning (peringatan), Merah (prioritas)  
✅ **Chart Visualisasi** - Pie chart distribusi status + Bar chart hari menuju jatuh tempo  
✅ **Update Setelah Bayar** - Form modal untuk update tanggal setelah bayar pajak  
✅ **Backup Otomatis** - Backup data sebelum update  
✅ **Responsive Design** - Tampilan optimal di desktop dan mobile  
✅ **API Lengkap** - Endpoint untuk data, stats, backups, dan update  

## Instalasi & Menjalankan

### 1. Clone atau salin folder
```bash
cd /root/stnk_monitoring/web_dashboard_new
```

### 2. Jalankan server
```bash
python3 server.py
```

### 3. Akses dashboard
Buka browser ke: http://localhost:8083

## Struktur File

```
web_dashboard_new/
├── index.html          # Halaman utama dashboard
├── script.js           # JavaScript utama
├── server.py           # Python backend server
├── data.json           # Data kendaraan
├── requirements.txt    # Dependencies
├── backups/            # Folder backup otomatis
└── server.log          # Log server
```

## API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/data` | GET | Data lengkap kendaraan |
| `/api/stats` | GET | Statistik dashboard |
| `/api/backups` | GET | List backup files |
| `/api/update` | POST | Update data kendaraan |

## Cara Update Setelah Bayar

1. Klik tombol **"UPDATE SETELAH BAYAR"** di navbar
2. Pilih kendaraan dari dropdown
3. Isi tanggal STNK dan Pajak baru
4. Tambahkan catatan (opsional)
5. Klik **"Update Data"**

Sistem akan:
- Update tanggal kadaluarsa
- Ubah status menjadi "AMAN" (hijau)
- Buat backup otomatis
- Update chart dan tabel

## Status Berdasarkan Hari

| Hari Menuju Jatuh Tempo | Status | Warna |
|-------------------------|--------|-------|
| > 90 hari | AMAN | Hijau |
| 31-90 hari | PERINGATAN | Kuning |
| ≤ 30 hari | PRIORITAS | Merah |

## Backup & Restore

### Backup Otomatis
Setiap update akan membuat backup di folder `backups/`

### Backup Manual
```bash
# Backup seluruh folder
tar -czf stnk_dashboard_backup_$(date +%Y%m%d_%H%M%S).tar.gz *

# Restore
tar -xzf stnk_dashboard_backup_*.tar.gz
```

## Troubleshooting

### Server tidak start
```bash
# Cek port 8083
sudo lsof -i :8083

# Kill process jika perlu
sudo kill -9 $(sudo lsof -t -i:8083)

# Start server
python3 server.py
```

### Data tidak muncul
```bash
# Cek format data.json
python3 -m json.tool data.json

# Cek log server
tail -f server.log
```

## Kontak & Support

Sistem ini dibuat untuk monitoring STNK & Pajak kendaraan. Untuk masalah teknis, pastikan:
1. Python 3.6+ terinstall
2. Port 8083 tidak digunakan
3. File data.json format JSON valid

---
**Versi**: 1.0  
**Terakhir Update**: April 2026  
**Developer**: Hermes Agent