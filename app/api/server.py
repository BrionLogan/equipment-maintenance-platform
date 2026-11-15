import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.api.validation import validate_request


class MaintenanceHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/requests":
            self.send_json(404, {"error": "Route not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))

            if content_length < 1 or content_length > 10000:
                self.send_json(400, {"error": "Body must be 1–10000 bytes"})
                return

            body = self.rfile.read(content_length)
            request = json.loads(body)

        except (ValueError, UnicodeDecodeError):
            self.send_json(400, {"error": "Body must contain valid JSON"})
            return

        if not isinstance(request, dict):
            self.send_json(400, {"error": "Body must be a JSON object"})
            return

        errors = validate_request(request)

        if errors:
            self.send_json(400, {"errors": errors})
            return

        self.send_json(200, {
            "message": "Request passed validation",
            "request": request,
        })

    def send_json(self, status, data):
        response = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MaintenanceHandler)
    print("Local API running at http://127.0.0.1:8000")
    server.serve_forever()