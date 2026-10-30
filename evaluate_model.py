
from pathlib import Path
import pandas as pd

from src.service_matcher import rank_services

ROOT = Path(__file__).resolve().parent

services = pd.read_csv(ROOT / "service_catalog.csv").fillna("")
data = pd.read_csv(ROOT / "synthetic_inquiries.csv").fillna("")

# Evaluate only the held-out test split
test_data = data[data["split"] == "test"].copy()

if test_data.empty:
    raise ValueError("No test records found in synthetic_inquiries.csv")

top1_hits = 0
top3_hits = 0
results = []

for _, row in test_data.iterrows():
    predictions = rank_services(
        row["inquiry_text"], services, top_k=3
    )

    predicted_ids = [p["service_id"] for p in predictions]
    expected_id = row["expected_primary_service_id"]

    top1 = bool(predicted_ids and predicted_ids[0] == expected_id)
    top3 = expected_id in predicted_ids

    top1_hits += int(top1)
    top3_hits += int(top3)

    results.append({
        "inquiry_id": row["inquiry_id"],
        "expected_service": expected_id,
        "top1_prediction": predicted_ids[0] if predicted_ids else "",
        "top3_predictions": ";".join(predicted_ids),
        "top1_correct": top1,
        "top3_hit": top3,
        "data_origin": row["data_origin"],
    })

total = len(test_data)

print("\n=== SYNTHETIC TEST-SET EVALUATION ===")
print(f"Test inquiries: {total}")
print(f"Top-1 hits: {top1_hits}/{total}")
print(f"Top-1 accuracy: {top1_hits / total:.2%}")
print(f"Top-3 hits: {top3_hits}/{total}")
print(f"Top-3 hit rate: {top3_hits / total:.2%}")

output = pd.DataFrame(results)
output.to_csv(ROOT / "evaluation_results.csv", index=False)
print("\nDetailed results saved to evaluation_results.csv")
print("Note: synthetic-data metrics are not real-world performance.")
