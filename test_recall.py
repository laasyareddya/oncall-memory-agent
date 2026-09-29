import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)

results = client.recall(
    bank_id="oncall",
    query="Redis connection pool exhausted, connection timeouts",
)
for r in results.results:
    print("-", r.text)
    print()
    