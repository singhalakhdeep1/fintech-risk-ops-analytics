"""
Real-time Fraud Detection Model
Uses ML to detect fraudulent transactions in real-time
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import joblib
import os

class FraudDetectionModel:
    """Real-time fraud detection using ensemble ML models"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.01,
            random_state=42,
            n_estimators=100
        )
        self.random_forest = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def preprocess_features(self, df):
        """Preprocess transaction features for ML model"""
        features = df.copy()
        
        # Calculate time-based features
        if 'timestamp' in features.columns:
            features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
            features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Calculate amount-based features
        if 'amount' in features.columns:
            features['amount_log'] = np.log1p(features['amount'])
            
        # Calculate velocity features
        if 'user_id' in features.columns:
            features['transaction_count'] = features.groupby('user_id').cumcount()
            
        # Select numerical features
        numerical_cols = features.select_dtypes(include=[np.number]).columns
        return features[numerical_cols].fillna(0)
    
    def train(self, df, labels=None):
        """Train the fraud detection model"""
        features = self.preprocess_features(df)
        
        if labels is not None:
            # Supervised training with Random Forest
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            X_train_scaled = self.scaler.fit_transform(X_train)
            self.random_forest.fit(X_train_scaled, y_train)
        else:
            # Unsupervised training with Isolation Forest
            X_scaled = self.scaler.fit_transform(features)
            self.isolation_forest.fit(X_scaled)
            
        self.is_trained = True
        
    def predict_fraud_probability(self, transaction):
        """Predict fraud probability for a single transaction"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        df = pd.DataFrame([transaction])
        features = self.preprocess_features(df)
        features_scaled = self.scaler.transform(features)
        
        # Get anomaly score from Isolation Forest
        anomaly_score = self.isolation_forest.decision_function(features_scaled)[0]
        
        # Convert to probability (0-1)
        fraud_probability = 1 / (1 + np.exp(-anomaly_score))
        
        return {
            'fraud_probability': float(fraud_probability),
            'is_fraud': fraud_probability > 0.5,
            'anomaly_score': float(anomaly_score)
        }
    
    def batch_predict(self, transactions):
        """Predict fraud for multiple transactions"""
        df = pd.DataFrame(transactions)
        features = self.preprocess_features(df)
        features_scaled = self.scaler.transform(features)
        
        anomaly_scores = self.isolation_forest.decision_function(features_scaled)
        fraud_probabilities = 1 / (1 + np.exp(-anomaly_scores))
        
        return [
            {
                'fraud_probability': float(prob),
                'is_fraud': prob > 0.5,
                'anomaly_score': float(score)
            }
            for prob, score in zip(fraud_probabilities, anomaly_scores)
        ]
    
    def save_model(self, path='models/fraud_model.pkl'):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        model_data = {
            'isolation_forest': self.isolation_forest,
            'random_forest': self.random_forest,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, path)
        
    def load_model(self, path='models/fraud_model.pkl'):
        """Load trained model from disk"""
        model_data = joblib.load(path)
        self.isolation_forest = model_data['isolation_forest']
        self.random_forest = model_data['random_forest']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']


# Risk Scoring Model
class RiskScoringModel:
    """ML-based risk scoring for transactions"""
    
    def __init__(self):
        self.risk_factors = {
            'amount_high': 0.3,
            'velocity_high': 0.25,
            'location_risk': 0.2,
            'time_risk': 0.15,
            'merchant_risk': 0.1
        }
        
    def calculate_risk_score(self, transaction):
        """Calculate comprehensive risk score (0-100)"""
        risk_score = 0
        factors = {}
        
        # Amount risk
        if 'amount' in transaction:
            amount = transaction['amount']
            if amount > 10000:
                factors['amount_high'] = self.risk_factors['amount_high']
                risk_score += self.risk_factors['amount_high'] * 100
            elif amount > 5000:
                factors['amount_high'] = self.risk_factors['amount_high'] * 0.5
                risk_score += self.risk_factors['amount_high'] * 50
                
        # Velocity risk (simplified)
        if 'transaction_count' in transaction:
            count = transaction['transaction_count']
            if count > 10:
                factors['velocity_high'] = self.risk_factors['velocity_high']
                risk_score += self.risk_factors['velocity_high'] * 100
                
        # Time risk
        if 'timestamp' in transaction:
            hour = pd.to_datetime(transaction['timestamp']).hour
            if hour < 6 or hour > 22:  # Unusual hours
                factors['time_risk'] = self.risk_factors['time_risk']
                risk_score += self.risk_factors['time_risk'] * 100
                
        return {
            'risk_score': min(int(risk_score), 100),
            'risk_level': self._get_risk_level(risk_score),
            'factors': factors
        }
    
    def _get_risk_level(self, score):
        """Convert numeric score to risk level"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        elif score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
