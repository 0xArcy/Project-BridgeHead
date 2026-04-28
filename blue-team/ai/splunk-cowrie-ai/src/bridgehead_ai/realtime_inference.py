import json
import time

import requests
import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

from .settings import SplunkConfig
from .splunk_client import send_to_splunk, stream_splunk_search_results
from .training import LABEL_MAP


def _score_command(model, tokenizer, command_text: str, device):
    """Return (predicted_label, confidence_pct) for one command string."""
    inputs = tokenizer(command_text, return_tensors="pt", truncation=True, padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_idx = torch.argmax(logits, dim=1).item()
        confidence = torch.softmax(logits, dim=1).max().item()

    return LABEL_MAP.get(predicted_idx, "unknown"), round(confidence * 100, 2)


def run_continuous_reader(model_path: str, config: SplunkConfig) -> None:
    """Continuously stream Cowrie logs from Splunk, score them, and push AI insights back."""
    print(f"Loading model from {model_path}...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path, num_labels=3)
    model.to(device)
    model.eval()

    print("Model initialized. Starting streaming loop...")

    while True:
        try:
            for result in stream_splunk_search_results(config):
                raw_event = result.get("_raw", "")
                if not raw_event:
                    continue

                try:
                    cowrie_event = json.loads(raw_event)
                except json.JSONDecodeError:
                    continue

                if cowrie_event.get("eventid") != "cowrie.command.input":
                    continue

                command_text = cowrie_event.get("input", "")
                if not command_text:
                    continue

                predicted_label, confidence = _score_command(model, tokenizer, command_text, device)
                ai_insight = {
                    "source_event": cowrie_event,
                    "model": "distilbert-base-uncased-finetuned",
                    "predicted_threat_label": predicted_label,
                    "confidence": confidence,
                    "analyzed_command": command_text,
                    "timestamp": cowrie_event.get("timestamp"),
                }

                send_to_splunk(ai_insight, config)
                print(f"[AI] {command_text} -> {predicted_label} ({confidence}%)")

        except requests.exceptions.RequestException as exc:
            print(f"Splunk connection error: {exc}")
            print("Retrying in 10 seconds...")
            time.sleep(10)
