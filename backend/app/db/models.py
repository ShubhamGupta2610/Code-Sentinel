"""SQLAlchemy ORM models for CodeSentinel."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ReviewStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class Severity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    INFO = "INFO"


class FeedbackAction(str, enum.Enum):
    accepted = "accepted"
    dismissed = "dismissed"


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)
    installation_id = Column(Integer, nullable=False)
    health_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pull_requests = relationship("PullRequestReview", back_populates="repository")


class PullRequestReview(Base):
    __tablename__ = "pull_request_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    head_sha = Column(String, nullable=False)
    pr_title = Column(String, nullable=False)
    intent_summary = Column(Text, nullable=True)
    reasoning_summary = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    grade = Column(String, nullable=True)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.pending, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    repository = relationship("Repository", back_populates="pull_requests")
    findings = relationship("Finding", back_populates="review", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("pull_request_reviews.id"), nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    category = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=True)
    issue_text = Column(Text, nullable=False)
    attack_scenario = Column(Text, nullable=True)
    fix_suggestion = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    github_comment_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    review = relationship("PullRequestReview", back_populates="findings")
    feedback = relationship("Feedback", back_populates="finding", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id = Column(UUID(as_uuid=True), ForeignKey("findings.id"), nullable=False)
    action = Column(Enum(FeedbackAction), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    finding = relationship("Finding", back_populates="feedback")