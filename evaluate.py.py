"""
Evaluate generated emails against custom metrics.
"""
import pandas as pd

def save_results(results, output_file):
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    return df