import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class NLPService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NLPService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the ONNX session and tokenizer."""
        self.model_path = getattr(settings, 'NLP_MODEL_PATH', None)
        self.is_mock = getattr(settings, 'USE_MOCK_NLP', False)
        
        if not self.model_path or not os.path.exists(self.model_path):
            if self.is_mock:
                logger.warning(f"ONNX model not found at {self.model_path}. NLPService will run in MOCK mode.")
                return
            else:
                raise RuntimeError(f"ModelLoadError: ONNX model not found at {self.model_path}. Set USE_MOCK_NLP=True for testing.")

        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
            
            logger.info(f"Loading ONNX model from {self.model_path}")
            # Initialize ONNX runtime session
            # We use CPUExecutionProvider for Green AI (no GPU overhead)
            self.session = ort.InferenceSession(
                self.model_path, 
                providers=['CPUExecutionProvider']
            )
            
            # For CamemBERT, the tokenizer can be loaded from HuggingFace Hub or a local path.
            model_dir = os.path.dirname(self.model_path)
            # Try to load it from the directory, fallback to huggingface hub if allowed.
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
            except Exception:
                # Fallback to standard camembert tokenizer (cached only)
                logger.warning(f"Could not load tokenizer from {model_dir}. Falling back to 'camembert-base' (local_files_only).")
                self.tokenizer = AutoTokenizer.from_pretrained("camembert-base", local_files_only=True)
                
            logger.info("ONNX model and tokenizer loaded successfully.")
        except Exception as e:
            if self.is_mock:
                logger.error(f"Failed to initialize NLPService: {e}. Running in MOCK mode.")
            else:
                raise RuntimeError(f"ModelLoadError: Failed to initialize NLPService: {e}") from e

    def predict_category(self, texts: list[str]) -> list[str]:
        """
        Predict the ADEME category for a list of accounting labels.
        Returns a list of predicted category names (or None if fallback).
        """
        if not texts:
            return []
            
        if self.is_mock:
            # Mock behavior: return a dummy category or just "Achats de Services"
            return ["Achats de Services" for _ in texts]
            
        try:
            # Tokenize the input texts
            inputs = self.tokenizer(
                texts, 
                padding=True, 
                truncation=True, 
                max_length=128, 
                return_tensors="np"
            )
            
            # Prepare ONNX inputs
            ort_inputs = {
                "input_ids": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"]
            }
            
            # Run inference
            logits = self.session.run(None, ort_inputs)[0]
            
            # Get predictions (argmax)
            import numpy as np
            predictions = np.argmax(logits, axis=1)
            
            # Map indices to category names (In a real system, this mapping comes from the model config)
            # Dummy mapping for now since we don't have the real model config
            # We assume index 0 -> "Achats de Services", etc.
            # This logic will be refined when the actual model is deployed.
            return [self._map_index_to_category(idx) for idx in predictions]
            
        except Exception as e:
            logger.error(f"Error during NLP prediction: {e}")
            raise RuntimeError(f"NLP Prediction Failed: {e}") from e
            
    def _map_index_to_category(self, index: int) -> str:
        # Placeholder mapping
        categories = {
            0: "Achats de Services",
            1: "Achats de Biens",
            2: "Déplacements",
            3: "Energie"
        }
        return categories.get(index, "Autre")
