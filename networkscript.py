import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== CONFIG SECTION =====
# ⚠️ REPLACE THESE WITH YOUR GMAIL CREDENTIALS
GMAIL_SENDER = "eshotoye@gmail.com"          # ← Your Gmail address
GMAIL_APP_PASSWORD = "pyei qpzc lbce gnzm"  # ← Your 16-character App Password (WITH spaces)
GMAIL_RECEIVER = "eshotoye@gmail.com"        # ← Who should get alerts (can be same as sender)

# ===== MOCK DATA FOR TESTING (NO VCO NEEDED) =====
edges = [
    {"name": "NYC-Branch-01", "edgeState": "CONNECTED", "haState": "ACTIVE", "siteId": 101},
    {"name": "LON-Branch-02", "edgeState": "OFFLINE", "haState": "STANDBY", "siteId": 102},
    {"name": "SYD-Branch-03", "edgeState": "CONNECTED", "haState": "N/A", "siteId": 103},
    {"name": "SFO-Branch-04", "edgeState": "CONNECTED", "haState": "ACTIVE", "siteId": 104},
    {"name": "PAR-Branch-05", "edgeState": "OFFLINE", "haState": "N/A", "siteId": 105},
    {"name": "TKY-Branch-06", "edgeState": "CONNECTED", "haState": "STANDBY", "siteId": 106}
]

print("\n" + "="*60)
print("         VELOCLOUD EDGE HEALTH REPORT")
print("="*60)

# ✅ Initialize unhealthy_edges — always defined
unhealthy_edges = []

# 📊 Process each edge
for edge in edges:
    name = edge.get('name', 'Unknown')
    state = edge.get('edgeState', 'UNKNOWN')
    ha_state = edge.get('haState', 'N/A')
    site_id = edge.get('siteId', 'N/A')

    if state == "CONNECTED":
        status = "✅ HEALTHY"
    else:
        status = "❌ DOWN"
        unhealthy_edges.append(name)

    print(f"Edge: {name:<20} | Site: {site_id:<8} | Status: {status:<10} | HA: {ha_state}")

print("\n" + "-"*60)

# 💾 Save report to file if any edges are down
if unhealthy_edges:
    filename = "unhealthy_edges.txt"
    with open(filename, "w", encoding="utf-8") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"UNHEALTHY EDGES - GENERATED AT: {now}\n")
        f.write("="*50 + "\n")
        for edge in unhealthy_edges:
            f.write(edge + "\n")
    print(f"⚠️  ALERT: {len(unhealthy_edges)} edges are down. Saved to '{filename}'")
else:
    print("🎉 ALL EDGES ARE HEALTHY!")

print("\n✅ Report complete. No VCO connection required for mock mode.\n")

# 📧 EMAIL ALERT FUNCTION
def send_email_alert(down_edges_list):
    """Sends alert email via Gmail using App Password"""
    try:
        # Setup message
        msg = MIMEMultipart()
        msg['From'] = GMAIL_SENDER
        msg['To'] = GMAIL_RECEIVER
        msg['Subject'] = f"🚨 SD-WAN ALERT: {len(down_edges_list)} Edges Down!"

        body = f"""
Velocloud Edge Health Check found DOWN edges at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:

{chr(10).join(down_edges_list)}

Check 'unhealthy_edges.txt' for details.
"""
        msg.attach(MIMEText(body, 'plain'))

        # Connect and send
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # ⚠️ Remove spaces from App Password before login
        clean_password = GMAIL_APP_PASSWORD.replace(" ", "")
        server.login(GMAIL_SENDER, clean_password)

        text = msg.as_string()
        server.sendmail(GMAIL_SENDER, GMAIL_RECEIVER, text)
        server.quit()

        print("✅ 📧 Email alert sent successfully to", GMAIL_RECEIVER)

    except Exception as e:
        print(f"❌ EMAIL FAILED: {type(e).__name__}: {e}")
        print("➡️  TROUBLESHOOTING TIPS:")
        print("   1. Did you enable 2-Factor Auth on Gmail?")
        print("   2. Is the App Password exactly 16 characters?")
        print("   3. Did you use the correct Gmail account?")
        print("   4. Try generating a NEW App Password at:")
        print("      https://myaccount.google.com/apppasswords")

# 🚨 TRIGGER EMAIL IF ANY EDGES ARE UNHEALTHY
if unhealthy_edges:
    send_email_alert(unhealthy_edges)
else:
    print("📬 No email sent — all edges are healthy.")