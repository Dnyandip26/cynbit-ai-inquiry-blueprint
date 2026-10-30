from pathlib import Path
import pandas as pd
import pytest

from src.service_matcher import rank_services, identify_missing_information
from src.blueprint import generate_blueprint
from src.llm_service import (
    format_inr_budget_label,
    sanitize_generated_analysis,
    normalize_currency_sentence,
    GroqConfigurationError,
    analyze_with_groq,
)

ROOT = Path(__file__).resolve().parents[1]
SERVICES = pd.read_csv(ROOT / "service_catalog.csv").fillna("")

def test_document_inquiry_matches_document_service():
    result = rank_services(
        "We need a chatbot that answers questions from PDF documents using an LLM",
        SERVICES, top_k=3
    )
    assert result
    assert result[0]["service_id"] == "S02"

def test_empty_inquiry_returns_no_matches():
    assert rank_services("   ", SERVICES) == []

def test_missing_information_checklist():
    missing = identify_missing_information(
        "Not specified", "Data availability unknown", "None specified",
        "Not specified", None
    )
    assert len(missing) == 5

def test_blueprint_includes_human_review_warning():
    matches = rank_services("Build a web portal", SERVICES, top_k=2)
    draft = generate_blueprint("Build a web portal", matches, [], 8)
    assert "Draft for human review" in draft
    assert "not a quote" in draft


def test_inr_budget_labels_preserve_selected_range():
    assert format_inr_budget_label("Under $2,000") == "Under ₹2,00,000"
    assert format_inr_budget_label("$2,000–$10,000") == "₹2,00,000–₹10,00,000"
    assert format_inr_budget_label("Not specified") == "Not specified"


@pytest.mark.parametrize(
    ("inquiry", "expected_service_terms"),
    [
        ("Customer Support AI Agent for internal help desk with document answers and routing", ["AI agent", "document", "knowledge"]),
        ("AI-powered resume screening system to shortlist candidates and summarize CVs", ["document", "LLM", "automation"]),
        ("E-commerce website development with product catalog, cart, checkout and customer accounts", ["web", "backend", "API"]),
        ("Business data analytics dashboard for sales and operations reporting", ["dashboard", "analytics", "data"]),
        ("AI-powered document processing system to extract and summarize scanned PDFs and invoices", ["document", "PDF", "automation"]),
    ],
)
def test_business_inquiry_scenarios_are_relevant(inquiry, expected_service_terms):
    matches = rank_services(inquiry, SERVICES, top_k=3)
    assert matches
    texts = " ".join(
        f"{item['service_name']} {item['description']} {item['matching_keywords']}"
        for item in matches
    ).lower()
    assert any(term.lower() in texts for term in expected_service_terms)

    blueprint = generate_blueprint(inquiry, matches, ["What data sources are available?"], 8)
    assert "Draft for human review" in blueprint
    assert "not a quote" in blueprint.lower()


def test_edge_cases_handle_gracefully():
    assert rank_services("   ", SERVICES) == []
    assert rank_services("", SERVICES) == []

    long_inquiry = "AI customer support automation " * 250
    matches = rank_services(long_inquiry, SERVICES, top_k=3)
    assert isinstance(matches, list)
    assert len(matches) <= 3

    missing = identify_missing_information(
        "Not specified",
        "Data availability unknown",
        "None specified",
        "Not specified",
        None,
    )
    assert len(missing) >= 5

    assert generate_blueprint("", [], [], None) == "Please enter a project inquiry to generate a blueprint."

    weak_match_warning = [{"similarity_score": 8.5, "service_name": "Unrelated service"}]
    assert weak_match_warning[0]["similarity_score"] < 15


def test_vendor_neutral_and_staffing_sanitization():
    cleaned = sanitize_generated_analysis({
        "recommended_technology_stack": [
            "OpenAI GPT-3.5 for orchestration",
            "Pinecone vector store",
            "Current prototype provider: Groq"
        ],
        "resource_requirements": [
            "1 × Project Manager, 2 engineers, 1 designer"
        ],
        "phase_effort_estimates": [
            "Discovery: 2 engineers for 3 weeks"
        ],
    })

    text = "\n".join(cleaned["recommended_technology_stack"])
    assert "LLM provider to be selected during discovery" in text
    assert "Groq" not in text or "Current prototype provider: Groq" in text
    assert cleaned["resource_requirements"] == ["To be estimated after discovery"]
    assert cleaned["phase_effort_estimates"] == ["To be estimated after discovery"]


def test_currency_sentence_avoids_hyphenated_inr_formatting():
    assert normalize_currency_sentence("Budget is under-₹2,00,000") == "Budget is within the budget range of Under ₹2,00,000"
    assert normalize_currency_sentence("Budget is within the budget range of Under ₹2,00,000") == "Budget is within the budget range of Under ₹2,00,000"


def test_groq_error_messages_are_user_safe(monkeypatch):
    def fake_get_groq_settings():
        return ("fake-key", "fake-model")

    class FakeCompletions:
        @staticmethod
        def create(*args, **kwargs):
            raise ConnectionError("https://api.groq.com/v1/chat/completions key=secret-value")

    class FakeClient:
        chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("src.llm_service.get_groq_settings", fake_get_groq_settings)
    monkeypatch.setattr("src.llm_service.Groq", lambda api_key: FakeClient())

    with pytest.raises(GroqConfigurationError) as exc:
        analyze_with_groq("Help desk agent", {"budget": "Under ₹2,00,000"}, [])

    message = str(exc.value).lower()
    assert "groq" in message
    assert "api.groq.com" not in message
    assert "secret-value" not in message

    class FakeBadResponse:
        @staticmethod
        def create(*args, **kwargs):
            class Response:
                choices = [type("Choice", (), {"message": type("Message", (), {"content": "{not-json"})()})()]
            return Response()

    monkeypatch.setattr("src.llm_service.Groq", lambda api_key: type("Client", (), {"chat": type("Chat", (), {"completions": FakeBadResponse()})()})())
    with pytest.raises(GroqConfigurationError) as exc2:
        analyze_with_groq("Document processing", {"budget": "Not specified"}, [])

    message2 = str(exc2.value).lower()
    assert "unexpected response" in message2 or "failed" in message2
    assert "secret" not in message2
