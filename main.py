from flask import Flask, request, jsonify
import hashlib
import time
import requests
import os  # ✅ ضعه في الأعلى

# ✅ قراءة المتغيرات من بيئة Render
APP_KEY = os.environ.get("APP_KEY")
APP_SECRET = os.environ.get("APP_SECRET")
TRACKING_ID = os.environ.get("TRACKING_ID")

app = Flask(__name__)

# (اختياري) اطبع القيم للمراجعة (ثم احذفها لاحقًا بعد التأكد)
print("APP_KEY:", APP_KEY)
print("APP_SECRET:", APP_SECRET)
print("TRACKING_ID:", TRACKING_ID)

def sign(params):
    sorted_params = sorted(params.items())
    query_string = "".join(f"{k}{v}" for k, v in sorted_params)
    raw_string = APP_SECRET + query_string + APP_SECRET
    return hashlib.md5(raw_string.encode("utf-8")).hexdigest().upper()

@app.route("/generate", methods=["GET"])
def generate_affiliate_link():
    origin_url = request.args.get("url")
    if not origin_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    timestamp = str(int(time.time() * 1000))
    method = "aliexpress.affiliate.link.generate"

    params = {
        "app_key": APP_KEY,
        "method": method,
        "timestamp": timestamp,
        "format": "json",
        "v": "2.0",
        "sign_method": "md5",
        "tracking_id": TRACKING_ID,
        "promotion_link_type": "cm",
        "source_values": origin_url
    }

    signature = sign(params)
    params["sign"] = signature

    url = "https://api-sg.aliexpress.com/openapi/param2/2/portals.open/api.link.generate"
    response = requests.get(url, params=params)

    try:
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": "Failed to parse response", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
