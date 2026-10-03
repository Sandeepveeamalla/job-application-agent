from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class AppConfig:
    job_board_api_key: str | None = None
    openai_api_key: str | None = None
    default_top_results: int = 5


def load_config() -> AppConfig:
    from dotenv import load_dotenv

    load_dotenv()

    return AppConfig(
        job_board_api_key=os.getenv("JOB_BOARD_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        default_top_results=5,
    )
