import pandas as pd
import numpy as np


def engineer_features(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Engineer features for fraud detection from transaction data"""
    df = transactions_df.copy()
    
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id', 'timestamp'])
    
    # Velocity features - transaction counts in time windows
    df['txn_count_1h'] = df.groupby('user_id')['timestamp'].transform(
        lambda x: x.rolling('1H', on='timestamp').count()
    )
    df['txn_count_24h'] = df.groupby('user_id')['timestamp'].transform(
        lambda x: x.rolling('24H', on='timestamp').count()
    )
    
    # Amount features - sum of amounts in time windows
    df['amount_sum_1h'] = df.groupby('user_id')['amount'].transform(
        lambda x: x.rolling('1H', on='timestamp').sum()
    )
    df['amount_sum_24h'] = df.groupby('user_id')['amount'].transform(
        lambda x: x.rolling('24H', on='timestamp').sum()
    )
    
    # Amount anomaly - z-score vs user's historical amounts
    user_stats = df.groupby('user_id')['amount'].agg(['mean', 'std'])
    df = df.join(user_stats, on='user_id', rsuffix='_hist')
    df['amount_zscore'] = (df['amount'] - df['mean']) / df['std'].replace(0, 1)
    
    # Time-based features
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'] >= 5
    df['is_night'] = (df['hour_of_day'] < 6) | (df['hour_of_day'] > 22)
    
    # Merchant category encoding (if exists)
    if 'merchant_category' in df.columns:
        df['merchant_category_encoded'] = df['merchant_category'].astype('category').cat.codes
    else:
        df['merchant_category_encoded'] = 0
    
    # Select final feature columns
    feature_cols = [
        'txn_count_1h', 'txn_count_24h', 'amount_sum_1h', 'amount_sum_24h',
        'amount_zscore', 'hour_of_day', 'day_of_week', 'is_weekend', 'is_night',
        'merchant_category_encoded', 'amount'
    ]
    
    # Add target column if exists
    if 'is_fraud' in df.columns:
        feature_cols.append('is_fraud')
    
    return df[feature_cols].fillna(0)
