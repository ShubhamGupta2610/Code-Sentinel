"""Severity ranking and deduplication utilities."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Tuple

from app.core.config import settings

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "INFO"]


def compute_score(counts: Counter) -> float:
    score = max(0, 100 - (counts.get("CRITICAL", 0) * 25 + counts.get("HIGH", 0) * 10 + counts.get("MEDIUM", 0) * 5 + counts.get("INFO", 0) * 1))
    return float(score)


def map_grade(score: float) -> Tuple[str, str]:
    if score >= 90:
        return "A", "success"
    if score >= 75:
        return "B", "success"
    if score >= 55:
        return "C", "pending"
    if score >= 35:
        return "D", "failure"
    return "F", "failure"


def deduplicate(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique = []
    for f in findings:
        key = (f.get("file_path"), f.get("line"), f.get("category"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique


def rank_and_limit(findings: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float, str, str]:
    unique = deduplicate(findings)
    counts = Counter(f.get("severity", "INFO") for f in unique)
    score = compute_score(counts)
    grade, github_state = map_grade(score)
    # order by severity priority then confidence desc
    priority = {sev: idx for idx, sev in enumerate(SEVERITY_ORDER)}
    sorted_findings = sorted(
        unique,
        key=lambda f: (priority.get(f.get("severity", "INFO"), 99), -float(f.get("confidence", 0))),
    )
    max_comments = settings.MAX_COMMENTS_PER_PR
    limited_for_posting = sorted_findings[:max_comments]
    suppressed = max(0, len(sorted_findings) - max_comments)
    return limited_for_posting, score, grade, github_state, suppressed
