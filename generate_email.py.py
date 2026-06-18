"""
Generate email using baseline or writer prompt.
"""
from pathlib import Path

def load_prompt(prompt_path):
    return Path(prompt_path).read_text(encoding="utf-8")

def build_prompt(prompt_template, intent, facts, tone):
    return prompt_template.format(
        intent=intent,
        facts="\n".join(f"- {f}" for f in facts),
        tone=tone,
    )