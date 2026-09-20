"""Runtime configuration for FixLens."""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    nebius_api_key: str
    nebius_base_url: str
    vision_model: str
    pinecone_api_key: str
    pinecone_index_name: str
    pinecone_namespace: str

    @property
    def vision_ready(self) -> bool:
        return bool(self.nebius_api_key and self.vision_model)

    @property
    def pinecone_ready(self) -> bool:
        return bool(self.pinecone_api_key and self.pinecone_index_name)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        nebius_api_key=os.getenv("NEBIUS_API_KEY", ""),
        nebius_base_url=os.getenv(
            "NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"
        ),
        vision_model=os.getenv("NEBIUS_VISION_MODEL", ""),
        pinecone_api_key=os.getenv("PINECONE_API_KEY", ""),
        pinecone_index_name=os.getenv("PINECONE_INDEX_NAME", "fixlens-honda"),
        pinecone_namespace=os.getenv("PINECONE_NAMESPACE", "honda-mvp-v1"),
    )

