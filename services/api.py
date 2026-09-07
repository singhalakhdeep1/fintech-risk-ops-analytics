from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import joblib
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.features import engineer_features

app = FastAPI(title="Fraud Detection API", version="1.0.0")

# Load model on startup
model = None
model_path = Path(__file__).parents[1] / 'models' / 'fraud_model.pkl'


class TransactionRequest(BaseModel):
    user_id: str
    amount: float
    timestamp: str
    merchant_category: Optional[str] = "other"
    # Additional fields can be added as needed


class ScoreResponse(BaseModel):
    fraud_probability: float
    is_fraud: bool
    risk_level: str


@app.on_event("startup")
async def load_model():
    global model
    try:
        if model_path.exists():
            model = joblib.load(model_path)
            print(f"Model loaded from {model_path}")
        else:
            print(f"Model file not found at {model_path}, using dummy model")
            # Create a dummy model for demo purposes
            from sklearn.dummy import DummyClassifier
            model = DummyClassifier(strategy="uniform")
            model.fit([[0]], [0])
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/api/score", response_model=ScoreResponse)
async def score_transaction(transaction: TransactionRequest):
    """Score a transaction for fraud risk"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame([transaction.dict()])
        
        # Engineer features
        features = engineer_features(df)
        
        # Remove target column if present
        X = features.drop(['is_fraud'], axis=1, errors='ignore')
        
        # Get prediction
        fraud_probability = float(model.predict_proba(X)[0, 1])
        is_fraud = fraud_probability > 0.5
        
        # Determine risk level
        if fraud_probability < 0.3:
            risk_level = "low"
        elif fraud_probability < 0.7:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return ScoreResponse(
            fraud_probability=fraud_probability,
            is_fraud=is_fraud,
            risk_level=risk_level
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring error: {str(e)}")


@app.post("/api/batch-score")
async def batch_score_transactions(transactions: list[TransactionRequest]):
    """Score multiple transactions in batch"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        df = pd.DataFrame([t.dict() for t in transactions])
        features = engineer_features(df)
        X = features.drop(['is_fraud'], axis=1, errors='ignore')
        
        probabilities = model.predict_proba(X)[:, 1]
        
        results = []
        for i, prob in enumerate(probabilities):
            results.append({
                "transaction_index": i,
                "fraud_probability": float(prob),
                "is_fraud": prob > 0.5,
                "risk_level": "low" if prob < 0.3 else "medium" if prob < 0.7 else "high"
            })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch scoring error: {str(e)}")
