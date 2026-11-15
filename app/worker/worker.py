import json
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def main():
    sqs = boto3.client("sqs", region_name="us-east-1")

    table = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
    ).Table("maintenance-requests-lab")

    queue_url = sqs.get_queue_url(
        QueueName="maintenance-requests-queue-lab"
    )["QueueUrl"]

    print("Worker running. Press Control+C to stop.", flush=True)

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
        )

        for message in response.get("Messages", []):
            try:
                body = json.loads(message["Body"])
                request_id = body["request_id"]

                if not isinstance(request_id, str) or not request_id.strip():
                    raise ValueError("Message has an invalid request_id")

                result = table.get_item(
                    Key={"request_id": request_id},
                    ConsistentRead=True,
                )

                item = result.get("Item")

                if item is None:
                    raise ValueError("Request does not exist in DynamoDB")

                if item.get("status") != "completed":
                    print(f"Processing request: {request_id}", flush=True)

                    table.update_item(
                        Key={"request_id": request_id},
                        UpdateExpression=(
                            "SET #status = :completed, completed_at = :time"
                        ),
                        ConditionExpression="attribute_exists(request_id)",
                        ExpressionAttributeNames={
                            "#status": "status",
                        },
                        ExpressionAttributeValues={
                            ":completed": "completed",
                            ":time": datetime.now(timezone.utc).isoformat(),
                        },
                    )
                else:
                    print(f"Already completed: {request_id}", flush=True)

                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message["ReceiptHandle"],
                )

                print(f"Removed message: {request_id}", flush=True)

            except (
                BotoCoreError,
                ClientError,
                ValueError,
                KeyError,
                TypeError,
            ) as error:
                print(
                    f"Processing failed; message left for retry: {error}",
                    flush=True,
                )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWorker stopped")