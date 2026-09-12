import pandas as pd
from agents.profiler import run_profiler

def test_run_profiler():
    df = pd.DataFrame({
        "A": [1, 2, 3, 4, 100],  # Outlier at 100
        "B": ["cat", "dog", "cat", None, "mouse"],
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"]
    })
    
    profile = run_profiler(df)
    
    assert profile["num_rows"] == 5
    assert profile["num_columns"] == 3
    
    col_names = [c["name"] for c in profile["columns"]]
    assert "A" in col_names
    assert "B" in col_names
    assert "Date" in col_names
    
    # Check if temporal is detected
    date_col = next(c for c in profile["columns"] if c["name"] == "Date")
    assert date_col["is_temporal"] == True
    
    # Check outlier detection in A
    a_col = next(c for c in profile["columns"] if c["name"] == "A")
    assert a_col["outliers"] == 1
    
    # Check missing in B
    b_col = next(c for c in profile["columns"] if c["name"] == "B")
    assert b_col["missing_values"] == 1
