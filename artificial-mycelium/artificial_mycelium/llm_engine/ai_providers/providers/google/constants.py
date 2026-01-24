TEXT_GENERATION_TIERS = [
    "3-flash",
]

MODEL_CONFIGURATIONS = {
    "3-flash": {
        "model": "gemini-3-flash-preview",
        "pricing": {"input": 0.50, "output": 3.00},
        "timeout": 360.0,
    },
}

API_KEY_ENVIRONMENT_VARIABLE_NAME = "GOOGLE_API_KEY"
