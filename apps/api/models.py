# apps/api/models.py
import uuid, enum
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class SnapshotStatus(str, enum.Enum):
    PENDING = "PENDING"
    CLONING = "CLONING"
    READY = "READY"
    FAILED = "FAILED"

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass

class Snapshot(Base):
    """
    Tracks immutable repository point-in-time commits mapped to physical local disk clones.
    """
    __tablename__ = "snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE")
    )
    commit_sha: Mapped[Optional[str]] = mapped_column(
        String(40), 
        nullable=True, 
        index=True
    )
    branch: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    status: Mapped[SnapshotStatus] = mapped_column(
        String(32), 
        default=SnapshotStatus.PENDING
    )
    storage_path: Mapped[Optional[str]] = mapped_column(
        String(1024), 
        nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    repository: Mapped["Repository"] = relationship(
        "Repository", back_populates="snapshots"
    )

class Repository(Base):
    """
    Represents a source code repository registered in CodeAtlas.
    Stores metadata required to locate, clone, and track index states.
    """
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4,
        comment="Unique identifier for the repository"
    )
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True,
        comment="Human-readable name of the repository"
    )
    url: Mapped[str] = mapped_column(
        String(1024), 
        nullable=False, 
        unique=True,
        comment="Remote Git URL used for cloning"
    )
    default_branch: Mapped[str] = mapped_column(
        String(255), 
        default="main", 
        nullable=False,
        comment="Primary branch to inspect during analysis"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="Optional repository summary"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship to snapshots (defined in Phase 4)
    snapshots: Mapped[List["Snapshot"]] = relationship(
        "Snapshot", 
        back_populates="repository", 
        cascade="all, delete-orphan"
    )