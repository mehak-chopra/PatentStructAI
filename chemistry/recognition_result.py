"""
Recognition result object used throughout the PatentStructAI chemistry pipeline.

Every molecular image recognizer (MolNexTR, MolScribe, future models)
must return this object so that downstream modules remain independent
from the OCR implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RecognitionResult:
    """
    Immutable container representing the output of a molecular
    image recognition model.
    """

    # ------------------------------------------------------------------
    # Input Information
    # ------------------------------------------------------------------

    image_path: Path

    patent_id: Optional[str] = None

    page_number: Optional[int] = None

    recognizer: str = "Unknown"

    recognizer_version: Optional[str] = None

    # ------------------------------------------------------------------
    # Recognition Output
    # ------------------------------------------------------------------

    smiles: Optional[str] = None

    canonical_smiles: Optional[str] = None

    molblock: Optional[str] = None

    atoms: List[Dict[str, Any]] = field(default_factory=list)

    bonds: List[Dict[str, Any]] = field(default_factory=list)

    recognition_confidence: Optional[float] = None

    # ------------------------------------------------------------------
    # Runtime Information
    # ------------------------------------------------------------------

    inference_time: Optional[float] = None

    device: Optional[str] = None

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    success: bool = True

    error: Optional[str] = None

    # ------------------------------------------------------------------
    # Extensibility
    # ------------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)

    artifacts: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validation Properties
    # ------------------------------------------------------------------

    @property
    def has_smiles(self) -> bool:
        """Return True if a predicted SMILES is available."""
        return self.smiles is not None


    @property
    def has_canonical_smiles(self) -> bool:
        """Return True if a canonical SMILES is available."""
        return self.canonical_smiles is not None


    @property
    def has_molblock(self) -> bool:
        """Return True if a MolBlock is available."""
        return self.molblock is not None


    @property
    def has_atoms(self) -> bool:
        """Return True if atom information exists."""
        return len(self.atoms) > 0


    @property
    def has_bonds(self) -> bool:
        """Return True if bond information exists."""
        return len(self.bonds) > 0


    @property
    def has_error(self) -> bool:
        """Return True if an error message exists."""
        return self.error is not None


    @property
    def is_valid(self) -> bool:
        """
        Returns True if the recognition completed successfully
        and produced a valid SMILES.
        """
        return (
            self.success
            and self.has_smiles
            and self.smiles != "<invalid>"
            and not self.has_error
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the recognition result into a JSON-serializable dictionary.
        """

        return {
            "image_path": str(self.image_path),
            "recognizer": self.recognizer,
            "smiles": self.smiles,
            "canonical_smiles": self.canonical_smiles,
            "molblock": self.molblock,
            "atoms": self.atoms,
            "bonds": self.bonds,
            "recognition_confidence": self.recognition_confidence,
            "inference_time": self.inference_time,
            "device": self.device,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "artifacts": self.artifacts,
            "patent_id": self.patent_id,
            "page_number": self.page_number,
            "recognizer_version": self.recognizer_version
        }


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecognitionResult":
        """
        Reconstruct a RecognitionResult from a dictionary.
        """

        return cls(
            image_path=Path(data["image_path"]),
            recognizer=data.get("recognizer", "Unknown"),
            smiles=data.get("smiles"),
            canonical_smiles=data.get("canonical_smiles"),
            molblock=data.get("molblock"),
            atoms=data.get("atoms", []),
            bonds=data.get("bonds", []),
            recognition_confidence=data.get("recognition_confidence"),
            inference_time=data.get("inference_time"),
            device=data.get("device"),
            success=data.get("success", True),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            artifacts=data.get("artifacts", {}),
            patent_id=data.get("patent_id"),
            page_number=data.get("page_number"),
            recognizer_version=data.get("recognizer_version")
        )
    
    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def filename(self) -> str:
        """Return the image filename."""
        return self.image_path.name


    @property
    def stem(self) -> str:
        """Return the filename without extension."""
        return self.image_path.stem


    @property
    def suffix(self) -> str:
        """Return the file extension."""
        return self.image_path.suffix


    @property
    def parent_directory(self) -> Path:
        """Return the directory containing the image."""
        return self.image_path.parent


    @property
    def num_atoms(self) -> int:
        """Return the number of detected atoms."""
        return len(self.atoms)


    @property
    def num_bonds(self) -> int:
        """Return the number of detected bonds."""
        return len(self.bonds)


    @property
    def has_metadata(self) -> bool:
        """Return True if metadata exists."""
        return bool(self.metadata)


    @property
    def has_artifacts(self) -> bool:
        """Return True if artifacts exist."""
        return bool(self.artifacts)

    # ------------------------------------------------------------------
    # Search Properties
    # ------------------------------------------------------------------

    @property
    def is_canonicalized(self) -> bool:
        """
        Returns True if the molecule has already been canonicalized.
        """
        return self.canonical_smiles is not None


    @property
    def has_patent(self) -> bool:
        """
        Returns True if a patent identifier is available.
        """
        return self.patent_id is not None


    @property
    def has_page_number(self) -> bool:
        """
        Returns True if the source page number is known.
        """
        return self.page_number is not None


    @property
    def searchable(self) -> bool:
        """
        Returns True if this recognition result can be indexed
        for similarity and substructure search.
        """
        return (
            self.success
            and self.has_smiles
            and self.has_atoms
            and self.has_bonds
        )


    @property
    def rdkit_ready(self) -> bool:
        """
        True if this result can be converted into an RDKit molecule.
        """
        return self.has_canonical_smiles


    @property
    def has_confidence(self) -> bool:
        return self.recognition_confidence is not None


    @property
    def has_runtime(self) -> bool:
        return self.inference_time is not None


    @property
    def molecule_size(self) -> int:
        """
        Number of atoms in the recognized molecule.
        """
        return self.num_atoms

    @property
    def image(self) -> str:
        return str(self.image_path)


    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Returns a lightweight summary of the recognition result.
        Useful for logging and debugging.
        """

        return {
            "filename": self.filename,
            "recognizer": self.recognizer,
            "patent_id": self.patent_id,
            "page_number": self.page_number,
            "success": self.success,
            "searchable": self.searchable,
            "smiles": self.smiles,
            "canonical_smiles": self.canonical_smiles,
            "num_atoms": self.num_atoms,
            "num_bonds": self.num_bonds,
            "device": self.device,
            "recognition_confidence": self.recognition_confidence,
            "inference_time": self.inference_time,
        }


    def __str__(self) -> str:
        patent = self.patent_id or "Unknown"
        page = self.page_number if self.page_number is not None else "?"

        return (
            f"RecognitionResult("
            f"patent='{patent}', "
            f"page={page}, "
            f"image='{self.filename}', "
            f"recognizer='{self.recognizer}', "
            f"success={self.success})"
        )


    def __repr__(self) -> str:
        return self.__str__()
    
    # ------------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------------

    def with_canonical_smiles(self, canonical_smiles: str) -> "RecognitionResult":
        """
        Return a new RecognitionResult with the canonical SMILES populated.
        """
        return replace(self, canonical_smiles=canonical_smiles)


    def with_metadata(self, **metadata: Any) -> "RecognitionResult":
        """
        Return a new RecognitionResult with additional metadata.
        """
        merged = {**self.metadata, **metadata}
        return replace(self, metadata=merged)


    def with_artifacts(self, **artifacts: Any) -> "RecognitionResult":
        """
        Return a new RecognitionResult with additional artifacts.
        """
        merged = {**self.artifacts, **artifacts}
        return replace(self, artifacts=merged)


    def with_error(self, message: str) -> "RecognitionResult":
        """
        Return a failed RecognitionResult containing an error message.
        """
        return replace(
            self,
            success=False,
            error=message,
        )


    @classmethod
    def failed(
        cls,
        image_path: Path,
        recognizer: str,
        message: str,
        **kwargs: Any,
    ) -> "RecognitionResult":
        """
        Construct a failed recognition result.
        """

        return cls(
            image_path=image_path,
            recognizer=recognizer,
            success=False,
            error=message,
            **kwargs,
        )