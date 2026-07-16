"""
Database models used by the repository layer.

These immutable dataclasses represent rows stored in the
PatentStructAI database.

They are intentionally independent of SQLAlchemy ORM.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# =====================================================
# Patent
# =====================================================

@dataclass(frozen=True)
class PatentRecord:
    """
    Represents one row in the patents table.
    """

    id: Optional[int] = None

    patent_number: str = ""

    title: Optional[str] = None

    pdf_url: Optional[str] = None

    country: Optional[str] = None

    pdf_downloaded: bool = False

    pdf_available: bool = True

    images_extracted: bool = False

    structures_extracted: bool = False

    processed: bool = False

    local_pdf_path: Optional[str] = None

    file_size: Optional[int] = None

    download_time: Optional[datetime] = None

    processing_started_at: Optional[datetime] = None

    processed_at: Optional[datetime] = None

    download_error: Optional[str] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


# =====================================================
# Patent Page
# =====================================================

@dataclass(frozen=True)
class PatentPageRecord:
    """
    Represents one rendered patent page.
    """

    id: Optional[int] = None

    patent_id: int = 0

    page_number: int = 0

    image_path: Optional[str] = None

    contains_chemistry: Optional[bool] = None

    chemistry_score: Optional[float] = None

    classifier_name: Optional[str] = None

    classifier_version: Optional[str] = None

    classification_time: Optional[float] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None


# =====================================================
# Structure
# =====================================================

@dataclass(frozen=True)
class StructureRecordDB:
    """
    Represents one searchable molecular structure stored
    in the database.

    Named StructureRecordDB to avoid clashing with the
    chemistry.pipeline StructureRecord.
    """

    id: Optional[int] = None

    patent_id: int = 0

    page_number: Optional[int] = None

    crop_index: Optional[int] = None

    image_path: Optional[str] = None

    smiles: Optional[str] = None

    canonical_smiles: Optional[str] = None

    molblock: Optional[str] = None

    fingerprint_hash: Optional[str] = None

    recognizer_name: Optional[str] = None

    recognizer_version: Optional[str] = None

    recognizer_confidence: Optional[float] = None

    backend: Optional[str] = None

    inference_time: Optional[float] = None

    pipeline_time: Optional[float] = None

    recognition_success: bool = False

    failure_reason: Optional[str] = None

    searchable: bool = False

    created_at: Optional[datetime] = None