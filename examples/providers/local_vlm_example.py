"""VerifyIQ with Local VLM Provider.

Prerequisites:
    pip install verifyiq[api]
    # Install your local VLM (e.g., Ollama, llama.cpp, vLLM)
    # Run your local VLM server on localhost:8001

See code/v2/providers/local_vlm_provider.py for the full interface.
"""

import os

# No API key needed for local models
os.environ["VERIFYIQ_MODE"] = "production"

from code.v2.pipeline import V2Pipeline

pipeline = V2Pipeline(config={
    "providers": {
        "local": {
            "model": "qwen2.5-vl-7b",
            "base_url": "http://localhost:8001",
        },
    }
})

state = pipeline.vision_manager.state
print(f"Vision state: {state.value}")
if pipeline.providers:
    print(f"Provider: Local ({pipeline.providers[0].model_name})")
else:
    print("Local provider not available (is your VLM server running?)")
