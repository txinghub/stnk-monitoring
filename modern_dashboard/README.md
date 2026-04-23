# Modern STNK Dashboard (Port 8087 & 8099)

Dashboard monitoring STNK dan Pajak kendaraan dengan desain modern TIDAL-style.

## 🎨 Fitur Utama

- **Desain Premium**: TIDAL-style dengan dark/light mode
- **Animasi Smooth**: Transisi dan efek visual modern
- **Responsive**: Optimal di semua device (desktop, tablet, mobile)
- **Export Data**: Download data dalam format CSV
- **Real-time Updates**: Data diperbarui otomatis
- **Multi-dashboard**: Portal semua link di satu tempat

## 🚀 Dashboard yang Tersedia

### 1. Dashboard Modern (Port 8087)
- **URL**: http://100.121.49.116:8087
- **Fitur**: Dashboard utama dengan semua fitur premium
- **Design**: TIDAL-style dengan dark/light mode toggle

### 2. Dashboard Portal (Port 8099)
- **URL**: http://100.121.49.116:8099
- **Fitur**: Portal semua dashboard links
- **Kegunaan**: Satu halaman untuk semua akses dashboard

### 3. Dashboard Lengkap (Port 8085)
- **URL**: http://100.121.49.116:8085
- **Fitur**: Dashboard lengkap dengan Bootstrap 5
- **Catatan**: Versi lengkap dengan semua fitur

## 📁 File Penting

- `server.py` - Server untuk dashboard modern (port 8087)
- `simple_server_8099.py` - Server untuk dashboard portal (port 8099)
- `index.html` - Dashboard utama (port 8087)
- `portal.html` - Portal semua links (port 8099)
- `script.js` - JavaScript logic
- `data.json` - Data kendaraan
- `send_all_links.sh` - Script kirim link via WhatsApp

## 🛠️ Menjalankan Dashboard

### Dashboard Modern (8087):
```bash
cd /root/stnk_monitoring/modern_dashboard
python3 server.py
```

### Dashboard Portal (8099):
```bash
cd /root/stnk_monitoring/modern_dashboard
python3 simple_server_8099.py
```

## 📱 Kirim Link via WhatsApp

Kirim semua link dashboard ke WhatsApp:
```bash
cd /root/stnk_monitoring/modern_dashboard
bash send_all_links.sh
```

## 🔐 Keamanan

- Semua dashboard hanya bisa diakses via Tailscale VPN
- IP Tailscale: `100.121.49.116`
- Domain Tailscale: `openclaw-hermes.ts.net`
- Hanya nomor yang diizinkan yang bisa menerima link

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