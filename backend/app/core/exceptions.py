"""Custom exception classes used across CodeSentinel."""
from __future__ import annotations


class WebhookValidationError(Exception):
    def __init__(self, received_sig: str | None, expected_sig: str | None) -> None:
        self.received_sig = received_sig
        self.expected_sig = expected_sig
        super().__init__("Invalid webhook signature")


class GitHubAPIError(Exception):
    def __init__(self, status_code: int, endpoint: str, rate_limit_reset: int | None = None) -> None:
        self.status_code = status_code
        self.endpoint = endpoint
        self.rate_limit_reset = rate_limit_reset
        super().__init__(f"GitHub API error {status_code} at {endpoint}")


class AIReviewError(Exception):
    def __init__(self, chunk_index: int, raw_output: str, attempts_made: int) -> None:
        self.chunk_index = chunk_index
        self.raw_output = raw_output
        self.attempts_made = attempts_made
        super().__init__("AI review failed to return valid JSON")


class DiffProcessingError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Diff processing failed: {reason}")


class RateLimitExceededError(Exception):
    def __init__(self, org_name: str, reset_at: int, current_count: int) -> None:
        self.org_name = org_name
        self.reset_at = reset_at
        self.current_count = current_count
        super().__init__(f"Rate limit exceeded for {org_name}")


class IntentExtractionError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)
