import os, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from src.llm_client import get_llm_client

# A deliberately flawed draft: claims 30 days but P1 = 7 days
flawed_draft = {
    "behavior": "grounded_reply",
    "reply_text": "Good news! We offer 30-day refunds [P1], so your request is approved.",
    "citations": ["P1"]
}

stage4_prompt = Path("prompts/stage4_critique.v2.md").read_text()  # adjust filename
policy = Path("data/policy.md").read_text()

client = get_llm_client()
input_text = f"POLICY:\n{policy}\n\nDRAFT TO REVIEW:\n{json.dumps(flawed_draft)}"
result = client.call(stage4_prompt, input_text)

print("=== STAGE 4 RED-TEAM RESULT ===")
print(result)
Path("outputs/stage4_redteam_test.json").write_text(result)
print("\nSaved to outputs/stage4_redteam_test.json")