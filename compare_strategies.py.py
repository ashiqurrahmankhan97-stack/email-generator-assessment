"""
Run Strategy A vs Strategy B using Google GenAI SDK and save results.
"""
import json
import csv
from pathlib import Path
from google import genai
from google.genai import types

from generate_email import load_prompt, build_prompt
from review_email import load_reviewer_prompt, build_review_prompt
from metrics import fact_coverage_score, professional_email_quality_score, tone_alignment_score

def call_llm(client: genai.Client, prompt_text: str) -> str:
    """Invokes Gemini 2.5 Flash model."""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1000
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"API Error: {e}")
        return ""

def get_llm_judge_score(client: genai.Client, generated_email: str, target_tone: str) -> float:
    """Implements an LLM-as-a-Judge check to grade Tone Alignment (1.0 to 5.0)."""
    judge_prompt = f"""
    Analyze the following email and rate how well it matches the tone '{target_tone}' on a scale from 1.0 to 5.0. 
    Provide ONLY the numeric float score as your response (e.g. 4.5). Do not write an explanation.

    Email:
    {generated_email}
    """
    raw_score = call_llm(client, judge_prompt)
    try:
        clean_score = "".join(c for c in raw_score if c.isdigit() or c == '.')
        return tone_alignment_score(clean_score)
    except Exception:
        return 3.0

def run_quality_check(email_text: str) -> int:
    """Helper to verify structural milestones for PEQS."""
    text_lower = email_text.lower()
    has_greeting = any(g in text_lower for g in ["dear", "hello", "hi", "team"])
    has_purpose = any(p in text_lower for p in ["follow", "request", "apologize", "invite", "remind", "announce", "escalate", "update"])
    has_flow = len(email_text.split('\n\n')) >= 2
    is_professional = not any(s in text_lower for s in ["hey", "wanna", "gonna", "asap"])
    has_closing = any(c in text_lower for c in ["sincerely", "regards", "thank you", "best"])
    
    return professional_email_quality_score(
        greeting=has_greeting,
        purpose=has_purpose,
        flow=has_flow,
        professionalism=is_professional,
        closing=has_closing
    )

def main():
    # Initializes Google GenAI Client using GEMINI_API_KEY environment variable
    client = genai.Client()

    base_dir = Path(__file__).parent.parent
    scenarios = json.loads((base_dir / "data/test_scenarios.json").read_text(encoding="utf-8"))
    
    baseline_template = load_prompt(base_dir / "prompts/baseline_prompt.txt")
    writer_template = load_prompt(base_dir / "prompts/writer_prompt.txt")
    reviewer_template = load_reviewer_prompt(base_dir / "prompts/reviewer_prompt.txt")

    results = []

    for idx, sc in enumerate(scenarios, 1):
        s_id = sc["scenario_id"]
        intent = sc["intent"]
        tone = sc["tone"]
        facts = sc["facts"]
        
        print(f"Running evaluation profile [{idx}/10] - ID: {s_id}")

        # Strategy A: Baseline
        prompt_a = build_prompt(baseline_template, intent, facts, tone)
        email_a = call_llm(client, prompt_a)
        
        results.append({
            "scenario_id": s_id,
            "strategy": "Baseline",
            "FCS": fact_coverage_score(facts, email_a),
            "TAS": get_llm_judge_score(client, email_a, tone),
            "PEQS": run_quality_check(email_a)
        })

        # Strategy B: Writer-Reviewer
        prompt_b_write = build_prompt(writer_template, intent, facts, tone)
        draft_b = call_llm(client, prompt_b_write)
        
        prompt_b_review = build_review_prompt(reviewer_template, intent, facts, tone, draft_b)
        final_email_b = call_llm(client, prompt_b_review)

        results.append({
            "scenario_id": s_id,
            "strategy": "Writer_Reviewer",
            "FCS": fact_coverage_score(facts, final_email_b),
            "TAS": get_llm_judge_score(client, final_email_b, tone),
            "PEQS": run_quality_check(final_email_b)
        })

    # Save to CSV using pandas wrapper
    from evaluate import save_results
    save_results(results, base_dir / "data/evaluation_results.csv")
    print("Execution complete. Results exported to data/evaluation_results.csv")

if __name__ == "__main__":
    main()