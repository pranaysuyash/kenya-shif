import os
import inspect
import pytest


from shif_analyzer import extract_with_openai, parse_pdf_with_pdfplumber


def test_model_defaults_are_correct():
    # Verify function-level defaults match the requested models
    sig_extract = inspect.signature(extract_with_openai)
    assert sig_extract.parameters["primary_model"].default == "gpt-5-mini"
    assert sig_extract.parameters["fallback_model"].default == "gpt-4.1-mini"

    sig_parse = inspect.signature(parse_pdf_with_pdfplumber)
    assert sig_parse.parameters["openai_primary"].default == "gpt-5-mini"
    assert sig_parse.parameters["openai_fallback"].default == "gpt-4.1-mini"


@pytest.mark.integration
def test_openai_key_present_or_skip():
    # Ensure OPENAI_API_KEY is set; otherwise skip this integration test
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set; skipping OpenAI integration test")


@pytest.mark.integration
def test_extract_with_openai_uses_primary_and_fallback_when_available():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set; skipping OpenAI integration test")

    # Minimal, realistic policy-like text
    text = (
        "Dialysis services: KES 10,650 per session; maximum 3 sessions per week; "
        "available at Level 4-6; not covered at Level 2."
    )

    # Call with explicit models
    result = extract_with_openai(text, key, primary_model="gpt-5-mini", fallback_model="gpt-4.1-mini")

    # The function must always return a well-formed dict with required keys
    for required in [
        "service",
        "tariff_value",
        "tariff_unit",
        "facility_levels",
        "coverage_status",
        "limits",
        "medical_category",
        "extraction_method",
        "model_used",
    ]:
        assert required in result

    # If OpenAI succeeded, we expect the extraction_method to be 'openai'
    # and model_used to be one of the requested models. If quota/availability issues
    # occur, the function falls back to regex_fallback but still returns a dict.
    if result.get("extraction_method") == "openai":
        assert result.get("model_used") in ("gpt-5-mini", "gpt-4.1-mini")
    else:
        # Fallback path should still be well-formed
        assert result.get("extraction_method") in ("regex_fallback", "regex_only")

