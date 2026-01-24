TEXT_GENERATION_TIERS = [
    "5-nano",
    "5-mini-minimal",
    "5-mini-low",
    "5-mini",
    "5-mini-high",
    "5-minimal",
    "5-low",
    "5.1",
    "5.2",
    "5-high",
    "5-pro",
    "5.2-pro-medium",
    "5.2-pro-high",
    "5.2-pro-xhigh",
]

DEEP_RESEARCH_TIERS = [
    "o3-deep-research",
]

IMAGE_GENERATION_TIERS = [
    "gpt-image-1-mini",
    "gpt-image-1",
    "gpt-image-1.5",
]

MODEL_CONFIGURATIONS = {
    "5-nano": {"model": "gpt-5-nano", "pricing": {"input": 0.05, "output": 0.40}, "timeout": 360.0},
    "5-mini-minimal": {
        "model": "gpt-5-mini",
        "reasoning": {"effort": "minimal"},
        "pricing": {"input": 0.25, "output": 2.00},
        "timeout": 360.0,
    },
    "5-mini-low": {
        "model": "gpt-5-mini",
        "reasoning": {"effort": "low"},
        "pricing": {"input": 0.25, "output": 2.00},
        "timeout": 360.0,
    },
    "5-mini": {"model": "gpt-5-mini", "pricing": {"input": 0.25, "output": 2.00}, "timeout": 360.0},
    "5-mini-high": {
        "model": "gpt-5-mini",
        "reasoning": {"effort": "high"},
        "pricing": {"input": 0.25, "output": 2.00},
        "timeout": 360.0,
    },
    "5-minimal": {
        "model": "gpt-5",
        "reasoning": {"effort": "minimal"},
        "pricing": {"input": 1.25, "output": 10.00},
        "timeout": 360.0,
    },
    "5-low": {
        "model": "gpt-5",
        "reasoning": {"effort": "low"},
        "pricing": {"input": 1.25, "output": 10.00},
        "timeout": 360.0,
    },
    "5.1": {"model": "gpt-5.1", "pricing": {"input": 1.25, "output": 10.00}, "timeout": 600.0},
    "5.2": {"model": "gpt-5.2", "pricing": {"input": 1.75, "output": 14.00}, "timeout": 600.0},
    "5-high": {
        "model": "gpt-5",
        "reasoning": {"effort": "high"},
        "pricing": {"input": 1.25, "output": 10.00},
        "timeout": 1200.0,
    },
    "5-pro": {
        "model": "gpt-5-pro",
        "background": True,
        "pricing": {"input": 15.00, "output": 120.00},
        "timeout": 1800.0,
    },
    "5.2-pro-medium": {
        "model": "gpt-5.2-pro",
        "reasoning": {"effort": "medium"},
        "background": True,
        "pricing": {"input": 21.00, "output": 168.00},
        "timeout": 1800.0,
    },
    "5.2-pro-high": {
        "model": "gpt-5.2-pro",
        "reasoning": {"effort": "high"},
        "background": True,
        "pricing": {"input": 21.00, "output": 168.00},
        "timeout": 1800.0,
    },
    "5.2-pro-xhigh": {
        "model": "gpt-5.2-pro",
        "reasoning": {"effort": "xhigh"},
        "background": True,
        "pricing": {"input": 21.00, "output": 168.00},
        "timeout": 1800.0,
    },
    # Deep Research model - for comprehensive multi-source research reports
    "o3-deep-research": {
        "model": "o3-deep-research",
        "background": True,
        "pricing": {"input": 15.00, "output": 120.00},  # Estimated, adjust based on actual pricing
        "timeout": 3600.0,  # 1 hour - deep research can take 30+ minutes
    },
    "gpt-image-1-mini": {
        "model": "gpt-image-1-mini",
        "pricing": {
            "low": {
                "1024x1024": 0.005,
                "1024x1536": 0.006,
                "1536x1024": 0.006,
            },
            "medium": {
                "1024x1024": 0.011,
                "1024x1536": 0.015,
                "1536x1024": 0.015,
            },
            "high": {
                "1024x1024": 0.036,
                "1024x1536": 0.052,
                "1536x1024": 0.052,
            },
            "text_input": 2.00,
            "text_cached": 0.20,
            "image_input": 2.50,
            "image_cached": 0.25,
            "image_output": 8.00,
        },
        "timeout": 360.0,
    },
    "gpt-image-1": {
        "model": "gpt-image-1",
        "pricing": {
            "low": {
                "1024x1024": 0.011,
                "1024x1536": 0.016,
                "1536x1024": 0.016,
            },
            "medium": {
                "1024x1024": 0.042,
                "1024x1536": 0.063,
                "1536x1024": 0.063,
            },
            "high": {
                "1024x1024": 0.167,
                "1024x1536": 0.25,
                "1536x1024": 0.25,
            },
            "text_input": 5.00,
            "text_cached": 1.25,
            "image_input": 10.00,
            "image_cached": 2.50,
            "image_output": 40.00,
        },
        "timeout": 360.0,
    },
    "gpt-image-1.5": {
        "model": "gpt-image-1.5",
        "pricing": {
            "low": {
                "1024x1024": 0.009,
                "1024x1536": 0.013,
                "1536x1024": 0.013,
            },
            "medium": {
                "1024x1024": 0.034,
                "1024x1536": 0.05,
                "1536x1024": 0.05,
            },
            "high": {
                "1024x1024": 0.133,
                "1024x1536": 0.20,
                "1536x1024": 0.20,
            },
            "text_input": 5.00,
            "text_cached": 1.25,
            "image_input": 8.00,
            "image_cached": 2.00,
            "image_output": 32.00,
        },
        "timeout": 360.0,
    },
}

API_KEY_ENVIRONMENT_VARIABLE_NAME = "OPENAI_API_KEY"
