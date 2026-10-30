"""Generate a conservative, template-based project blueprint."""
from __future__ import annotations
from datetime import date

def generate_blueprint(
    inquiry: str,
    matches: list[dict],
    missing_questions: list[str],
    timeline_weeks: int | str | None,
) -> str:
    inquiry = (inquiry or "").strip()
    if not inquiry:
        return "Please enter a project inquiry to generate a blueprint."
    service_lines = []
    for match in matches[:3]:
        service_lines.append(
            f"- {match['service_name']} (text similarity: {match['similarity_score']:.2f}/100)"
        )
    if not service_lines:
        service_lines = ["- No clear catalogue match; manual discovery is recommended."]
    timeline = str(timeline_weeks).strip() if timeline_weeks not in (None, "") else "not specified"
    questions = "\n".join(f"- {q}" for q in missing_questions) if missing_questions else "- Confirm acceptance criteria and pilot success measures."
    return f"""# Preliminary Project Blueprint

**Generated:** {date.today().isoformat()}  
**Status:** Draft for human review — not a quote, commitment, or final architecture.

## 1. Client requirement
{inquiry}

## 2. Potentially relevant services
{chr(10).join(service_lines)}

*Similarity scores indicate text overlap with the service catalogue. They are not probabilities or guarantees of suitability.*

## 3. Suggested discovery workstreams
1. Confirm business objective, target users, and measurable acceptance criteria.
2. Validate data sources, quality, access permissions, and privacy constraints.
3. Confirm required integrations and the system-of-record for each data type.
4. Define a small proof of concept and review the results with stakeholders.
5. Estimate delivery only after scope, dependencies, and risks have been reviewed.

## 4. Timeline
Client-stated target: {timeline} week(s). This is an input, not a feasibility estimate or delivery promise.

## 5. Questions to confirm
{questions}

## 6. Risks and assumptions
- Service recommendations are based on text similarity and the current demo catalogue.
- No price, delivery commitment, or production architecture has been inferred.
- Technology choices, architecture decisions, and effort estimates are provisional until discovery is complete.
- Data protection, access control, monitoring, and human review must be designed before deployment.
- A Cynbit solution architect should validate the scope and recommendations before sharing externally.

## 7. Proposed success metrics
- Proposed targets only; all targets are preliminary and require client approval.

*Note: technology selection, staffing assumptions, effort estimates, and success targets are provisional until confirmed in discovery and approved by the client.*
"""
