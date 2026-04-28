import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


@dataclass
class SplunkConfig:
    rest_url: str
    username: str
    password: str
    search_query: str
    hec_url: str
    hec_token: str
    index: str

    def missing_required(self) -> List[str]:
        missing: List[str] = []
        required_fields = {
            "rest_url": self.rest_url,
            "username": self.username,
            "password": self.password,
            "search_query": self.search_query,
            "hec_url": self.hec_url,
            "hec_token": self.hec_token,
        }
        for key, value in required_fields.items():
            if not value.strip():
                missing.append(key)
        return missing


def load_splunk_config() -> SplunkConfig:
    """Load Splunk connection settings from environment variables."""
    load_dotenv()

    return SplunkConfig(
        rest_url=os.getenv("SPLUNK_REST_URL", ""),
        username=os.getenv("SPLUNK_USERNAME", ""),
        password=os.getenv("SPLUNK_PASSWORD", ""),
        search_query=os.getenv("SPLUNK_SEARCH_QUERY", ""),
        hec_url=os.getenv("SPLUNK_HEC_URL", ""),
        hec_token=os.getenv("SPLUNK_HEC_TOKEN", ""),
        index=os.getenv("SPLUNK_INDEX", "main"),
    )
