from ml.preprocessing.audit import classify_record
from ml.preprocessing.pipeline import preprocess_training_records
from agents.fewshot import fewshot_prompt_block, load_fewshot_examples


def test_drops_malformed_records():
    records = [
        {"visualization_type": "bar", "visualization_spec": {"type": "bar", "x": "a"}, "executive_insight": "ok"},
        {"visualization_type": "unknown", "visualization_spec": {}, "executive_insight": "bad"},
        "not a dict",
        {"foo": 1},
    ]
    kept = preprocess_training_records(records)
    assert len(kept) == 1
    assert kept[0]["visualization_type"] == "bar"


def test_classify_invalid_json_and_causal_claim():
    record = {
        "enhanced_prompt": "Data: Region, Revenue. North 10, South 20.",
        "enhanced_completion": """### Chart Type & Rationale:
Bar chart for category comparison.

### Visualization Specification:
```json
{ this is not json
```

### Executive Insight:
North caused the increase because of marketing.
""",
    }
    result = classify_record(0, record)
    assert "invalid_json_specification" in result["flags"]
    assert result["status"] == "rejected"


def test_classify_valid_bar_example():
    record = {
        "enhanced_prompt": "Compare regions. Data: | Region | Revenue |\n| North | 100 |\n| South | 80 |",
        "enhanced_completion": """### Chart Type & Rationale:
Bar chart to compare categories.

### Visualization Specification:
```json
{"type": "bar", "data": {"labels": ["North", "South"], "datasets": [{"data": [100, 80]}]}}
```

### Executive Insight:
North has the higher recorded revenue at 100 compared with South at 80.
""",
    }
    result = classify_record(1, record)
    assert result["status"] == "valid_visualization_task"
    assert result["databloom_spec"]["type"] == "bar"


def test_fewshot_loader_does_not_raise():
    load_fewshot_examples.cache_clear()
    block = fewshot_prompt_block()
    assert isinstance(block, str)
