"""
Review and improve a generated email.
"""
from pathlib import Path

def load_reviewer_prompt(prompt_path):
    return Path(prompt_path).read_text(encoding="utf-8")

def build_review_prompt(prompt_template, intent, facts, tone, draft_email):
    return prompt_template.format(
        intent=intent,
        facts="\n".join(f"- {f}\" for f in facts),
        tone=tone,
        draft_email=draft_email,
    )