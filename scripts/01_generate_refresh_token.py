"""
Genera el refresh_token OAuth para acceder a Google Ads API.
Corre una sola vez. El token resultante va en .env.

Uso:
    cd google-ads-cli-toolkit
    source .venv/bin/activate
    python scripts/01_generate_refresh_token.py CLIENT_ID CLIENT_SECRET
"""
import sys
import urllib.parse
import webbrowser
import http.server
import socketserver
import requests
import threading

SCOPES = ["https://www.googleapis.com/auth/adwords"]
REDIRECT_URI = "http://localhost:8765"
PORT = 8765

received_code = {"value": None}


class CodeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        code = params.get("code", [None])[0]
        received_code["value"] = code
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = "Listo. Volvé a la terminal." if code else "Falló."
        self.wfile.write(f"<h1>{msg}</h1>".encode("utf-8"))

    def log_message(self, *_):
        pass


def main():
    if len(sys.argv) != 3:
        print("Uso: python 01_generate_refresh_token.py CLIENT_ID CLIENT_SECRET")
        sys.exit(1)
    client_id, client_secret = sys.argv[1], sys.argv[2]

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": REDIRECT_URI,
                "scope": " ".join(SCOPES),
                "access_type": "offline",
                "prompt": "consent",
            }
        )
    )

    print(f"Abriendo navegador para autorizar...")
    print(f"Si no se abre, copia esta URL: {auth_url}")

    server = socketserver.TCPServer(("", PORT), CodeHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(auth_url)

    while received_code["value"] is None:
        pass
    server.shutdown()

    code = received_code["value"]
    print("Code recibido. Intercambiando por refresh_token...")

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )
    resp.raise_for_status()
    data = resp.json()

    print()
    print("=" * 60)
    print("REFRESH TOKEN (guárdalo en .env como GOOGLE_ADS_REFRESH_TOKEN):")
    print()
    print(data.get("refresh_token", "ERROR: no se obtuvo refresh_token"))
    print("=" * 60)


if __name__ == "__main__":
    main()
