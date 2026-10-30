# Technical Approach Report
## Cynbit AI Inquiry-to-Blueprint Assistant
**Applicant:** Dnyandip Pandurang Vadane  
**Assessment:** AI/ML Engineer Intern  
**Status:** Proof-of-concept design and local demo

## 1. Architecture
Client inquiry + intake fields → text normalization → TF-IDF service catalogue vectors → cosine similarity ranking → missing-information checklist → deterministic blueprint template → human review.

## 2. Model and algorithm choices
### TF-IDF
TF-IDF weights terms by their importance within the catalogue. Unigrams and bigrams are used to capture both single terms and phrases. Catalogue service names and keywords receive repeated representation to make the short service descriptions more discoverable.

### Cosine similarity
Cosine similarity compares the inquiry vector with each service vector. Results are sorted by similarity. The score is multiplied by 100 for readability but is not a probability, calibrated confidence, or business-success score.

### Why not train a classifier?
There is no verified historical Cynbit inquiry dataset with human-confirmed outcomes. Synthetic examples are useful for testing data flow but are not sufficient evidence for a production classifier. A supervised model should only be considered after collecting permitted historical inquiries and reliable labels.

### Missing-information checklist
A deterministic checklist flags unknown budget, data readiness, integrations, security requirements, and timeline. These are discovery prompts, not model predictions.

### Blueprint generation and prompt engineering
The baseline uses a deterministic template rather than an external LLM. This avoids API costs and makes claims easier to control. If an approved LLM is added later, use a structured prompt that:
- treats the client inquiry as untrusted data, not instructions to override system policy;
- only uses facts present in the inquiry and approved service catalogue;
- separates facts, assumptions, recommendations, and unanswered questions;
- never invents price, delivery dates, capabilities, or guarantees;
- outputs a fixed schema (summary, matched services, workstreams, risks, questions);
- requires human review before external sharing.

## 3. Data pipeline
1. Read `service_catalog.csv` and validate required columns.
2. Normalize whitespace and handle missing cells.
3. Build service documents from name, description, keywords, and capabilities.
4. Fit TF-IDF on service documents plus the current inquiry for the small baseline implementation.
5. Rank catalogue entries by cosine similarity.
6. Run the missing-information checklist.
7. Generate and download the draft blueprint.

For a larger system, fit the vectorizer on a versioned catalogue, persist the fitted vectorizer, and monitor catalogue changes.

## 4. Dataset provenance
`synthetic_inquiries.csv` contains 180 synthetic scenarios and expected service labels, authored for this assessment. The service catalogue is paraphrased from public company service descriptions. The inquiry data are not real client records. Repeated scenario templates mean a random row split can leak near-duplicate language across splits; rigorous evaluation should split by template family or scenario group.

## 5. Evaluation plan
- **Top-1 accuracy:** fraction of held-out inquiries whose expected primary service is ranked first.
- **Top-3 recall/hit rate:** fraction where the expected primary service appears in the top three.
- **Per-class results:** inspect performance by service to detect categories that are often confused.
- **Checklist recall:** human reviewers mark which discovery questions are genuinely necessary; measure how many are surfaced.
- **Draft quality:** reviewers assess factual consistency, usefulness, missing assumptions, and unsupported claims.
- **Workflow value:** compare median time to prepare an initial blueprint with a measured manual baseline.

Do not report scores from synthetic examples as evidence of real-world accuracy. Establish a template-grouped, human-reviewed test set before claiming model performance.

## 6. Risks, privacy and controls
- Do not enter confidential data in a public demo.
- Avoid protected or sensitive personal characteristics in scoring.
- Do not automatically reject leads or make binding commercial commitments.
- Human review is required for service recommendations and generated drafts.
- Keep future API keys in environment variables or platform secrets.
- Production deployment requires authentication, access control, data-retention rules, security testing and company approval.

## 7. Execution plan
1. Confirm service catalogue with a Cynbit stakeholder.
2. Establish acceptance criteria and a reviewed evaluation set.
3. Run baseline matching and inspect errors by class.
4. Improve retrieval only where measured errors justify the extra complexity.
5. Pilot with consented and secured inquiries.
6. Compare workflow time and reviewer quality against the manual baseline.
7. Decide whether CRM integration or an LLM adds enough value to justify operational cost and risk.
