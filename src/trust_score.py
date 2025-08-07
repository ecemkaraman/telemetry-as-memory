def compute_trust(record):
    score = 1.0
    if record['cpu'] > 90 or record['errors'] > 10:
        score -= 0.5
    return max(score, 0.0)
def trust_score(df):
    df['trust_score'] = df.apply(compute_trust, axis=1)
    return df[['timestamp', 'trust_score']]
# Example Use
if __name__ == "__main__":          
    df = generate_telemetry(num_points=100, anomaly=True)
    df = preprocess(df)
    trust_df = trust_score(df)
    print(trust_df.head())
"""
import pandas as pd
from telemetry_as_memory import generate_telemetry