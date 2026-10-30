# Dataset README — Cynbit AI Inquiry-to-Blueprint Assistant

## Files
- `service_catalog.csv`: 12 public-service-aligned catalogue entries, paraphrased from Cynbit's official Services page.
- `synthetic_inquiries.csv`: 180 synthetic client-inquiry examples with target service labels and structured context.
- `opportunity_matrix.csv`: qualitative opportunity comparison used in the report.
- `AI_Opportunity_Report.docx` / `.md`: assessment report.

## Important provenance note
The inquiry records are **synthetic examples authored for prototype development**. They are not Cynbit customer records, actual CRM leads, or evidence of actual market demand. The service catalogue descriptions are paraphrased from public pages; the taxonomy, example inquiries, labels, score, and evaluation split are project-created.

## `service_catalog.csv` fields
- `service_id`: stable service identifier (S01–S12).
- `service_name`, `category`: service label and grouping.
- `description`: short service summary.
- `keywords`: semicolon-separated matching terms.
- `capabilities`: semicolon-separated capability summary.
- `source_url`: public page used to ground the service entry.

## `synthetic_inquiries.csv` fields
- `inquiry_id`: unique synthetic record ID.
- `company_name`: fictional example company name.
- `industry`, `company_size`, `project_type`, `business_goal`: scenario context.
- `inquiry_text`: natural-language request used by the text-matching prototype.
- `urgency`, `budget_band`, `timeline_weeks`, `data_availability`, `integration_context`, `security_sensitivity`: illustrative intake fields.
- `requirement_clarity_1_to_5`: synthetic ordinal feature, not a measured human rating.
- `rule_based_priority_score_0_to_100`: deterministic illustrative score from urgency, clarity, budget band and timeline. This is **not an ML prediction** and is not calibrated on historical outcomes.
- `expected_primary_service_id`: target primary service label.
- `expected_secondary_service_ids`: secondary service label(s), separated by semicolons.
- `expected_service_names`: human-readable labels.
- `expected_keywords`: keywords for qualitative review.
- `missing_information_to_confirm`: synthetic checklist of information gaps.
- `recommended_human_questions`: questions that a consultant should ask.
- `data_origin`: `synthetic_example` for every inquiry record.
- `split`: deterministic `train`/`validation`/`test` assignment. Because templates are repeated, do not interpret scores from this split as an unbiased real-world benchmark; use template-grouped splitting for rigorous evaluation.

## Suggested use
1. Fit TF-IDF on the `service_catalog.csv` service descriptions + keywords.
2. Transform each inquiry text and rank services using cosine similarity.
3. Compare top-1/top-3 predictions against `expected_primary_service_id`.
4. Inspect errors by service; use grouped holdout validation because paraphrases share templates.
5. Use rule-based priority only as a transparent demo heuristic. Replace it with a trained model only when real, consented historical outcomes and a defensible target label are available.

## Privacy and responsible use
Do not insert real personal information or confidential client documents into this public demo. Human review is required before any proposal is sent or any lead is prioritized operationally.
