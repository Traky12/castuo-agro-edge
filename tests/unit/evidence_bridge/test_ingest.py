from pathlib import Path

from evidence_bridge.bridge.ingest import ingest_jsonl

FIXTURES = Path(__file__).resolve().parents[3] / "evidence_bridge" / "fixtures"


def test_normal_fixture_all_valid():
    results = list(ingest_jsonl(FIXTURES / "normal.jsonl"))
    assert len(results) == 3
    assert all(r.valid for r in results)


def test_deviation_fixture_all_valid():
    results = list(ingest_jsonl(FIXTURES / "deviation_environmental.jsonl"))
    assert len(results) == 3
    assert all(r.valid for r in results)


def test_duplicate_fixture_both_valid_individually():
    results = list(ingest_jsonl(FIXTURES / "duplicate.jsonl"))
    assert len(results) == 2
    assert all(r.valid for r in results)
    assert results[0].event["source_event_id"] == results[1].event["source_event_id"]


def test_delayed_fixture_preserves_both_timestamps():
    results = list(ingest_jsonl(FIXTURES / "delayed.jsonl"))
    assert len(results) == 1
    event = results[0].event
    assert event["occurred_at"] != event["received_at"]


def test_sequence_gap_fixture_all_valid_but_gap_not_detected_here():
    results = list(ingest_jsonl(FIXTURES / "sequence_gap.jsonl"))
    assert all(r.valid for r in results)
    sequence_numbers = [r.event["sequence_number"] for r in results]
    assert sequence_numbers == [1, 2, 4]


def test_corrupt_malformed_fixture_all_rejected():
    results = list(ingest_jsonl(FIXTURES / "corrupt_malformed.jsonl"))
    assert len(results) == 3
    assert all(r.valid is False for r in results)
    assert all(r.errors for r in results)
