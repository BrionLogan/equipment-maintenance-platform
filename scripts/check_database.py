from datetime import datetime, timezone
from uuid import uuid4

import boto3


def main():
    table = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
    ).Table("maintenance-requests-lab")

    item = {
        "request_id": str(uuid4()),
        "equipment_id": "GEN-101",
        "description": "Generator will not start",
        "priority": "high",
        "status": "submitted",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    table.put_item(Item=item)
    print("Saved request:", item["request_id"])

    response = table.get_item(
        Key={"request_id": item["request_id"]},
        ConsistentRead=True,
    )

    saved_item = response.get("Item")

    if saved_item != item:
        raise RuntimeError("Retrieved record does not match saved request")

    print("Retrieved request:", saved_item)
    print("Database check passed")


if __name__ == "__main__":
    main()