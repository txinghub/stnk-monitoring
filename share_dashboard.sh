#!/bin/bash
# Script untuk share dashboard link ke WhatsApp
# Simpan di: /root/stnk_monitoring/share_dashboard.sh

DASHBOARD_SIMPLE="http://100.121.49.116:8084"
DASHBOARD_COMPLETE="http://100.121.49.116:8085"
TAILSCALE_IP="100.121.49.116"

# Nomor WhatsApp yang diizinkan (dari memory)
ALLOWED_NUMBERS=(
    "+628****9099"
    "+628****0230"  
    "+628****3289"
    "+628159153720"
    "+861****1161"
)

# Function untuk kirim ke WhatsApp Bridge
send_whatsapp() {
    local phone_number="$1"
    local message="$2"
    
    echo "Mengirim ke: $phone_number"
    
    # Kirim via WhatsApp Bridge (port 3000)
    curl -X POST http://localhost:3000/send \
        -H "Content-Type: application/json" \
        -d "{
            \"chatId\": \"${phone_number}@c.us\",
            \"message\": \"$message\"
        }" 2>/dev/null
    
    echo ""
}

# Pesan yang akan dikirim
MESSAGE="📊 STNK MONITORING DASHBOARD

🔗 Dashboard Sederhana (Clean Design):
${DASHBOARD_SIMPLE}

📈 Dashboard Lengkap (Full Features):
${DASHBOARD_COMPLETE}

🔐 INSTRUKSI AKSES:
1. Pastikan device terinstall Tailscale
2. Login dengan akun yang di-share
3. Buka link di atas di browser
4. Dashboard akan muncul otomatis

📱 Tailscale IP: ${TAILSCALE_IP}
🕐 Link aktif selama server menyala

⚠️ HANYA untuk yang diizinkan!
Jika tidak bisa akses, pastikan Tailscale connected."

# Kirim ke semua nomor yang diizinkan
echo "Mengirim dashboard link ke WhatsApp..."
echo "======================================"

for number in "${ALLOWED_NUMBERS[@]}"; do
    # Ganti placeholder dengan nomor asli jika ada
    if [[ $number == *"****"* ]]; then
        echo "Skipping placeholder: $number"
        continue
    fi
    
    send_whatsapp "$number" "$MESSAGE"
    sleep 2  # Delay antar pengiriman
done

echo "======================================"
echo "Selesai mengirim link dashboard!"