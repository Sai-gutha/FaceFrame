from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("FACEFRAME_DATABASE_PATH", "faceframe.db")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "FACEFRAME_ALLOWED_ORIGINS",
            "http://localhost:3000,https://faceframe-customer-experience.guthaskarthik.chatgpt.site",
        ).split(",")
        if origin.strip()
    )
    session_days: int = int(os.getenv("FACEFRAME_SESSION_DAYS", "30"))


settings = Settings()
