#!/usr/bin/env python3
"""
Meeting Value Estimator (Qwen3-Embedding Calibrated)
Usage: python estimate_value.py <input_json> [output_json]
"""

import sys
import json
import time
import argparse
import numpy as np
from pathlib import Path
from src.classifier import SimpleQwen3Classifier

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def load_calendar_data(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Handle different formats
    if isinstance(data, list):
        return data
    elif 'events' in data:
        return data['events']
    elif 'value' in data:
        return data['value']
    else:
        # Assume it might be a single object or unknown format, try to wrap in list if dict
        if isinstance(data, dict):
            return [data]
        raise ValueError("Could not parse calendar data. Expected list or dict with 'events' key.")

def main():
    parser = argparse.ArgumentParser(description="Estimate meeting value using Qwen3-Embedding")
    parser.add_argument("input_file", help="Path to input JSON file containing meetings")
    parser.add_argument("--output", "-o", help="Path to output JSON file", default=None)
    parser.add_argument("--model-path", "-m", help="Path to model directory", default="models/qwen3-embedding")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)
        
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("output") / f"{input_path.stem}_estimated.json"
        output_path.parent.mkdir(exist_ok=True)
        
    model_path = Path(args.model_path)
    if not model_path.exists():
        # Try relative to script location
        script_dir = Path(__file__).parent
        model_path = script_dir / args.model_path
        if not model_path.exists():
            print(f"❌ Model not found at: {model_path}")
            print("Please ensure the model is downloaded to 'models/qwen3-embedding'")
            sys.exit(1)
            
    print(f"🚀 Initializing Qwen3-Embedding Classifier...")
    classifier = SimpleQwen3Classifier(str(model_path))
    
    print(f"📅 Loading meetings from {input_path}...")
    meetings = load_calendar_data(str(input_path))
    print(f"✅ Loaded {len(meetings)} meetings")
    
    results = []
    print("\nProcessing meetings...")
    
    start_total = time.time()
    
    for i, meeting in enumerate(meetings, 1):
        subject = meeting.get('subject', 'Unknown')
        body = meeting.get('bodyPreview', '') or meeting.get('body', {}).get('content', '')
        attendees = meeting.get('attendees', [])
        attendee_count = len(attendees) if isinstance(attendees, list) else 0
        
        score, reasoning = classifier.estimate_value(subject, body, attendee_count)
        
        # Also get category
        category, confidence = classifier.classify_meeting(subject, body, attendee_count)
        
        result = {
            'meeting': subject,
            'score': round(score, 1),
            'category': category,
            'confidence': round(confidence, 2),
            'reasoning': reasoning,
            'original_data': meeting
        }
        results.append(result)
        
        # Progress bar
        if i % 10 == 0 or i == len(meetings):
            sys.stdout.write(f"\rProcessed {i}/{len(meetings)} meetings")
            sys.stdout.flush()
            
    elapsed = time.time() - start_total
    print(f"\n\n✅ Completed in {elapsed:.1f}s ({elapsed/len(meetings):.3f}s per meeting)")
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
        
    print(f"💾 Results saved to {output_path}")

if __name__ == "__main__":
    main()
