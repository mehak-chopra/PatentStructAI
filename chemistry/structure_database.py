"""
In-memory molecular structure database used by PatentStructAI.

This module stores recognized chemical structures together with
their canonical representations and fingerprints so they can be
searched efficiently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from chemistry.recognition_result import RecognitionResult
from chemistry.canonicalizer import CanonicalizationResult
from chemistry.fingerprints import FingerprintResult


# ------------------------------------------------------------------
# Structure Record
# ------------------------------------------------------------------

@dataclass(frozen=True)
class StructureRecord:
    """
    Represents one indexed chemical structure.

    A record combines the outputs of every stage of the
    chemistry pipeline into one searchable object.
    """

    # ------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------

    structure_id: str

    patent_id: Optional[str] = None

    page_number: Optional[int] = None

    image_path: Optional[Path] = None

    # ------------------------------------------------------------
    # Chemistry Pipeline
    # ------------------------------------------------------------

    recognition: Optional[RecognitionResult] = None

    canonicalization: Optional[CanonicalizationResult] = None

    fingerprint: Optional[FingerprintResult] = None

    # ------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)


    # ------------------------------------------------------------
    # Recognition Shortcuts
    # ------------------------------------------------------------

    @property
    def smiles(self) -> Optional[str]:
        """
        Return the recognized SMILES string.
        """
        if self.recognition is None:
            return None

        return self.recognition.smiles


    @property
    def canonical_smiles(self) -> Optional[str]:
        """
        Return the canonical SMILES string.
        """
        if self.canonicalization is None:
            return None

        return self.canonicalization.canonical_smiles


    @property
    def rdkit_molecule(self):
        """
        Return the RDKit molecule.
        """
        if self.canonicalization is None:
            return None

        return self.canonicalization.rdkit_molecule


    @property
    def recognition_confidence(self) -> Optional[float]:
        """
        Recognition confidence reported by the OCR model.
        """
        if self.recognition is None:
            return None

        return self.recognition.recognition_confidence


    @property
    def inference_time(self) -> Optional[float]:
        """
        Recognition inference time.
        """
        if self.recognition is None:
            return None

        return self.recognition.inference_time


    # ------------------------------------------------------------
    # Fingerprint Shortcuts
    # ------------------------------------------------------------

    @property
    def has_fingerprint(self) -> bool:
        """
        True if a searchable fingerprint exists.
        """
        return (
            self.fingerprint is not None
            and self.fingerprint.searchable
        )


    @property
    def fingerprint_vector(self):
        """
        Return the NumPy fingerprint vector.
        """
        if self.fingerprint is None:
            return None

        return self.fingerprint.bit_vector


    @property
    def fingerprint_hash(self) -> Optional[str]:
        """
        Stable fingerprint hash.
        """
        if self.fingerprint is None:
            return None

        return self.fingerprint.fingerprint_hash


    # ------------------------------------------------------------
    # Search Properties
    # ------------------------------------------------------------

    @property
    def searchable(self) -> bool:
        """
        True if this structure is ready for searching.
        """

        return (
            self.recognition is not None
            and self.recognition.searchable
            and self.canonicalization is not None
            and self.canonicalization.searchable
            and self.has_fingerprint
        )


    @property
    def filename(self) -> Optional[str]:
        """
        Image filename.
        """

        if self.image_path is None:
            return None

        return self.image_path.name


    @property
    def has_patent(self) -> bool:
        """
        True if the record belongs to a patent.
        """

        return self.patent_id is not None


    @property
    def has_page(self) -> bool:
        """
        True if a page number is available.
        """

        return self.page_number is not None



# ------------------------------------------------------------------
# Structure Database
# ------------------------------------------------------------------

class StructureDatabase:
    """
    In-memory collection of StructureRecord objects.

    This class acts as the central repository for all recognized
    chemical structures before they are searched or persisted.
    """

    def __init__(self) -> None:
        """
        Initialize an empty structure database.
        """

        self._records: dict[str, StructureRecord] = {}

    @property
    def size(self) -> int:
        """
        Number of records stored in the database.
        """

        return len(self._records)

    def __len__(self) -> int:
        return self.size

    def __iter__(self):
        """
        Iterate over all stored StructureRecord objects.
        """

        return iter(self._records.values())

    def __contains__(self, structure_id: str) -> bool:
        """
        Allow:

            if "ABC123" in database:
                ...
        """

        return structure_id in self._records

    # ------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------

    def add(self, record: StructureRecord) -> None:
        """
        Add a structure record to the database.

        Existing records with the same structure ID
        are replaced.
        """

        self._records[record.structure_id] = record


    def add_many(
        self,
        records: list[StructureRecord],
    ) -> None:
        """
        Add multiple structure records.
        """

        for record in records:
            self.add(record)


    def get(
        self,
        structure_id: str,
    ) -> Optional[StructureRecord]:
        """
        Retrieve a structure by its ID.

        Returns None if the structure does not exist.
        """

        return self._records.get(structure_id)


    def exists(
        self,
        structure_id: str,
    ) -> bool:
        """
        Check whether a structure exists.
        """

        return structure_id in self._records


    def remove(
        self,
        structure_id: str,
    ) -> Optional[StructureRecord]:
        """
        Remove a structure from the database.

        Returns the removed record or None.
        """

        return self._records.pop(
            structure_id,
            None,
        )


    def clear(self) -> None:
        """
        Remove all stored structures.
        """

        self._records.clear()


    # ------------------------------------------------------------
    # Database Views
    # ------------------------------------------------------------

    def all(self) -> list[StructureRecord]:
        """
        Return all stored structure records.
        """

        return list(self._records.values())


    def searchable(self) -> list[StructureRecord]:
        """
        Return only searchable structures.
        """

        return [
            record
            for record in self._records.values()
            if record.searchable
        ]


    def fingerprints(self) -> list[FingerprintResult]:
        """
        Return all searchable fingerprints.
        """

        return [
            record.fingerprint
            for record in self.searchable()
            if record.fingerprint is not None
        ]


    def canonical_smiles(self) -> list[str]:
        """
        Return all canonical SMILES.
        """

        return [
            record.canonical_smiles
            for record in self.searchable()
            if record.canonical_smiles is not None
        ]


    def patent_ids(self) -> list[str]:
        """
        Return every unique patent ID.
        """

        return sorted(
            {
                record.patent_id
                for record in self._records.values()
                if record.patent_id is not None
            }
        )


    def structure_ids(self) -> list[str]:
        """
        Return every stored structure ID.
        """

        return list(self._records.keys())


        # ------------------------------------------------------------
    # Filtering Helpers
    # ------------------------------------------------------------

    def by_patent(
        self,
        patent_id: str,
    ) -> list[StructureRecord]:
        """
        Return all structures belonging to one patent.
        """

        return [
            record
            for record in self._records.values()
            if record.patent_id == patent_id
        ]


    def by_page(
        self,
        page_number: int,
    ) -> list[StructureRecord]:
        """
        Return all structures from a page.
        """

        return [
            record
            for record in self._records.values()
            if record.page_number == page_number
        ]


    def by_filename(
        self,
        filename: str,
    ) -> Optional[StructureRecord]:
        """
        Find a structure by image filename.
        """

        for record in self._records.values():

            if record.filename == filename:
                return record

        return None


    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    def statistics(self) -> Dict[str, Any]:
        """
        Return basic statistics describing the database.
        """

        searchable = self.searchable()

        return {
            "total_structures": self.size,
            "searchable_structures": len(searchable),
            "non_searchable_structures": (
                self.size - len(searchable)
            ),
            "unique_patents": len(self.patent_ids()),
            "unique_pages": len(
                {
                    record.page_number
                    for record in self._records.values()
                    if record.page_number is not None
                }
            ),
        }


    def summary(self) -> Dict[str, Any]:
        """
        Return a lightweight summary of the database.
        """

        stats = self.statistics()

        return {
            **stats,
            "structure_ids": self.structure_ids(),
        }


    # ------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------

    def __str__(self) -> str:
        """
        Human-readable representation.
        """

        stats = self.statistics()

        return (
            "StructureDatabase("
            f"structures={stats['total_structures']}, "
            f"searchable={stats['searchable_structures']}, "
            f"patents={stats['unique_patents']}"
            ")"
        )


    def __repr__(self) -> str:
        return self.__str__()