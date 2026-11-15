def validate_request(request):
    errors = []

    equipment_id = request.get("equipment_id")

    if not isinstance(equipment_id, str) or not equipment_id.strip():
        errors.append("equipment_id must be a nonempty string")

    description = request.get("description")

    if not isinstance(description, str) or not description.strip():
        errors.append("description must be a nonempty string")

    priority = request.get("priority")

    if priority not in ("low", "medium", "high"):
        errors.append("priority must be low, medium, or high")

    return errors


if __name__ == "__main__":
    valid_request = {
        "equipment_id": "GEN-101",
        "description": "Generator will not start",
        "priority": "high"
    }

    invalid_request = {
        "equipment_id": "GEN-101",
        "description": "Generator will not start",
        "priority": "urgent"
    }

    print("Valid request:", validate_request(valid_request))
    print("Invalid request:", validate_request(invalid_request))