"""
Custom evaluation metrics.
"""
import re

def fact_coverage_score(required_facts, generated_email):
    found = sum(
        1 for fact in required_facts
        if any(word.lower() in generated_email.lower() for word in fact.split())
    )
    return round((found / len(required_facts)) * 100, 2)

def tone_alignment_score(judge_score):
    return float(judge_score)

def professional_email_quality_score(
    greeting=True,
    purpose=True,
    flow=True,
    professionalism=True,
    closing=True
):
    return sum([
        20 if greeting else 0,
        20 if purpose else 0,
        20 if flow else 0,
        20 if professionalism else 0,
        20 if closing else 0
    ])
