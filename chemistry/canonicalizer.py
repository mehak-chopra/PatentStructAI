"""
Utilities for canonicalizing molecular SMILES.

This module converts raw recognizer output into a standardized
representation that can be safely indexed, searched, and compared.

The canonicalizer is the bridge between molecular recognition
and cheminformatics.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

from rdkit import Chem
from rdkit.Chem.rdchem import Mol


@dataclass(frozen=True)
class CanonicalizationResult:
    """
    Immutable result returned by the Canonicalizer.

    Every successful canonicalization stores both the original
    recognizer output and the RDKit standardized representation.

    The RDKit molecule is intentionally cached here so downstream
    modules (fingerprints, similarity search, substructure search)
    never need to parse the SMILES again.
    """

    # ------------------------------------------------------------
    # Input
    # ------------------------------------------------------------

    original_smiles: Optional[str]

    # ------------------------------------------------------------
    # Canonical Output
    # ------------------------------------------------------------

    canonical_smiles: Optional[str]

    rdkit_molecule: Optional[Mol]

    # ------------------------------------------------------------
    # Status
    # ------------------------------------------------------------

    success: bool = True

    error: Optional[str] = None

    # ------------------------------------------------------------
    # Extra information
    # ------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------
    # Validation Properties
    # ------------------------------------------------------------

    @property
    def has_original_smiles(self) -> bool:
        """
        True if an original SMILES string exists.
        """
        return self.original_smiles is not None


    @property
    def has_canonical_smiles(self) -> bool:
        """
        True if canonicalization produced a SMILES string.
        """
        return self.canonical_smiles is not None


    @property
    def has_rdkit_molecule(self) -> bool:
        """
        True if an RDKit molecule object exists.
        """
        return self.rdkit_molecule is not None


    @property
    def has_error(self) -> bool:
        """
        True if canonicalization produced an error.
        """
        return self.error is not None


    @property
    def is_valid(self) -> bool:
        """
        True if canonicalization completed successfully.
        """
        return (
            self.success
            and self.has_canonical_smiles
            and self.has_rdkit_molecule
            and not self.has_error
        )


    @property
    def searchable(self) -> bool:
        """
        True if this molecule can be indexed for
        similarity and substructure search.
        """
        return self.is_valid


    # ------------------------------------------------------------
    # Molecule Information
    # ------------------------------------------------------------

    @property
    def num_atoms(self) -> int:
        """
        Number of atoms in the RDKit molecule.
        """
        if self.rdkit_molecule is None:
            return 0

        return self.rdkit_molecule.GetNumAtoms()


    @property
    def num_bonds(self) -> int:
        """
        Number of bonds in the RDKit molecule.
        """
        if self.rdkit_molecule is None:
            return 0

        return self.rdkit_molecule.GetNumBonds()


    # ------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the canonicalization result into a JSON-serializable
        dictionary.

        NOTE:
        RDKit molecule objects cannot be serialized directly,
        so they are intentionally omitted.
        """

        return {
            "original_smiles": self.original_smiles,
            "canonical_smiles": self.canonical_smiles,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalizationResult":
        """
        Reconstruct a CanonicalizationResult from a dictionary.

        The RDKit molecule is intentionally left as None.
        It can be recreated later from the canonical SMILES.
        """

        return cls(
            original_smiles=data.get("original_smiles"),
            canonical_smiles=data.get("canonical_smiles"),
            rdkit_molecule=None,
            success=data.get("success", True),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )


    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Lightweight summary useful for logging.
        """

        return {
            "success": self.success,
            "original_smiles": self.original_smiles,
            "canonical_smiles": self.canonical_smiles,
            "num_atoms": self.num_atoms,
            "num_bonds": self.num_bonds,
            "searchable": self.searchable,
            "error": self.error,
        }


    def __str__(self) -> str:
        return (
            f"CanonicalizationResult("
            f"success={self.success}, "
            f"canonical='{self.canonical_smiles}')"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------

    def with_metadata(self, **metadata: Any) -> "CanonicalizationResult":
        """
        Return a new CanonicalizationResult with additional metadata.
        """
        merged = {**self.metadata, **metadata}
        return replace(self, metadata=merged)


    def with_error(self, message: str) -> "CanonicalizationResult":
        """
        Return a failed canonicalization result containing an error.
        """
        return replace(
            self,
            success=False,
            error=message,
            canonical_smiles=None,
            rdkit_molecule=None,
        )


    def with_canonical_smiles(
        self,
        canonical_smiles: str,
        molecule: Mol,
    ) -> "CanonicalizationResult":
        """
        Return a new result populated with a canonical SMILES
        and its RDKit molecule.
        """
        return replace(
            self,
            canonical_smiles=canonical_smiles,
            rdkit_molecule=molecule,
            success=True,
            error=None,
        )


    # ------------------------------------------------------------
    # Factory Methods
    # ------------------------------------------------------------

    @classmethod
    def failed(
        cls,
        original_smiles: Optional[str],
        message: str,
        **metadata: Any,
    ) -> "CanonicalizationResult":
        """
        Construct a failed canonicalization result.
        """

        return cls(
            original_smiles=original_smiles,
            canonical_smiles=None,
            rdkit_molecule=None,
            success=False,
            error=message,
            metadata=metadata,
        )


    @classmethod
    def successful(
        cls,
        original_smiles: str,
        canonical_smiles: str,
        molecule: Mol,
        **metadata: Any,
    ) -> "CanonicalizationResult":
        """
        Construct a successful canonicalization result.
        """

        return cls(
            original_smiles=original_smiles,
            canonical_smiles=canonical_smiles,
            rdkit_molecule=molecule,
            success=True,
            error=None,
            metadata=metadata,
        )


# =============================================================================
# Canonicalizer
# =============================================================================


class Canonicalizer:
    """
    Converts arbitrary molecular SMILES into a standardized
    RDKit canonical representation.

    This class is the gateway between molecular recognition
    and all downstream cheminformatics modules.

    Responsibilities
    ----------------
    • Validate SMILES
    • Create RDKit molecule objects
    • Generate canonical SMILES
    • Handle invalid molecules safely
    • Cache nothing (stateless design)
    """

    @staticmethod
    def canonicalize(smiles: Optional[str]) -> CanonicalizationResult:
        """
        Canonicalize a SMILES string.

        Parameters
        ----------
        smiles:
            Raw SMILES produced by a recognizer.

        Returns
        -------
        CanonicalizationResult
        """

        if smiles is None:
            return CanonicalizationResult.failed(
                original_smiles=None,
                message="No SMILES provided."
            )

        smiles = smiles.strip()

        if not smiles:
            return CanonicalizationResult.failed(
                original_smiles=smiles,
                message="Empty SMILES string."
            )

        try:

            # --------------------------------------------------------
            # Parse molecule
            # --------------------------------------------------------

            molecule = Chem.MolFromSmiles(smiles)

            if molecule is None:
                return CanonicalizationResult.failed(
                    original_smiles=smiles,
                    message="Invalid SMILES."
                )

            # --------------------------------------------------------
            # Generate canonical representation
            # --------------------------------------------------------

            canonical_smiles = Chem.MolToSmiles(
                molecule,
                canonical=True,
                isomericSmiles=True,
            )

            return CanonicalizationResult.successful(
                original_smiles=smiles,
                canonical_smiles=canonical_smiles,
                molecule=molecule,
            )

        except Exception as exc:

            return CanonicalizationResult.failed(
                original_smiles=smiles,
                message=str(exc),
            )


    @staticmethod
    def canonicalize_result(
        recognition_result,
    ) -> CanonicalizationResult:
        """
        Canonicalize a RecognitionResult.

        Convenience wrapper so downstream modules never need
        to manually extract result.smiles.
        """
        raise NotImplementedError


    @staticmethod
    def canonicalize_batch(
        smiles_list: list[str],
    ) -> list[CanonicalizationResult]:
        """
        Canonicalize multiple SMILES.

        Batch processing is useful during patent indexing.
        """
        raise NotImplementedError


    # ------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------

    @staticmethod
    def is_valid_smiles(smiles: Optional[str]) -> bool:
        """
        Check whether a SMILES string is valid.
        """
        if not smiles:
            return False

        return Chem.MolFromSmiles(smiles) is not None


    @staticmethod
    def canonicalize_or_none(smiles: Optional[str]) -> Optional[str]:
        """
        Canonicalize a SMILES string.

        Returns
        -------
        Optional[str]
            Canonical SMILES if successful,
            otherwise None.
        """

        result = Canonicalizer.canonicalize(smiles)

        if result.success:
            return result.canonical_smiles

        return None


    @staticmethod
    def molecule_from_smiles(smiles: Optional[str]) -> Optional[Mol]:
        """
        Convert a SMILES string into an RDKit molecule.

        Returns None if parsing fails.
        """

        if not smiles:
            return None

        return Chem.MolFromSmiles(smiles)