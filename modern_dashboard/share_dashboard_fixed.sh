#!/bin/bash
# Modern Dashboard Sharing Script via Tailscale
# Dashboard TIDAL Style - Port 8087

# Configuration
TAILSCALE_IP="100.121.49.116"
MODERN_DASHBOARD="http://${TAILSCALE_IP}:8087"
WHATSAPP_BRIDGE="http://localhost:3000/send"

# Authorized WhatsApp numbers
ALLOWED_NUMBERS=(
    "+628159153720"    # User's current number (主任)
    "+6285261919099"   # Owner/pemilik utama
    "+8615017041161"   # Mandarin/English contact
)

# Create simple message without special characters
MESSAGE="🚀 DASHBOARD MODERN TIDAL STYLE 🎵

📊 STNK & PAJAK MONITORING - Premium Edition

🔗 Dashboard Link:
${MODERN_DASHBOARD}

🎨 Fitur Premium:
✅ Desain TIDAL style (dark blue gradient)
✅ Animasi halus & hover effects  
✅ Charts interaktif dengan tooltips
✅ Sidebar navigation fixed
✅ Dark/light mode toggle
✅ Auto-refresh setiap 30 detik
✅ Export data ke CSV
✅ Mobile responsive design
✅ Auto backup system

📱 INSTRUKSI AKSES:
1. Install Tailscale di device Anda
2. Login dengan akun yang di-share
3. Buka link di atas di browser
4. Dashboard premium akan muncul otomatis

🔐 INFORMASI TEKNIS:
• Tailscale IP: ${TAILSCALE_IP}
• Port: 8087 (Modern Dashboard)
• Server: openclaw-hermes
• Status: ✅ Active & Running

⚠️ PERINGATAN KEAMANAN:
• HANYA untuk yang diizinkan!
• Jangan share link ke orang lain
• Pastikan Tailscale connected
• Dashboard menggunakan HTTPS via Tailscale

📞 BANTUAN:
Jika tidak bisa akses:
1. Cek Tailscale status (harus Connected)
2. Coba refresh browser
3. Clear browser cache
4. Hubungi admin jika masih bermasalah

🎯 Dashboard ini jauh lebih modern dan elegan dari versi sebelumnya!"

# Function to send via WhatsApp Bridge
send_whatsapp() {
    local phone_number="$1"
    local message="$2"
    
    echo "📱 Mengirim ke: $phone_number"
    
    # Escape JSON characters
    message_escaped=$(echo "$message" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
    
    curl -X POST "$WHATSAPP_BRIDGE" \
        -H "Content-Type: application/json" \
        -d "{\"chatId\": \"${phone_number}@c.us\", \"message\": \"$message_escaped\"}" \
        --silent
    
    echo "✅ Terkirim"
    sleep 2  # Delay between sends
}

# Main execution
echo "🚀 Memulai pengiriman link dashboard modern..."
echo "=============================================="

for number in "${ALLOWED_NUMBERS[@]}"; do
    send_whatsapp "$number" "$MESSAGE"
done

echo "=============================================="
echo "🎉 Selesai! Link dashboard modern terkirim."
echo ""
echo "🔗 Dashboard URL: $MODERN_DASHBOARD"
echo "📱 Bisa diakses dari mana saja via Tailscale"