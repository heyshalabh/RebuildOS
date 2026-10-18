from app.core.scoring import calculate_readiness_score, get_readiness_label
from app.models.schemas import Finding


def test_perfect_score():
    score, label, msg, cat_scores = calculate_readiness_score([])
    assert score == 100
    assert label == "Strong"
    for cat_name, cat in cat_scores.items():
        assert cat.score == cat.weight
        assert cat.deductions == 0


def test_duplicate_finding_deduplication():
    # Adding the identical finding twice should NOT double the penalty
    finding1 = Finding(
        id="PY_NO_LOCKFILE",
        title="Missing lockfile",
        severity="critical",
        category="dependency",
        affected_file="requirements.txt",
        description="test",
        why_it_matters="test",
        recommended_fix="test",
    )
    finding2 = Finding(
        id="PY_NO_LOCKFILE",
        title="Missing lockfile",
        severity="critical",
        category="dependency",
        affected_file="requirements.txt",
        description="test",
        why_it_matters="test",
        recommended_fix="test",
    )

    score_single, _, _, cat_single = calculate_readiness_score([finding1])
    score_double, _, _, cat_double = calculate_readiness_score([finding1, finding2])

    assert score_single == score_double
    assert cat_single["dependency"].deductions == cat_double["dependency"].deductions


def test_category_penalty_capping():
    # Generate 10 critical findings in 'runtime' category (weight 25)
    # 10 * 15 = 150 points deducted, but max_penalty is 25.
    findings = [
        Finding(
            id=f"CRITICAL_RUNTIME_{i}",
            title=f"Critical runtime {i}",
            severity="critical",
            category="runtime",
            affected_file=f"file_{i}.txt",
            description="test",
            why_it_matters="test",
            recommended_fix="test",
        )
        for i in range(10)
    ]
    score, label, msg, cat_scores = calculate_readiness_score(findings)

    # Runtime category cannot drop below 0
    assert cat_scores["runtime"].score == 0
    assert cat_scores["runtime"].deductions == 25
    # Overall score should be 100 - 25 = 75
    assert score == 75


def test_readiness_labels():
    assert get_readiness_label(100) == "Strong"
    assert get_readiness_label(90) == "Strong"
    assert get_readiness_label(89) == "Good"
    assert get_readiness_label(75) == "Good"
    assert get_readiness_label(74) == "Needs work"
    assert get_readiness_label(50) == "Needs work"
    assert get_readiness_label(49) == "High risk"
    assert get_readiness_label(0) == "High risk"
