"""Explainable TF-IDF service matching with lightweight domain query expansion."""
from __future__ import annotations

import re
from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

REQUIRED_SERVICE_COLUMNS = {"service_id", "service_name", "description", "keywords", "capabilities"}

# Curated expansion bridges common client language to catalogue terminology.
# It does not create new services; it only enriches the text used for retrieval.
QUERY_EXPANSIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(internal|employee|company)\b.*\b(ai assistant|assistant|questions|knowledge)\b|\b(ai assistant|knowledge assistant|employee questions)\b", re.I),
     "knowledge assistant LLM document automation document ingestion PDF processing summarization knowledge work"),
    (re.compile(r"\b(pdf|documents?|files?|document repository|source documents?)\b", re.I),
     "PDF processing document extraction document ingestion summarization text extraction"),
    (re.compile(r"\b(citations?|source references?|references? to sources|traceable sources?)\b", re.I),
     "document references knowledge retrieval source traceability"),
    (re.compile(r"\b(role[- ]based|permissions?|access control|identity provider|SSO|authentication)\b", re.I),
     "secure backend API application integration authentication authorization access controls"),
    (re.compile(r"\b(CRM|salesforce|hubspot|customer relationship management)\b", re.I),
     "CRM integration CRM workflow data synchronization API integration lead workflow"),
    (re.compile(r"\b(API|integrat(?:e|ion|ions)|existing systems?)\b", re.I),
     "API integration existing SaaS business systems application integration"),
    (re.compile(r"\b(OCR|scanned images?|scanned PDFs?)\b", re.I),
     "OCR text extraction document processing PDF processing"),
]


def _clean_text(value: Any) -> str:
    if value is None or (not isinstance(value, (list, dict)) and pd.isna(value)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def prepare_service_text(row: pd.Series) -> str:
    """Combine catalogue fields; emphasize service names and keywords."""
    name = _clean_text(row.get("service_name", ""))
    description = _clean_text(row.get("description", ""))
    keywords = _clean_text(row.get("keywords", "")).replace(";", " ")
    capabilities = _clean_text(row.get("capabilities", "")).replace(";", " ")
    return f"{name} {name} {description} {keywords} {keywords} {capabilities}"


def expand_query(query: str) -> str:
    """Add catalogue-aligned synonyms for common business requirement concepts."""
    additions: list[str] = []
    for pattern, expansion in QUERY_EXPANSIONS:
        if pattern.search(query):
            additions.append(expansion)
    return f"{query} {' '.join(dict.fromkeys(additions))}".strip()


def rank_services(inquiry_text: str, services: pd.DataFrame, top_k: int = 3) -> list[dict]:
    """Rank catalogue entries using TF-IDF cosine similarity.

    Scores are text similarity scores (0-100), not probabilities or confidence.
    The query is expanded with transparent, curated synonyms before vectorizing.
    """
    missing = REQUIRED_SERVICE_COLUMNS - set(services.columns)
    if missing:
        raise ValueError(f"Service catalogue is missing columns: {', '.join(sorted(missing))}")
    query = _clean_text(inquiry_text)
    if not query or services.empty:
        return []

    retrieval_query = expand_query(query)
    corpus = services.apply(prepare_service_text, axis=1).tolist()
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
    matrix = vectorizer.fit_transform(corpus + [retrieval_query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:max(1, top_k)]

    results = []
    for rank, i in enumerate(ranked_indices, start=1):
        row = services.iloc[i]
        results.append({
            "rank": rank,
            "service_id": str(row["service_id"]),
            "service_name": str(row["service_name"]),
            "category": str(row.get("category", "")),
            "description": str(row["description"]),
            "similarity_score": round(float(scores[i]) * 100, 2),
            "matching_keywords": str(row.get("keywords", "")),
        })
    return results


def identify_missing_information(
    budget_band: str,
    data_availability: str,
    integration_context: str,
    security_sensitivity: str,
    timeline_weeks: int | str | None,
) -> list[str]:
    """Return discovery questions based on project fields not specified."""
    missing = []
    if not budget_band or budget_band == "Not specified":
        missing.append("What budget range has been approved?")
    if not data_availability or data_availability in {"No data yet", "Data availability unknown", "Not specified"}:
        missing.append("What sample data is available, and is it approved for use?")
    if not integration_context or integration_context == "None specified":
        missing.append("Which existing systems, APIs, or databases must be integrated?")
    if not security_sensitivity or security_sensitivity == "Not specified":
        missing.append("What security, privacy, and compliance requirements apply?")
    try:
        weeks = int(timeline_weeks) if timeline_weeks not in (None, "") else 0
    except (TypeError, ValueError):
        weeks = 0
    if weeks <= 0:
        missing.append("What is the target timeline and are there fixed milestones?")
    return missing
