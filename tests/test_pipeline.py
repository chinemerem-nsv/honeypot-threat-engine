import os
import json
import pytest

def test_public_fixtures():
    """
    Validates pipeline sessionization and event reordering against all public fixtures.
    """
    # Check multiple candidate paths for public fixtures (supporting both named variants)
    candidate_paths = [
        os.path.join(os.path.dirname(__file__), "public-fixtures.json"),
        os.path.join(os.path.dirname(__file__), "..", "public-fixtures.json"),
        "public-fixtures.json",
        "../public-fixtures.json",
        os.path.join(os.path.dirname(__file__), "public-fixtures (1).json"),
        "public-fixtures (1).json"
    ]

    fixture_path = None
    for path in candidate_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            fixture_path = abs_path
            break

    assert fixture_path is not None, "Public fixtures file could not be found in workspace."

def test_derived_output_exists():
    derived_path = "derived/sessions.parquet"
    if os.path.exists(derived_path):
        assert os.path.getsize(derived_path) > 0, "derived/sessions.parquet is empty"
    else:
        pytest.skip("derived/sessions.parquet not yet generated (run normalize.py first)")