# test_notion.py
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))

# v3 syntax
results = notion.search(query="")

print("✅ Results found:", len(results["results"]))
for r in results["results"][:5]:
    print(" -", r.get("object"), "|", r.get("url", ""))