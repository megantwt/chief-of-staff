"""Run ONCE on your own laptop to get a read-only Google Calendar refresh token for GitHub.

    python get_google_token.py YOUR_CLIENT_ID YOUR_CLIENT_SECRET

It opens Google's sign-in page; sign in with your personal Gmail and allow "See your calendars".
The refresh token is printed at the end: paste it into GitHub as the GOOGLE_REFRESH_TOKEN secret.
Only the calendar.readonly permission is requested, so the token can never change your calendar.
"""

import http.server
import json
import sys
import urllib.parse
import urllib.request
import webbrowser

SCOPE = "https://www.googleapis.com/auth/calendar.readonly"


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    client_id, client_secret = sys.argv[1], sys.argv[2]
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result["code"] = (q.get("code") or [None])[0]
            result["error"] = (q.get("error") or [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Done. You can close this tab and go back to the terminal.</h2>")

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{server.server_port}"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent"})
    print("Opening your browser. If it doesn't open, paste this link:\n" + url)
    webbrowser.open(url)
    server.handle_request()
    if not result.get("code"):
        sys.exit("No code received: " + str(result.get("error")))
    body = urllib.parse.urlencode({"code": result["code"], "client_id": client_id,
                                   "client_secret": client_secret, "redirect_uri": redirect,
                                   "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=body)) as r:
        tokens = json.loads(r.read().decode())
    print("\nYour refresh token (keep it secret; paste it into GitHub as GOOGLE_REFRESH_TOKEN):\n")
    print(tokens.get("refresh_token", "(none returned: remove the app at myaccount.google.com/permissions and run again)"))


if __name__ == "__main__":
    main()
