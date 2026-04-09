schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "parameters": {"type": "object"},
        "return": {"type": "object"},
    },
    "required": ["name", "description", "parameters", "return"]
}
