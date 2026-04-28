import json
from typing import Iterator

import requests
import urllib3

from .settings import SplunkConfig


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def send_to_splunk(data: dict, config: SplunkConfig) -> None:
    """Send one AI insight event to Splunk HEC."""
    headers = {"Authorization": f"Splunk {config.hec_token}"}
    payload = {
        "event": data,
        "index": config.index,
        "sourcetype": "_json",
    }

    response = requests.post(
        config.hec_url,
        json=payload,
        headers=headers,
        verify=False,
        timeout=15,
    )
    response.raise_for_status()


def stream_splunk_search_results(config: SplunkConfig) -> Iterator[dict]:
    """Yield streaming search result objects from Splunk real-time export API."""
    export_url = f"{config.rest_url}/services/search/jobs/export"
    search_params = {
        "search": config.search_query,
        "output_mode": "json",
        "earliest_time": "rt",
        "latest_time": "rt",
        "search_mode": "realtime",
    }

    response = requests.post(
        export_url,
        auth=(config.username, config.password),
        data=search_params,
        verify=False,
        stream=True,
        timeout=60,
    )
    response.raise_for_status()

    for line in response.iter_lines():
        if not line:
            continue

        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue

        result = parsed.get("result")
        if result:
            yield result
