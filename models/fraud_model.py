import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, classification_report
import joblib
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))
from analysis.features import engineer_features


def train_fraud_model(data_path: str) -> dict:
    """Train XGBoost fraud detection model"""
    df = pd.read_csv(data_path)
    
    # Engineer features
    features = engineer_features(df)
    
    # Separate features and target
    X = features.drop('is_fraud', axis=1, errors='ignore')
    y = features['is_fraud'] if 'is_fraud' in features.columns else None
    
    if y is None:
        raise ValueError("Target column 'is_fraud' not found in data")
    
    # Train-test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # Calculate scale_pos_weight for class imbalance
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    # Initialize XGBoost classifier
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=scale_pos_weight,
        use_label_encoder=False,
        eval_metric='auc',
        random_state=42
    )
    
    # Train model with early stopping
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=20,
        verbose=False
    )
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    metrics = {
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "auc_roc": roc_auc_score(y_test, y_prob),
    }
    
    print(f"Model metrics: {metrics}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
    
    # Assert minimum performance threshold
    assert metrics['f1'] > 0.85, f"F1 score {metrics['f1']:.3f} below threshold 0.85"
    
    # Save model
    model_dir = Path(__file__).parent
    model_path = model_dir / 'fraud_model.pkl'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    return metrics


def load_model():
    """Load the trained fraud model"""
    model_path = Path(__file__).parent / 'fraud_model.pkl'
    return joblib.load(model_path)


if __name__ == "__main__":
    # Example usage with sample data
    from pathlib import Path
    data_path = Path(__file__).parents[1] / 'data' / 'transactions.csv'
    
    if data_path.exists():
        metrics = train_fraud_model(str(data_path))
        print(f"\nTraining completed successfully!")
    else:
        print(f"Data file not found at {data_path}")
        print("Please provide training data to train the model.")
