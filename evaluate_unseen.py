from pathlib import Path
import pandas as pd
from src.service_matcher import rank_services

ROOT = Path(__file__).resolve().parent
services = pd.read_csv(ROOT / "service_catalog.csv").fillna("")

# New, manually written synthetic inquiries.
# These are diagnostic examples, not real customer data.
cases = [
    {
        "id": "NEW01",
        "expected": "S01",
        "text": "Our employees need a digital assistant that collects information from internal tools, prepares task briefs, and suggests what to do next."
    },
    {
        "id": "NEW02",
        "expected": "S02",
        "text": "We receive scanned agreements and need important dates, obligations, and summaries extracted for staff verification."
    },
    {
        "id": "NEW03",
        "expected": "S04",
        "text": "Connect an AI capability to our existing CRM application through APIs without replacing the current software."
    },
    {
        "id": "NEW04",
        "expected": "S10",
        "text": "Our paid search campaigns need better lead quality and lower advertising costs using Google Ads performance data."
    },
    {
        "id": "NEW05",
        "expected": "S12",
        "text": "Many visitors open our pricing page but leave before signing up. We want to test page layouts and simplify the registration journey."
    },
    {
        "id": "NEW06",
        "expected": "S06",
        "text": "Build reliable backend endpoints so our customer records can be exchanged securely between the application and internal dashboard."
    },
]

available_ids = set(services["service_id"].astype(str))
missing = sorted({c["expected"] for c in cases} - available_ids)

if missing:
    raise ValueError(f"Expected service IDs missing from catalogue: {missing}")

results = []

for case in cases:
    predictions = rank_services(case["text"], services, top_k=3)
    predicted_ids = [p["service_id"] for p in predictions]

    results.append({
        "inquiry_id": case["id"],
        "expected_service": case["expected"],
        "top1_prediction": predicted_ids[0] if predicted_ids else "",
        "top3_predictions": ";".join(predicted_ids),
        "top1_correct": bool(predicted_ids and predicted_ids[0] == case["expected"]),
        "top3_hit": case["expected"] in predicted_ids,
        "inquiry_text": case["text"],
    })

out = pd.DataFrame(results)
out.to_csv(ROOT / "unseen_evaluation_results.csv", index=False)

print("\n=== NEW SYNTHETIC DIAGNOSTIC SET ===")
print(f"Inquiries: {len(out)}")
print(f"Top-1: {out['top1_correct'].sum()}/{len(out)} "
      f"({out['top1_correct'].mean():.2%})")
print(f"Top-3: {out['top3_hit'].sum()}/{len(out)} "
      f"({out['top3_hit'].mean():.2%})")
print("\nDetailed predictions:")
print(out[[
    "inquiry_id", "expected_service", "top1_prediction",
    "top3_predictions", "top1_correct", "top3_hit"
]].to_string(index=False))
print("\nSaved to unseen_evaluation_results.csv")
print("Note: these are manually authored synthetic examples, not real-world validation.")
