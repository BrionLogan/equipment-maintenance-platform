import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.api.validation import validate_request


class MaintenanceHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/requests":
            self.send_json(404, {"error": "Route not found"})
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )

            if content_length < 1 or content_length > 10000:
                self.send_json(
                    400,
                    {"error": "Body must be 1–10000 bytes"},
                )
                return

            body = self.rfile.read(content_length)
            request = json.loads(body)

        except (ValueError, UnicodeDecodeError):
            self.send_json(
                400,
                {"error": "Body must contain valid JSON"},
            )
            return

        if not isinstance(request, dict):
            self.send_json(
                400,
                {"error": "Body must be a JSON object"},
            )
            return

        errors = validate_request(request)

        if errors:
            self.send_json(400, {"errors": errors})
            return

        item = {
            "request_id": str(uuid4()),
            "equipment_id": request["equipment_id"].strip(),
            "description": request["description"].strip(),
            "priority": request["priority"],
            "status": "submitted",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            table = boto3.resource(
                "dynamodb",
                region_name="us-east-1",
            ).Table("maintenance-requests-lab")

            table.put_item(Item=item)

            sqs = boto3.client("sqs", region_name="us-east-1")

            queue_url = sqs.get_queue_url(
                QueueName="maintenance-requests-queue-lab"
            )["QueueUrl"]

            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    "request_id": item["request_id"]
                }),
            )

        except (BotoCoreError, ClientError) as error:
            self.log_error(
                "Failed to save maintenance request: %s",
                type(error).__name__,
            )
            self.send_json(
                503,
                {"error": "Unable to save request; try again later"},
            )
            return

        self.send_json(
            201,
            {
                "message": "Maintenance request saved",
                "request": item,
            },
        )

    def do_GET(self):
        prefix = "/requests/"

        if not self.path.startswith(prefix):
            self.send_json(404, {"error": "Route not found"})
            return

        request_id = self.path[len(prefix):]

        if not request_id or "/" in request_id:
            self.send_json(400, {"error": "Provide one request ID"})
            return

        try:
            table = boto3.resource(
                "dynamodb",
                region_name="us-east-1",
            ).Table("maintenance-requests-lab")

            response = table.get_item(
                Key={"request_id": request_id},
                ConsistentRead=True,
            )

        except (BotoCoreError, ClientError) as error:
            self.log_error(
                "Failed to retrieve maintenance request: %s",
                type(error).__name__,
            )
            self.send_json(
                503,
                {"error": "Unable to retrieve request; try again later"},
            )
            return

        item = response.get("Item")

        if item is None:
            self.send_json(404, {"error": "Request not found"})
            return

        self.send_json(200, {"request": item})

    def send_json(self, status, data):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MaintenanceHandler)
    print("Local API running on port 8000", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local API")
    finally:
        server.server_close()