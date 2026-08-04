import os
from contextvars import ContextVar
from typing import Any

import yaml

request_llm_credentials: ContextVar[dict[str, str] | None] = ContextVar(
    "request_llm_credentials",
    default=None,
)


def set_llm_credentials(metadata: dict[str, Any] | None) -> None:
    use_llm_proxy = os.environ["USE_LLM_PROXY"]
    assert use_llm_proxy in {"true", "false"}
    if use_llm_proxy == "false":
        request_llm_credentials.set(None)
        return

    assert metadata is not None
    proxy_metadata = metadata["https://ichatbio.org/a2a/v1"]
    assert proxy_metadata["temporary_llm_key"] is not None, "temporary_llm_key is required but None was provided."
    assert proxy_metadata["ichatbio_base_url"] is not None, "ichatbio_base_url is required but None was provided."
    request_llm_credentials.set({
        "api_key": proxy_metadata["temporary_llm_key"],
        "base_url": f"{proxy_metadata['ichatbio_base_url'].rstrip('/')}/llm",
    })


def get_config_value(key: str, default: str = None) -> str:
    """Get configuration value from environment or env.yaml file"""
    value = os.getenv(key)
    if value:
        return value

    try:
        with open("env.yaml", "r") as f:
            config = yaml.safe_load(f) or {}
            return config.get(key, default)
    except FileNotFoundError:
        return default


def get_llm_credentials() -> dict[str, str]:
    credentials = request_llm_credentials.get()
    if credentials is not None:
        return credentials

    api_key = get_config_value("OPENAI_API_KEY")
    base_url = get_config_value("OPENAI_BASE_URL")
    assert api_key is not None, "OPENAI_API_KEY must be set"
    assert base_url is not None, "OPENAI_BASE_URL must be set"
    return {"api_key": api_key, "base_url": base_url}