"""Test which JSON Schema keys the Gemini API actually accepts/rejects."""

import os
import sys

from google import genai

API_KEY = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3-flash-preview"

BASE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
    },
    "required": ["name", "age"],
}

TEST_CASES = {
    "minimum": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0},
        },
        "required": ["name", "age"],
    },
    "maximum": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "maximum": 150},
        },
        "required": ["name", "age"],
    },
    "exclusiveMinimum": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "exclusiveMinimum": 0},
        },
        "required": ["name", "age"],
    },
    "exclusiveMaximum": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "exclusiveMaximum": 200},
        },
        "required": ["name", "age"],
    },
    "minLength": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    },
    "maxLength": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "maxLength": 100},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    },
    "pattern": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "pattern": "^[A-Za-z]+$"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    },
    "minItems": {
        "type": "object",
        "properties": {
            "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        },
        "required": ["tags"],
    },
    "maxItems": {
        "type": "object",
        "properties": {
            "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        },
        "required": ["tags"],
    },
    "uniqueItems": {
        "type": "object",
        "properties": {
            "tags": {"type": "array", "items": {"type": "string"}, "uniqueItems": True},
        },
        "required": ["tags"],
    },
    "minProperties": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
        "minProperties": 1,
    },
    "maxProperties": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
        "maxProperties": 5,
    },
    "title": {
        "type": "object",
        "title": "PersonInfo",
        "properties": {
            "name": {"type": "string", "title": "Name"},
            "age": {"type": "integer", "title": "Age"},
        },
        "required": ["name", "age"],
    },
    "default": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "default": "Unknown"},
            "age": {"type": "integer", "default": 0},
        },
        "required": ["name", "age"],
    },
}


def test_key(key_name, schema):
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents="Give me a fictional person.",
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema,
            },
        )
        return True, response.text[:80]
    except Exception as e:
        return False, str(e)[:120]


if __name__ == "__main__":
    print(f"Testing schema keys against {MODEL}...\n")
    print(f"{'Key':<20} {'Supported?':<12} {'Detail'}")
    print("-" * 80)

    for key_name, schema in TEST_CASES.items():
        ok, detail = test_key(key_name, schema)
        status = "YES" if ok else "NO"
        print(f"{key_name:<20} {status:<12} {detail}")

    print("\nDone.")
