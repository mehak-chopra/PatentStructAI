"""
SMILES extraction pipeline for PatentStructAI.

This module orchestrates molecular recognition,
canonicalization and fingerprint generation into a
single reusable pipeline.

It is intentionally independent from patent parsing
and database indexing.
"""

from __future__ import annotations

import time

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Optional

from chemistry.recognition_result import RecognitionResult

from chemistry.canonicalizer import (
    CanonicalizationResult,
    Canonicalizer,
)

from chemistry.fingerprints import (
    FingerprintGenerator,
    FingerprintResult,
)

from chemistry.structure_database import (
    StructureRecord,
)

from chemistry.recognizers.base import (
    BaseRecognizer,
)



# ------------------------------------------------------------------
# SMILES Extraction Result
# ------------------------------------------------------------------

@dataclass(frozen=True)
class SMILESExtractionResult:
    """
    Complete output of the chemistry extraction pipeline.
    """

    # ------------------------------------------------------------
    # Input
    # ------------------------------------------------------------

    image_path: Optional[Path] = None

    # ------------------------------------------------------------
    # Intermediate Results
    # ------------------------------------------------------------

    recognition: Optional[RecognitionResult] = None

    canonicalization: Optional[
        CanonicalizationResult
    ] = None

    fingerprint: Optional[
        FingerprintResult
    ] = None

    structure: Optional[
        StructureRecord
    ] = None

    # ------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------

    elapsed_time: float = 0.0

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
    # Properties
    # ------------------------------------------------------------

    @property
    def has_recognition(self) -> bool:
        return self.recognition is not None


    @property
    def has_canonicalization(self) -> bool:
        return self.canonicalization is not None


    @property
    def has_fingerprint(self) -> bool:
        return self.fingerprint is not None


    @property
    def has_structure(self) -> bool:
        return self.structure is not None


    @property
    def searchable(self) -> bool:
        """
        True if the pipeline produced a searchable structure.
        """

        return (
            self.success
            and self.has_structure
            and self.structure.searchable
        )


    @property
    def has_error(self) -> bool:
        return self.error is not None


    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:

        return {
            "success": self.success,
            "image": (
                str(self.image_path)
                if self.image_path is not None
                else None
            ),
            "recognition": self.has_recognition,
            "canonicalization": self.has_canonicalization,
            "fingerprint": self.has_fingerprint,
            "structure": self.has_structure,
            "searchable": self.searchable,
            "elapsed_time": round(
                self.elapsed_time,
                4,
            ),
            "error": self.error,
        }


    def __str__(self) -> str:
        return (
            "SMILESExtractionResult("
            f"success={self.success}, "
            f"searchable={self.searchable})"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "SMILESExtractionResult":

        return replace(
            self,
            metadata={
                **self.metadata,
                **metadata,
            },
        )


    def with_error(
        self,
        message: str,
    ) -> "SMILESExtractionResult":

        return replace(
            self,
            success=False,
            error=message,
        )



# ------------------------------------------------------------------
# SMILES Extractor
# ------------------------------------------------------------------

class SMILESExtractor:
    """
    High-level chemistry extraction pipeline.

    This class orchestrates:

        Image
            ↓
        Molecular Recognition
            ↓
        Canonicalization
            ↓
        Fingerprint Generation
            ↓
        StructureRecord
    """

    def __init__(
        self,
        recognizer: BaseRecognizer,
    ) -> None:
        """
        Parameters
        ----------
        recognizer:
            Molecular image recognizer
            (MolNexTR, MolScribe, etc.)
        """

        self.recognizer = recognizer

        self._num_processed = 0

        self._num_successful = 0

        self._total_runtime = 0.0


    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    @property
    def recognizer_name(self) -> str:
        """
        Name of the underlying recognizer.
        """

        return self.recognizer.name


    @property
    def processed(self) -> int:
        """
        Number of processed structures.
        """

        return self._num_processed


    @property
    def successful(self) -> int:
        """
        Number of successful extractions.
        """

        return self._num_successful


    @property
    def failed(self) -> int:
        """
        Number of failed extractions.
        """

        return (
            self.processed
            - self.successful
        )


    @property
    def success_rate(self) -> float:
        """
        Pipeline success rate.
        """

        if self.processed == 0:
            return 0.0

        return round(
            self.successful
            / self.processed,
            4,
        )


    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    def statistics(self) -> Dict[str, Any]:
        """
        Return pipeline statistics.
        """

        average = 0.0

        if self.processed > 0:

            average = (
                self._total_runtime
                / self.processed
            )

        return {
            "recognizer": self.recognizer_name,
            "processed": self.processed,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "average_runtime": round(
                average,
                4,
            ),
        }


    # ------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------

    def __str__(self) -> str:

        stats = self.statistics()

        return (
            "SMILESExtractor("
            f"recognizer='{stats['recognizer']}', "
            f"processed={stats['processed']}, "
            f"success_rate={stats['success_rate']:.2%}"
            ")"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Core Extraction
    # ------------------------------------------------------------

    def extract_from_path(
        self,
        image_path: str | Path,
        *,
        patent_id: Optional[str] = None,
        page_number: Optional[int] = None,
        structure_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SMILESExtractionResult:
        """
        Extract a searchable StructureRecord from an image.
        """

        start_time = time.perf_counter()

        image_path = Path(image_path)

        metadata = metadata or {}

        self._num_processed += 1

        # --------------------------------------------------------
        # Recognition
        # --------------------------------------------------------

        recognition = self.recognizer.predict(
            image_path,
        )

        if not recognition.searchable:

            self._total_runtime += (
                time.perf_counter() - start_time
            )

            return SMILESExtractionResult(
                image_path=image_path,
                recognition=recognition,
                elapsed_time=time.perf_counter() - start_time,
                success=False,
                error=recognition.error,
                metadata=metadata,
            )

        # --------------------------------------------------------
        # Canonicalization
        # --------------------------------------------------------

        canonical = Canonicalizer.canonicalize(
            recognition.smiles,
        )

        if not canonical.searchable:

            self._total_runtime += (
                time.perf_counter() - start_time
            )

            return SMILESExtractionResult(
                image_path=image_path,
                recognition=recognition,
                canonicalization=canonical,
                elapsed_time=time.perf_counter() - start_time,
                success=False,
                error=canonical.error,
                metadata=metadata,
            )

        # --------------------------------------------------------
        # Fingerprint
        # --------------------------------------------------------

        fingerprint = FingerprintGenerator.from_rdkit(
            molecule=canonical.rdkit_molecule,
            canonical_smiles=canonical.canonical_smiles,
        )

        if not fingerprint.searchable:

            self._total_runtime += (
                time.perf_counter() - start_time
            )

            return SMILESExtractionResult(
                image_path=image_path,
                recognition=recognition,
                canonicalization=canonical,
                fingerprint=fingerprint,
                elapsed_time=time.perf_counter() - start_time,
                success=False,
                error=fingerprint.error,
                metadata=metadata,
            )


        # --------------------------------------------------------
        # Structure Record
        # --------------------------------------------------------

        structure = StructureRecord(
            structure_id=structure_id,
            patent_id=patent_id,
            page_number=page_number,
            image_path=image_path,
            recognition=recognition,
            canonicalization=canonical,
            fingerprint=fingerprint,
            metadata=metadata,
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        self._total_runtime += elapsed

        self._num_successful += 1

        return SMILESExtractionResult(
            image_path=image_path,
            recognition=recognition,
            canonicalization=canonical,
            fingerprint=fingerprint,
            structure=structure,
            elapsed_time=elapsed,
            success=True,
            metadata=metadata,
        )


    # ------------------------------------------------------------
    # Batch Extraction
    # ------------------------------------------------------------

    def extract_batch(
        self,
        image_paths: List[str | Path],
        *,
        patent_id: Optional[str] = None,
        page_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SMILESExtractionResult]:
        """
        Extract molecules from multiple images.

        Parameters
        ----------
        image_paths:
            Collection of molecular structure images.

        Returns
        -------
        List[SMILESExtractionResult]
        """

        results: List[
            SMILESExtractionResult
        ] = []

        for index, image_path in enumerate(
            image_paths,
            start=1,
        ):

            result = self.extract_from_path(
                image_path=image_path,
                patent_id=patent_id,
                page_number=page_number,
                structure_id=f"STR{index:06d}",
                metadata=metadata,
            )

            results.append(result)

        return results


    # ------------------------------------------------------------
    # Batch Summary
    # ------------------------------------------------------------

    @staticmethod
    def summarize_batch(
        results: List[SMILESExtractionResult],
    ) -> Dict[str, Any]:
        """
        Summarize a batch extraction.
        """

        total = len(results)

        successful = sum(
            result.success
            for result in results
        )

        searchable = sum(
            result.searchable
            for result in results
        )

        failed = total - successful

        average_runtime = 0.0

        if total > 0:

            average_runtime = (
                sum(
                    result.elapsed_time
                    for result in results
                )
                / total
            )

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "searchable": searchable,
            "average_runtime": round(
                average_runtime,
                4,
            ),
        }


    # ------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------

    def reset_statistics(self) -> None:
        """
        Reset runtime statistics.

        Useful when benchmarking multiple datasets using
        the same extractor instance.
        """

        self._num_processed = 0

        self._num_successful = 0

        self._total_runtime = 0.0


    @staticmethod
    def create_failed(
        message: str,
        image_path: Optional[str | Path] = None,
    ) -> SMILESExtractionResult:
        """
        Create a failed extraction result.
        """

        return SMILESExtractionResult(
            image_path=(
                Path(image_path)
                if image_path is not None
                else None
            ),
            success=False,
            error=message,
        )


# ------------------------------------------------------------------
# Public Exports
# ------------------------------------------------------------------

__all__ = [
    "SMILESExtractionResult",
    "SMILESExtractor",
]