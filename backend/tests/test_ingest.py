import json

import pytest

from agents.ingest import parse_bytes


def test_parse_csv():
    csv = "a,b\n1,2\n3,4\n".encode()
    df = parse_bytes(csv, "demo.csv")
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_parse_json_records():
    payload = json.dumps([{"region": "North", "sales": 10}, {"region": "South", "sales": 20}]).encode()
    df = parse_bytes(payload, "demo.json")
    assert len(df) == 2
    assert "region" in df.columns


def test_parse_json_wrapped():
    payload = json.dumps({"data": [{"x": 1}, {"x": 2}]}).encode()
    df = parse_bytes(payload, "wrapped.json")
    assert len(df) == 2


def test_empty_dataset_rejected():
    with pytest.raises(ValueError, match="empty"):
        parse_bytes(b"a,b\n", "empty.csv")


def test_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported"):
        parse_bytes(b"hello", "notes.txt")
