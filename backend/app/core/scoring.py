"""
Readiness Scoring Engine for RebuildOS.
Calculates a transparent 0-100 score across 6 categories with deduplication and penalty caps.
"""
from typing import List, Dict, Tuple
from app.models.schemas import (
    Finding,
    CategoryScore,
    FindingCategory,
    ReadinessLabel,
)
from app.core.config import CATEGORY_CONFIG, SEVERITY_PENALTIES


def get_readiness_label(score: int) -> ReadinessLabel:
    """Returns the human-readable readiness tier for a given score."""
    if score >= 90:
        return "Strong"
    elif score >= 75:
        return "Good"
    elif score >= 50:
        return "Needs work"
    else:
        return "High risk"


def get_summary_message(score: int, label: ReadinessLabel, critical_count: int) -> str:
    """Generates an executive summary of the repository rebuild readiness."""
    if score >= 90:
        return (
            "Repository demonstrates exceptional reproducibility. Runtime versions, dependencies, "
            "and configurations are well-pinned with clear build and verification instructions."
        )
    elif score >= 75:
        return (
            "Repository has good foundational reproducibility. Minor improvements in runtime declarations, "
            "lockfile consistency, or environment documentation will make it fully rebuild-ready."
        )
    elif score >= 50:
        if critical_count > 0:
            return (
                f"Repository needs work ({critical_count} critical issue(s) detected). Missing lockfiles, "
                "unpinned dependencies, or missing runtime declarations pose notable rebuild hazards on fresh environments."
            )
        return (
            "Repository needs work. Several missing configurations or unpinned dependencies may cause unpredictable build failures."
        )
    else:
        return (
            "High rebuild risk. The repository lacks essential dependency manifests, lockfiles, runtime specifications, "
            "or installation documentation. Significant setup failures are expected on foreign machines."
        )


def calculate_readiness_score(
    findings: List[Finding]
) -> Tuple[int, ReadinessLabel, str, Dict[FindingCategory, CategoryScore]]:
    """
    Computes overall readiness score (0-100) and detailed category scores.
    Ensures duplicate findings do not apply duplicate deductions.
    Enforces maximum category penalty caps.
    """
    # 1. Deduplicate findings by (id, affected_file)
    seen_deductions = set()
    category_deductions: Dict[FindingCategory, int] = {
        cat: 0 for cat in CATEGORY_CONFIG.keys()  # type: ignore
    }
    category_finding_counts: Dict[FindingCategory, int] = {
        cat: 0 for cat in CATEGORY_CONFIG.keys()  # type: ignore
    }

    for finding in findings:
        cat = finding.category
        category_finding_counts[cat] = category_finding_counts.get(cat, 0) + 1

        dedup_key = f"{finding.id}:{finding.affected_file or 'none'}"
        if dedup_key in seen_deductions:
            continue
        seen_deductions.add(dedup_key)

        penalty = SEVERITY_PENALTIES.get(finding.severity, 2)
        category_deductions[cat] = category_deductions.get(cat, 0) + penalty

    # 2. Build CategoryScore objects applying category penalty caps
    category_scores: Dict[FindingCategory, CategoryScore] = {}
    total_score = 0
    critical_count = sum(1 for f in findings if f.severity == "critical")

    for cat_key, config in CATEGORY_CONFIG.items():
        weight = config["weight"]
        max_penalty = config["max_penalty"]
        raw_deductions = category_deductions.get(cat_key, 0)  # type: ignore
        effective_deduction = min(raw_deductions, max_penalty)
        cat_score = max(0, weight - effective_deduction)

        category_scores[cat_key] = CategoryScore(  # type: ignore
            category=cat_key,  # type: ignore
            name=config["name"],
            weight=weight,
            score=cat_score,
            deductions=effective_deduction,
            max_penalty=max_penalty,
            findings_count=category_finding_counts.get(cat_key, 0),  # type: ignore
        )
        total_score += cat_score

    # Clamp total score strictly between 0 and 100
    final_score = max(0, min(100, total_score))
    label = get_readiness_label(final_score)
    summary_msg = get_summary_message(final_score, label, critical_count)

    return final_score, label, summary_msg, category_scores
