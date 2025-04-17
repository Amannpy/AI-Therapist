import os

port = int(os.environ.get("PORT", 5000))  # Render sets this PORT env var

app.run(host="0.0.0.0", port=port, debug=True)
