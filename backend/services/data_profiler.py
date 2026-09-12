import pandas as pd

def profile_dataframe(df: pd.DataFrame) -> dict:
    """
    Generate a concise profile of the dataframe to be sent to the AI.
    """
    # Basic info
    num_rows = len(df)
    num_cols = len(df.columns)
    
    # Column info
    columns_info = []
    
    data_quality_issues = []
    
    for col in df.columns:
        col_series = df[col]
        col_type = str(col_series.dtype)
        num_missing = int(col_series.isnull().sum())
        missing_pct = num_missing / num_rows if num_rows > 0 else 0
        
        info = {
            "name": col,
            "type": col_type,
            "missing_values": num_missing,
            "missing_percentage": round(missing_pct * 100, 2),
        }
        
        # Determine if categorical or numeric
        if pd.api.types.is_numeric_dtype(col_series):
            info["min"] = float(col_series.min()) if not pd.isna(col_series.min()) else None
            info["max"] = float(col_series.max()) if not pd.isna(col_series.max()) else None
            info["mean"] = float(col_series.mean()) if not pd.isna(col_series.mean()) else None
            info["unique_values"] = int(col_series.nunique())
        else:
            info["unique_values"] = int(col_series.nunique())
            if info["unique_values"] < 20:
                info["sample_values"] = [str(x) for x in col_series.dropna().unique()[:5]]
                
        columns_info.append(info)
        
        # Log data quality issues
        if missing_pct > 0.05:
            data_quality_issues.append({
                "column": col,
                "issue": "High missing values",
                "severity": "medium",
                "description": f"{round(missing_pct * 100, 2)}% of values are missing."
            })
            
    # Check for duplicates
    num_duplicates = int(df.duplicated().sum())
    if num_duplicates > 0:
        data_quality_issues.append({
            "column": "dataset",
            "issue": "Duplicate rows",
            "severity": "medium",
            "description": f"Found {num_duplicates} duplicate rows."
        })

    return {
        "num_rows": num_rows,
        "num_columns": num_cols,
        "columns": columns_info,
        "data_quality_issues": data_quality_issues,
        "head": df.head(3).to_dict(orient="records")
    }
