#!/bin/bash
# Send All Dashboard Links via WhatsApp

TAILSCALE_IP="100.121.49.116"
WHATSAPP_BRIDGE="http://localhost:3000/send"

# Authorized numbers
ALLOWED_NUMBERS=(
    "+628159153720"    # User
    "+6285261919099"   # Owner
    "+8615017041161"   # Mandarin contact
)

MESSAGE="📊 **ALL STNK DASHBOARD LINKS** 📊

🚀 **DASHBOARD MODERN - TIDAL STYLE** (Premium)
🔗 http://${TAILSCALE_IP}:8087
🎨 Fitur: TIDAL design, animations, dark/light mode, export CSV

📱 **DASHBOARD PORTAL** (All Links)
🔗 http://${TAILSCALE_IP}:8099
📋 Semua link dalam satu halaman

⚡ **DASHBOARD SEDERHANA** (Clean Design)
🔗 http://${TAILSCALE_IP}:8084
✨ Versi simple untuk monitoring cepat

📈 **DASHBOARD LENGKAP** (Full Features)
🔗 http://${TAILSCALE_IP}:8085
🔧 Semua fitur: charts, tables, updates, backups

🔐 **INSTRUKSI AKSES:**
1. Install Tailscale di device
2. Login dengan akun yang di-share  
3. Pastikan status \"Connected\"
4. Buka link di browser

⚠️ **KEAMANAN:**
• HANYA untuk yang diizinkan!
• End-to-end encrypted via Tailscale
• Jangan share link ke orang lain

📞 **BANTUAN:**
• Tailscale IP: ${TAILSCALE_IP}
• Server: openclaw-hermes
• Jika tidak bisa akses, cek Tailscale status

🎯 **REKOMENDASI:**
Gunakan Dashboard Modern (port 8087) untuk pengalaman terbaik!"

# Function to send message
send_whatsapp() {
    local phone_number="$1"
    local message="$2"
    
    echo "📱 Sending to: $phone_number"
    
    # Escape JSON
    message_escaped=$(echo "$message" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
    
    curl -X POST "$WHATSAPP_BRIDGE" \
        -H "Content-Type: application/json" \
        -d "{\"chatId\": \"${phone_number}@c.us\", \"message\": \"$message_escaped\"}" \
        --silent
    
    echo "✅ Sent"
    sleep 2
}

# Main execution
echo "🚀 Sending all dashboard links..."
echo "================================="

for number in "${ALLOWED_NUMBERS[@]}"; do
    send_whatsapp "$number" "$MESSAGE"
done

echo "================================="
echo "🎉 All links sent successfully!"
echo ""
echo "📊 Dashboard Portal: http://${TAILSCALE_IP}:8099"
echo "🎨 Modern Dashboard: http://${TAILSCALE_IP}:8087"
echo "⚡ Simple Dashboard: http://${TAILSCALE_IP}:8084"
echo "📈 Complete Dashboard: http://${TAILSCALE_IP}:8085"