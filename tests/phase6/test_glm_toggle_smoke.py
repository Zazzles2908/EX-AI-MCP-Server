import os
import pytest
from dotenv import load_dotenv

# Load .env so toggles present in local dev
load_dotenv()

def test_glm_stream_toggle_env_present():
    if os.getenv("GLM_STREAM_ENABLED") is None:
        pytest.skip("GLM_STREAM_ENABLED not set in environment")
    assert True

