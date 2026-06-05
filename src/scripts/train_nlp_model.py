import os
import json
import logging
import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_synthetic_dataset():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "models", "fec_synthetic_dataset.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Synthetic dataset not found at {csv_path}. Run generate_fec_dataset.py first.")
        
    df = pd.read_csv(csv_path, sep="|")
    
    texts = df['EcritureLib'].tolist()
    labels_text = df['CategorieADEME'].tolist()
    
    unique_labels = sorted(list(set(labels_text)))
    label2id = {label: i for i, label in enumerate(unique_labels)}
    id2label = {i: label for label, i in label2id.items()}
    
    labels = [label2id[l] for l in labels_text]
    
    return texts, labels, id2label, label2id

class FECDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def main():
    logger.info("Loading synthetic dataset...")
    texts, labels, id2label, label2id = load_synthetic_dataset()
    
    model_name = "almanach/camembertav2-base"
    logger.info(f"Loading tokenizer {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    logger.info("Tokenizing data...")
    # Tokenize in batches if necessary, but 10,000 lines should fit in memory
    encodings = tokenizer(texts, truncation=True, padding=True, max_length=128)
    dataset = FECDataset(encodings, labels)
    
    logger.info(f"Loading base model {model_name}...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(id2label),
        id2label=id2label,
        label2id=label2id
    )
    
    output_dir = "./tmp_trainer"
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        logging_steps=50,
        save_strategy="no",
        report_to="none"
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )
    
    logger.info("Training model on synthetic dataset...")
    trainer.train()
    
    # Save the fine-tuned PyTorch model temporarily
    tmp_model_dir = "./tmp_model"
    trainer.save_model(tmp_model_dir)
    tokenizer.save_pretrained(tmp_model_dir)
    
    logger.info("Exporting to ONNX...")
    # Export to ONNX using Optimum
    ort_model = ORTModelForSequenceClassification.from_pretrained(tmp_model_dir, export=True)
    
    final_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(final_output_dir, exist_ok=True)
    
    # Save the base ONNX model
    base_onnx_dir = "./tmp_onnx"
    ort_model.save_pretrained(base_onnx_dir)
    tokenizer.save_pretrained(base_onnx_dir)
    
    logger.info("Quantizing to INT8...")
    quantizer = ORTQuantizer.from_pretrained(ort_model)
    qconfig = AutoQuantizationConfig.avx2(is_static=False, per_channel=True)
    quantizer.quantize(save_dir=final_output_dir, quantization_config=qconfig)
    
    # Optimum generates `model_quantized.onnx`. We need to rename it and move tokenizer files
    shutil.copy(os.path.join(base_onnx_dir, "config.json"), final_output_dir)
    # Tokenizer files
    for file in os.listdir(base_onnx_dir):
        if file.startswith("sentencepiece") or file.startswith("tokenizer") or file == "special_tokens_map.json":
            shutil.copy(os.path.join(base_onnx_dir, file), final_output_dir)
            
    # Rename model_quantized.onnx to camembert-int8.onnx
    quantized_model_path = os.path.join(final_output_dir, "model_quantized.onnx")
    target_model_path = os.path.join(final_output_dir, "camembert-int8.onnx")
    if os.path.exists(quantized_model_path):
        os.rename(quantized_model_path, target_model_path)
    
    logger.info(f"Model successfully saved to {target_model_path}")
    
    # Cleanup temporary directories
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.rmtree(tmp_model_dir, ignore_errors=True)
    shutil.rmtree(base_onnx_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
