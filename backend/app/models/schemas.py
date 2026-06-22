"""Pydantic response/request schemas for dashboard API."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FindingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    severity: str
    category: str
    file_path: str
    line_number: Optional[int]
    issue_text: str
    attack_scenario: Optional[str]
    fix_suggestion: Optional[str]
    confidence: float
    github_comment_id: Optional[int]
    created_at: datetime


class PullRequestReviewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repo_id: UUID
    pr_number: int
    head_sha: str
    pr_title: str
    intent_summary: Optional[str]
    reasoning_summary: Optional[str]
    score: Optional[float]
    grade: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    findings: List[FindingSchema] = []


class RepositorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner: str
    name: str
    installation_id: int
    health_score: Optional[float]
    created_at: datetime
    pull_requests: List[PullRequestReviewSchema] = []


class FeedbackSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    finding_id: UUID
    action: str
    created_at: datetime
