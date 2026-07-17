"""
PatentStructAI Search Result Models.

Every search algorithm returns SearchResult objects.

This keeps Exact Search, Similarity Search and
Substructure Search completely interchangeable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================================
# Search Type
# ============================================================

class SearchType(str, Enum):
    """
    Type of search that produced the result.
    """

    EXACT = "exact"

    SUBSTRUCTURE = "substructure"

    SIMILARITY = "similarity"


# ============================================================
# Search Result
# ============================================================

@dataclass
class SearchResult:
    """
    Represents one searchable chemical structure.
    """

    # ------------------------------------------
    # Patent Information
    # ------------------------------------------

    patent_id: int

    patent_number: str

    patent_title: str

    country: str


    # ------------------------------------------
    # Structure Information
    # ------------------------------------------

    structure_id: int

    page_number: int

    crop_index: int

    image_path: str


    # ------------------------------------------
    # Chemistry
    # ------------------------------------------

    smiles: str

    canonical_smiles: str

    fingerprint_hash: Optional[str] = None


    # ------------------------------------------
    # Search Information
    # ------------------------------------------

    search_type: SearchType = SearchType.EXACT

    matched_by: set[SearchType] = field(
        default_factory=set
    )

    similarity_score: float = 1.0

    searchable: bool = True


    # ------------------------------------------
    # Recognition Metadata
    # ------------------------------------------

    recognizer_name: Optional[str] = None

    recognizer_version: Optional[str] = None

    recognizer_confidence: Optional[float] = None

    backend: Optional[str] = None

    inference_time: Optional[float] = None


    # ========================================================
    # Display
    # ========================================================

    @property
    def display_name(
        self,
    ) -> str:
        """
        Human-readable display name.
        """

        return (

            f"{self.patent_number}"

            f" | Page {self.page_number}"

            f" | {self.search_type.value.title()}"

        )


    # ========================================================
    # Ranking
    # ========================================================

    @property
    def ranking_score(
        self,
    ) -> float:
        """
        Unified ranking score.

        Exact Search
            1.0

        Similarity Search
            similarity score

        Substructure Search
            0.95

        Can later be expanded to include
        recognizer confidence, citation count,
        patent quality, etc.
        """

        if self.search_type == SearchType.EXACT:

            return 1.0

        if self.search_type == SearchType.SUBSTRUCTURE:

            return 0.95

        return self.similarity_score


    # ========================================================
    # Deduplication
    # ========================================================

    @property
    def unique_key(
        self,
    ) -> tuple:
        """
        Unique identifier used when merging
        search results.
        """

        return (

            self.patent_id,

            self.structure_id,

        )


    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Convert into a JSON-friendly dictionary.
        """

        return {

            "patent_id": self.patent_id,

            "patent_number": self.patent_number,

            "patent_title": self.patent_title,

            "country": self.country,

            "structure_id": self.structure_id,

            "page_number": self.page_number,

            "crop_index": self.crop_index,

            "image_path": self.image_path,

            "smiles": self.smiles,

            "canonical_smiles": self.canonical_smiles,

            "fingerprint_hash": self.fingerprint_hash,

            "search_type": self.search_type.value,

            "similarity_score": self.similarity_score,

            "searchable": self.searchable,

            "recognizer_name": self.recognizer_name,

            "recognizer_version": self.recognizer_version,

            "recognizer_confidence": self.recognizer_confidence,

            "backend": self.backend,

            "inference_time": self.inference_time,

        }


    # ========================================================
    # Sorting
    # ========================================================

    def __lt__(
        self,
        other,
    ):
        """
        Enables:

        sorted(results, reverse=True)

        Highest ranked result appears first.
        """

        return (

            self.ranking_score

            <

            other.ranking_score

        )


    # ========================================================
    # String Representation
    # ========================================================

    def __str__(
        self,
    ) -> str:

        return (

            f"{self.patent_number}"

            f" | "

            f"{self.search_type.value}"

            f" | "

            f"{self.similarity_score:.3f}"

        )