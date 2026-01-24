TEXT_GENERATION_TIERS = [
    "chat",
    "reasoner",
]

MODEL_CONFIGURATIONS = {
    "chat": {
        "model": "deepseek-chat",
        "pricing": {
            "input": 0.14,
            "cached": 0.014,
            "output": 0.28,
        },
        "timeout": 360.0,
    },
    "reasoner": {
        "model": "deepseek-reasoner",
        "pricing": {
            "input": 0.14,
            "cached": 0.014,
            "output": 0.28,
            "reasoning_output": 0.28,
        },
        "timeout": 600.0,
    },
}

API_KEY_ENVIRONMENT_VARIABLE_NAME = "DEEPSEEK_API_KEY"
BASE_URL = "https://api.deepseek.com/v1"
