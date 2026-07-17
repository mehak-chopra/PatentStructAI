"""
Similarity computation utilities for PatentStructAI.

This module provides a unified interface for comparing molecular
fingerprints using multiple similarity metrics.

It is intentionally independent from patents, databases and
recognizers so it can be reused throughout the chemistry engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

from chemistry.fingerprints import (
    FingerprintGenerator,
    FingerprintResult,
)

from chemistry.structure_database import StructureRecord


# ------------------------------------------------------------------
# Similarity Result
# ------------------------------------------------------------------

@dataclass(frozen=True)
class SimilarityResult:
    """
    Immutable container describing the similarity between two molecules.
    """

    # ------------------------------------------------------------
    # Input Fingerprints
    # ------------------------------------------------------------

    query: FingerprintResult

    candidate: StructureRecord

    # ------------------------------------------------------------
    # Similarity Information
    # ------------------------------------------------------------

    similarity_score: float = 0.0

    metric: str = "Tanimoto"

    threshold: float = 0.7

    # ------------------------------------------------------------
    # Status
    # ------------------------------------------------------------

    success: bool = True

    error: Optional[str] = None

    # ------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    @property
    def is_match(self) -> bool:
        """
        Returns True if the similarity score meets or exceeds
        the configured threshold.
        """
        return (
            self.success
            and self.similarity_score >= self.threshold
        )


    @property
    def has_error(self) -> bool:
        """
        Returns True if an error occurred.
        """
        return self.error is not None


    @property
    def has_query(self) -> bool:
        """
        Returns True if the query fingerprint exists.
        """
        return self.query is not None


    @property
    def has_candidate(self) -> bool:
        """
        Returns True if the candidate structure exists.
        """
        return self.candidate is not None


    @property
    def searchable(self) -> bool:
        """
        Returns True if both fingerprints are valid and can
        participate in similarity calculations.
        """
        return (
            self.success
            and self.has_query
            and self.has_candidate
            and self.query.searchable
            and self.candidate.searchable
        )


    @property
    def comparison_ready(self) -> bool:
        """
        Alias used by higher-level search modules.
        """
        return self.searchable


    @property
    def score_percentage(self) -> float:
        """
        Similarity score expressed as a percentage.
        """
        return round(self.similarity_score * 100.0, 2)


    @property
    def distance(self) -> float:
        """
        Distance derived from similarity.

        A perfect match has distance 0.
        """
        return 1.0 - self.similarity_score


    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a lightweight summary of the similarity result.
        """

        return {
            "success": self.success,
            "metric": self.metric,
            "similarity_score": round(self.similarity_score, 4),
            "score_percentage": self.score_percentage,
            "threshold": self.threshold,
            "is_match": self.is_match,
            "patent_id": self.candidate.patent_id,
            "page_number": self.candidate.page_number,
            "structure_id": self.candidate.structure_id,
            "error": self.error,
        }


    # ------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the similarity result into a JSON-serializable
        dictionary.
        """

        return {
            "query": self.query.summary(),
            "candidate": self.candidate.summary(),
            "similarity_score": self.similarity_score,
            "metric": self.metric,
            "threshold": self.threshold,
            "patent_id": self.candidate.patent_id,
            "page_number": self.candidate.page_number,
            "structure_id": self.candidate.structure_id,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


    # ------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"SimilarityResult("
            f"metric='{self.metric}', "
            f"score={self.similarity_score:.4f}, "
            f"match={self.is_match})"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "SimilarityResult":
        """
        Return a new SimilarityResult with updated metadata.
        """

        merged = {**self.metadata, **metadata}

        return replace(
            self,
            metadata=merged,
        )


    def with_error(
        self,
        message: str,
    ) -> "SimilarityResult":
        """
        Return a failed similarity result.
        """

        return replace(
            self,
            success=False,
            error=message,
        )


# ------------------------------------------------------------------
# Similarity Calculator
# ------------------------------------------------------------------

class SimilarityCalculator:
    """
    Utility class for computing molecular similarity.

    This class wraps the similarity functions provided by
    FingerprintGenerator and provides a unified interface
    for future search modules.
    """

    DEFAULT_METRIC = "Tanimoto"

    DEFAULT_THRESHOLD = 0.70


    @staticmethod
    def compare(
        query: FingerprintResult,
        candidate: StructureRecord,
        metric: str = DEFAULT_METRIC,
        threshold: float = DEFAULT_THRESHOLD,
        **metadata: Any,
    ) -> SimilarityResult:
        """
        Compare two fingerprints using the requested metric.

        Supported metrics
        -----------------
        - Tanimoto
        - Dice
        - Cosine
        """

        metric = metric.lower()

        # --------------------------------------------------------
        # Validate fingerprints
        # --------------------------------------------------------

        if (
            not query.searchable
            or not candidate.searchable
        ):
            return SimilarityResult(
                query=query,
                candidate=candidate,
                metric=metric.capitalize(),
                threshold=threshold,
                success=False,
                error="One or both fingerprints are invalid.",
                metadata=metadata,
            )

        if metric == "tanimoto":

            score = FingerprintGenerator.tanimoto(
                query,
                candidate.fingerprint,
            )

        elif metric == "dice":

            score = FingerprintGenerator.dice(
                query,
                candidate.fingerprint,
            )

        elif metric == "cosine":

            score = FingerprintGenerator.cosine(
                query,
                candidate.fingerprint,
            )

        else:

            return SimilarityResult(
                query=query,
                candidate=candidate,
                metric=metric,
                threshold=threshold,
                success=False,
                error=f"Unsupported similarity metric: {metric}",
                metadata=metadata,
            )

        return SimilarityResult(
            query=query,
            candidate=candidate,
            similarity_score=score,
            metric=metric.capitalize(),
            threshold=threshold,
            metadata=metadata,
        )


    # ------------------------------------------------------------
    # Convenience Comparison Methods
    # ------------------------------------------------------------

    @staticmethod
    def tanimoto(
        query: FingerprintResult,
        candidate: StructureRecord,
        threshold: float = DEFAULT_THRESHOLD,
        **metadata: Any,
    ) -> SimilarityResult:
        """
        Compare two fingerprints using the Tanimoto metric.
        """

        return SimilarityCalculator.compare(
            query=query,
            candidate=candidate,
            metric="Tanimoto",
            threshold=threshold,
            **metadata,
        )


    @staticmethod
    def dice(
        query: FingerprintResult,
        candidate: StructureRecord,
        threshold: float = DEFAULT_THRESHOLD,
        **metadata: Any,
    ) -> SimilarityResult:
        """
        Compare two fingerprints using the Dice metric.
        """

        return SimilarityCalculator.compare(
            query=query,
            candidate=candidate,
            metric="Dice",
            threshold=threshold,
            **metadata,
        )


    @staticmethod
    def cosine(
        query: FingerprintResult,
        candidate: StructureRecord,
        threshold: float = DEFAULT_THRESHOLD,
        **metadata: Any,
    ) -> SimilarityResult:
        """
        Compare two fingerprints using the Cosine metric.
        """

        return SimilarityCalculator.compare(
            query=query,
            candidate=candidate,
            metric="Cosine",
            threshold=threshold,
            **metadata,
        )


    @staticmethod
    def is_similar(
        query: FingerprintResult,
        candidate: FingerprintResult,
        threshold: float = DEFAULT_THRESHOLD,
        metric: str = DEFAULT_METRIC,
    ) -> bool:
        """
        Return True if two molecules are considered similar.
        """

        result = SimilarityCalculator.compare(
            query=query,
            candidate=candidate,
            metric=metric,
            threshold=threshold,
        )

        return result.is_match


    # ------------------------------------------------------------
    # Batch Utilities
    # ------------------------------------------------------------

    @staticmethod
    def compare_batch(
        query: FingerprintResult,
        candidates: list[FingerprintResult],
        metric: str = DEFAULT_METRIC,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> list[SimilarityResult]:
        """
        Compare one query fingerprint against multiple candidates.
        """

        results = []

        for candidate in candidates:

            results.append(
                SimilarityCalculator.compare(
                    query=query,
                    candidate=candidate,
                    metric=metric,
                    threshold=threshold,
                )
            )

        return results


    @staticmethod
    def sort_by_similarity(
        results: list[SimilarityResult],
        descending: bool = True,
    ) -> list[SimilarityResult]:
        """
        Sort similarity results by similarity score.
        """

        return sorted(
            results,
            key=lambda result: result.similarity_score,
            reverse=descending,
        )


    @staticmethod
    def best_match(
        query: FingerprintResult,
        candidates: list[FingerprintResult],
        metric: str = DEFAULT_METRIC,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> Optional[SimilarityResult]:
        """
        Return the single most similar molecule.
        """

        results = SimilarityCalculator.compare_batch(
            query=query,
            candidates=candidates,
            metric=metric,
            threshold=threshold,
        )

        if not results:
            return None

        return max(
            results,
            key=lambda result: result.similarity_score,
        )


    @staticmethod
    def filter_matches(
        results: list[SimilarityResult],
    ) -> list[SimilarityResult]:
        """
        Keep only results that satisfy the similarity threshold.
        """

        return [
            result
            for result in results
            if result.is_match
        ]