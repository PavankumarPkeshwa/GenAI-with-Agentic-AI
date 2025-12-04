"""
local_llm.py
------------
Local LLM using HuggingFace transformers pipeline.
No API token required - models downloaded locally.
"""

from transformers import pipeline
from typing import Optional

# Singleton to avoid reloading models
_llm_pipeline = None
_model_name = "google/flan-t5-base"  # Smaller model for faster loading


def get_local_llm(model_name: Optional[str] = None):
    """
    Returns a local HuggingFace pipeline for text generation.
    Model is downloaded once and cached locally.
    
    Args:
        model_name: Model to use (default: flan-t5-base for speed)
    
    Returns:
        Pipeline that can be called like: llm("question")
    """
    global _llm_pipeline, _model_name
    
    if model_name:
        _model_name = model_name
    
    if _llm_pipeline is None:
        print(f"🔄 Loading local model: {_model_name} (first time may take a few minutes)...")
        _llm_pipeline = pipeline(
            "text2text-generation",
            model=_model_name,
            max_length=512,
            do_sample=False,  # Deterministic output
            device=-1  # CPU (use 0 for GPU if available)
        )
        print(f"✅ Model loaded successfully!")
    
    return _llm_pipeline


class LocalLLM:
    """
    LangChain-compatible wrapper for local HuggingFace pipeline.
    Can be used as drop-in replacement for HuggingFaceHub.
    """
    
    def __init__(self, model_name: str = "google/flan-t5-base", **kwargs):
        self.model_name = model_name
        self.pipeline = get_local_llm(model_name)
        self.kwargs = kwargs
    
    def __call__(self, prompt: str) -> str:
        """Direct call interface"""
        return self.invoke(prompt)
    
    def invoke(self, prompt: str) -> str:
        """LangChain 1.x invoke interface"""
        result = self.pipeline(prompt, max_length=self.kwargs.get('max_length', 512))
        return result[0]['generated_text'] if result else ""
    
    def run(self, prompt: str) -> str:
        """Legacy run interface (deprecated but still works)"""
        return self.invoke(prompt)
    
    def predict(self, text: str) -> str:
        """Alternative interface"""
        return self.invoke(text)
