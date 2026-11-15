from remote_job_radar.scorer import calculate_compatibility_score


def test_scores_high_for_compatible_job():
    job = {
        "title": "Technical Support Engineer L2",
        "description": (
            "Work with Microsoft 365, Exchange Online, Microsoft Teams, "
            "Active Directory, incident management and troubleshooting."
        ),
        "location": "Remote - Brazil",
        "worldwide": False,
    }

    score, reasons = calculate_compatibility_score(job)

    assert score >= 70
    assert reasons


def test_scores_low_for_non_support_role():
    job = {
        "title": "Senior Software Engineer",
        "description": "Build distributed systems in Go and Kubernetes.",
        "location": "Remote - Europe",
        "worldwide": False,
    }

    score, _ = calculate_compatibility_score(job)

    assert score < 70
