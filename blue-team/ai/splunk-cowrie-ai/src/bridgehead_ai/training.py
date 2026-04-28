import json
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizer,
    Trainer,
    TrainingArguments,
)


MODEL_NAME = "distilbert-base-uncased"
LABEL_MAP = {
    0: "recon_bot",
    1: "malware_dropper",
    2: "human_interactive",
}


def _infer_label_from_session_text(text: str) -> int:
    """Apply heuristic labels used to bootstrap model training."""
    malware_indicators = ["wget", "curl", "chmod +x", "./"]
    human_indicators = ["cd /etc", "cat passwd", ".ssh", "id_rsa", "ls -la"]

    if any(indicator in text for indicator in malware_indicators):
        return 1
    if any(indicator in text for indicator in human_indicators):
        return 2
    return 0


def load_cowrie_logs(file_paths: Iterable[str]) -> tuple[list[str], list[int]]:
    """Extract session command strings from Cowrie JSONL logs and assign heuristic labels."""
    sessions: dict[str, list[str]] = {}

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            continue

        with path.open("r", encoding="utf-8") as file_handle:
            for line in file_handle:
                event = json.loads(line.strip())
                session_id = event.get("session")
                if not session_id:
                    continue

                if session_id not in sessions:
                    sessions[session_id] = []

                if event.get("eventid") == "cowrie.command.input":
                    sessions[session_id].append(event.get("input", ""))

    texts: list[str] = []
    labels: list[int] = []

    for commands in sessions.values():
        if not commands:
            continue

        combined_text = " ".join(commands)
        texts.append(combined_text)
        labels.append(_infer_label_from_session_text(combined_text))

    return texts, labels


def fine_tune_distilbert(texts: list[str], labels: list[int], output_dir: str = "saved_distilbert_cowrie"):
    """Fine-tune DistilBERT for three-label Cowrie threat classification."""
    if len(texts) < 5:
        raise ValueError("Need at least 5 labeled sessions for a train/eval split.")

    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=3)

    dataset = Dataset.from_dict({"text": texts, "label": labels})
    split_dataset = dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = split_dataset["train"]
    eval_dataset = split_dataset["test"]

    def tokenize_func(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

    tokenized_train = train_dataset.map(tokenize_func, batched=True)
    tokenized_eval = eval_dataset.map(tokenize_func, batched=True)

    def compute_metrics(eval_pred):
        logits, truth_labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return {"accuracy": float(np.mean(predictions == truth_labels))}

    training_args = TrainingArguments(
        output_dir="results",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        compute_metrics=compute_metrics,
    )

    print("Starting fine-tuning...")
    trainer.train()

    print("Evaluating model on test dataset...")
    eval_results = trainer.evaluate()
    print(f"Evaluation results: {eval_results}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(output_path))
    tokenizer.save_pretrained(str(output_path))

    return model, tokenizer, eval_dataset


def preview_eval_predictions(model, tokenizer, eval_dataset, limit: int = 10) -> None:
    """Print a small sample of prediction results for sanity-checking."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    for index in range(min(limit, len(eval_dataset))):
        text = eval_dataset[index]["text"]
        true_label = eval_dataset[index]["label"]

        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=1).item()
            confidence = torch.softmax(logits, dim=1).max().item()

        print(f"Session: {text}")
        print(
            "   => true="
            f"{LABEL_MAP.get(true_label, true_label)}, "
            f"predicted={LABEL_MAP.get(predicted_class, predicted_class)}, "
            f"confidence={confidence * 100:.2f}%"
        )
