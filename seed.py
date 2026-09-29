import json
import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = "oncall"

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)

try:
    client.create_bank(bank_id=BANK_ID, name="On-call incidents")
except Exception as e:
    print("Bank may already exist, continuing:", e)

with open("data/incidents.json", encoding="utf-8") as f:
    incidents = json.load(f)

for inc in incidents:
    content = (
        f"Incident {inc['id']} on {inc['date']} in {inc['service']} "
        f"({inc['severity']}): {inc['title']}\n"
        f"Symptoms: {inc['symptoms']}\n"
        f"Error log: {inc['error_log']}\n"
        f"Root cause: {inc['root_cause']}\n"
        f"Failed attempts (did NOT work): {inc['failed_attempts']}\n"
        f"Resolution (worked): {inc['resolution']}\n"
        f"Time to resolve: {inc['time_to_resolve_minutes']} minutes"
    )
    client.retain(
        bank_id=BANK_ID,
        content=content,
        context="past production incident and how it was resolved",
        timestamp=f"{inc['date']}T10:00:00Z",
    )
    print(f"Saved {inc['id']}: {inc['title']}")

print("Done! All incidents saved.")
