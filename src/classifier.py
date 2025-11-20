#!/usr/bin/env python3
"""
Simple Qwen3-Embedding classifier using only transformers and torch
No sklearn, no sentence-transformers dependencies
"""

import torch
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import numpy as np


class SimpleQwen3Classifier:
    """Meeting classifier using Qwen3-Embedding with minimal dependencies"""
    
    TEMPLATE_CATEGORIES = {
        "Quarterly Business Review (QBR)": "Strategic business review meeting covering quarterly performance, metrics, and goals",
        "Product Launch": "Meeting focused on launching new products or features to market",
        "Conference/Event Preparation": "Planning and coordination meeting for conferences, summits, or large events",
        "Executive Presentation": "High-stakes presentation to executive leadership or board",
        "Budget Planning": "Financial planning and budget allocation meeting",
        "Project Kickoff": "Initial meeting to start a new project with team alignment",
        "Hiring Committee": "Meeting to review candidates and make hiring decisions",
        "Training Workshop": "Educational session for skill development and knowledge sharing"
    }
    
    # Semantic anchors for value estimation
    # Refined based on Qwen3-30B feedback to improve correlation
    HIGH_VALUE_DESC = "High strategic impact, executive presentation, critical decision making, large scale coordination, crisis management, board meeting, product launch, pillar review, fiscal year kickoff, strategy roadmap, business review, okr planning"
    LOW_VALUE_DESC = "Routine status check, casual sync, social event, administrative task, 1:1 catch up, weekly sync, team happy hour, training workshop, boot camp, open day, showcase, learning session"
    
    # Calibration parameters (derived from Qwen3-30B comparison)
    CALIBRATION_SLOPE = 2.0089
    CALIBRATION_INTERCEPT = -79.3864
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        
        print(f"Loading Qwen3-Embedding from {self.model_path}...")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(self.model_path),
            trust_remote_code=True
        )
        
        self.model = AutoModel.from_pretrained(
            str(self.model_path),
            torch_dtype=torch.float32,  # Use float32 for CPU
            device_map="cpu",
            trust_remote_code=True
        )
        
        self.model.eval()
        
        print("✅ Model loaded")
        print("📊 Pre-computing category and value embeddings...")
        
        # Pre-compute category embeddings
        self.category_embeddings = {}
        for cat_name, cat_desc in self.TEMPLATE_CATEGORIES.items():
            text = f"{cat_name}: {cat_desc}"
            emb = self._embed(text)
            self.category_embeddings[cat_name] = emb
            
        # Pre-compute value anchors
        self.high_value_emb = self._embed(self.HIGH_VALUE_DESC)
        self.low_value_emb = self._embed(self.LOW_VALUE_DESC)
        
        print(f"✅ {len(self.category_embeddings)} categories ready")
        print(f"✅ Value estimation anchors ready\n")
    
    def _embed(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Mean pooling
            embedding = outputs.last_hidden_state.mean(dim=1)
        
        return embedding.cpu().numpy().flatten()
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def classify_meeting(
        self,
        title: str,
        description: Optional[str] = None,
        attendee_count: Optional[int] = None
    ) -> Tuple[str, float]:
        """Classify meeting into category"""
        # Build context
        context = f"Meeting: {title}"
        if description:
            context += f". {description}"
        if attendee_count:
            context += f". {attendee_count} attendees"
        
        # Get meeting embedding
        meeting_emb = self._embed(context)
        
        # Calculate similarities
        best_category = None
        best_score = -1.0
        
        for cat_name, cat_emb in self.category_embeddings.items():
            similarity = self._cosine_similarity(meeting_emb, cat_emb)
            if similarity > best_score:
                best_score = similarity
                best_category = cat_name
        
        # Normalize confidence from [-1, 1] to [0, 1]
        confidence = (best_score + 1) / 2
        
        return best_category, confidence

    def estimate_value(
        self,
        title: str,
        description: Optional[str] = None,
        attendee_count: Optional[int] = None
    ) -> Tuple[float, str]:
        """
        Estimate meeting value using semantic similarity to value anchors
        Returns: (score 0-100, reasoning string)
        """
        # Build context
        context = f"Meeting: {title}"
        if description:
            context += f". {description}"
        if attendee_count:
            context += f". {attendee_count} attendees"
            
        # Get meeting embedding
        meeting_emb = self._embed(context)
        
        # Calculate similarity to high and low value anchors
        high_sim = self._cosine_similarity(meeting_emb, self.high_value_emb)
        low_sim = self._cosine_similarity(meeting_emb, self.low_value_emb)
        
        # Calculate raw score based on relative similarity
        # If closer to high than low, score > 50
        # We use softmax-like logic or simple projection
        
        # Simple projection: (high - low + 1) / 2  -> maps [-1, 1] difference to [0, 1]
        diff = high_sim - low_sim
        raw_score = (diff + 1) / 2  # 0.0 to 1.0
        
        # Apply attendee boost (logarithmic)
        attendee_boost = 0
        if attendee_count:
            # 10 attendees -> +0.1, 100 attendees -> +0.2
            attendee_boost = min(0.2, np.log10(max(1, attendee_count)) / 10)
            
        final_score = min(100, (raw_score + attendee_boost) * 100)
        
        # Apply calibration to match Qwen3-30B variance
        # Formula: y = 2.0089 * x - 79.3864
        calibrated_score = self.CALIBRATION_SLOPE * final_score + self.CALIBRATION_INTERCEPT
        calibrated_score = max(0, min(100, calibrated_score))
        
        # Generate "reasoning" (synthetic based on score components)
        reasoning = f"Semantic similarity to high-value concepts: {high_sim:.2f} vs low-value: {low_sim:.2f}."
        if attendee_count and attendee_count > 20:
            reasoning += f" Boosted by high attendee count ({attendee_count})."
        reasoning += f" Calibrated from raw score {final_score:.1f}."
            
        return calibrated_score, reasoning
