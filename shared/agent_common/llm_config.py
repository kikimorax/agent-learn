"""Shared configuration loaded on demand from the shared/.env and environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values

# Installed in editable mode by each stage.
DEFAULT_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


@dataclass(frozen=True)
class LLMSettings:
    base_url: str
    model: str
    api_key: str | None = None

    @property
    def local_gateway(self) -> bool:
        """Whether the gateway uses one of the supported loopback hosts."""
        return urlsplit(self.base_url).hostname in ("127.0.0.1", "localhost", "::1")

    @classmethod
    def from_environment(
        cls, *, env_file: str | Path | None = DEFAULT_ENV_FILE
    ) -> LLMSettings:
        """Read fresh settings; environment wins. None disables .env loading."""
        values = (
            dict(dotenv_values(env_file, encoding="utf-8-sig"))
            if env_file is not None else {}
        )
        values.update(os.environ)
        base_url = (values.get("LLM_BASE_URL") or "").strip().rstrip("/")
        model = (values.get("LLM_MODEL") or "").strip()
        api_key = (values.get("LLM_API_KEY") or "").strip() or None

        missing = [
            name
            for name, value in (("LLM_BASE_URL", base_url), ("LLM_MODEL", model))
            if not value
        ]
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"缺少环境变量：{names}。请参考仓库根目录 .env.example。")

        return cls(base_url=base_url, model=model, api_key=api_key)

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
