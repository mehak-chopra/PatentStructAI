"""
RDKit utility functions for PatentStructAI.

This module provides a thin abstraction over RDKit so the rest
of the chemistry package does not directly depend on RDKit APIs.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

from rdkit.Chem.rdchem import Mol

from rdkit import Chem
from rdkit.Chem import (
    MolFromSmiles,
    MolFromInchi,
    MolToSmiles,
    MolToInchi,
    MolToInchiKey,
    SaltRemover,
)

from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Descriptors import ExactMolWt


# ------------------------------------------------------------------
# RDKit Result
# ------------------------------------------------------------------

@dataclass(frozen=True)
class RDKitResult:
    """
    Immutable container describing an RDKit molecule and
    associated metadata.
    """

    # ------------------------------------------------------------
    # Molecule
    # ------------------------------------------------------------

    molecule: Optional[Mol] = None

    smiles: Optional[str] = None

    inchi: Optional[str] = None

    inchi_key: Optional[str] = None

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
    def has_molecule(self) -> bool:
        return self.molecule is not None


    @property
    def searchable(self) -> bool:
        return (
            self.success
            and self.has_molecule
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
            "smiles": self.smiles,
            "inchi": self.inchi,
            "inchi_key": self.inchi_key,
            "searchable": self.searchable,
            "error": self.error,
        }


    def __str__(self) -> str:
        return (
            f"RDKitResult("
            f"success={self.success}, "
            f"smiles={self.smiles!r})"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "RDKitResult":
        """
        Return a new RDKitResult with updated metadata.
        """

        merged = {
            **self.metadata,
            **metadata,
        }

        return replace(
            self,
            metadata=merged,
        )


    def with_error(
        self,
        message: str,
    ) -> "RDKitResult":
        """
        Return a failed RDKit result.
        """

        return replace(
            self,
            success=False,
            error=message,
        )



# ------------------------------------------------------------------
# RDKit Utilities
# ------------------------------------------------------------------

class RDKitUtils:
    """
    Thin wrapper around RDKit.

    All chemistry modules should interact with RDKit through this
    class rather than calling RDKit directly.
    """

    # ------------------------------------------------------------
    # Molecule Creation
    # ------------------------------------------------------------

    @staticmethod
    def from_smiles(
        smiles: str,
    ) -> RDKitResult:
        """
        Create an RDKit molecule from a SMILES string.
        """

        if not smiles:

            return RDKitResult(
                smiles=smiles,
                success=False,
                error="No SMILES provided.",
            )

        try:

            molecule = MolFromSmiles(smiles)

            if molecule is None:

                return RDKitResult(
                    smiles=smiles,
                    success=False,
                    error="Invalid SMILES.",
                )

            return RDKitResult(
                molecule=molecule,
                smiles=MolToSmiles(
                    molecule,
                    canonical=True,
                ),
                success=True,
            )

        except Exception as exc:

            return RDKitResult(
                smiles=smiles,
                success=False,
                error=str(exc),
            )


    @staticmethod
    def from_inchi(
        inchi: str,
    ) -> RDKitResult:
        """
        Create an RDKit molecule from an InChI string.
        """

        if not inchi:

            return RDKitResult(
                inchi=inchi,
                success=False,
                error="No InChI provided.",
            )

        try:

            molecule = MolFromInchi(inchi)

            if molecule is None:

                return RDKitResult(
                    inchi=inchi,
                    success=False,
                    error="Invalid InChI.",
                )

            return RDKitResult(
                molecule=molecule,
                smiles=MolToSmiles(
                    molecule,
                    canonical=True,
                ),
                inchi=inchi,
                success=True,
            )

        except Exception as exc:

            return RDKitResult(
                inchi=inchi,
                success=False,
                error=str(exc),
            )


    @staticmethod
    def copy(
        molecule: Mol,
    ) -> Optional[Mol]:
        """
        Return a deep copy of an RDKit molecule.
        """

        if molecule is None:
            return None

        return Chem.Mol(molecule)


    # ------------------------------------------------------------
    # Conversion Utilities
    # ------------------------------------------------------------

    @staticmethod
    def to_smiles(
        molecule: Mol,
        canonical: bool = True,
    ) -> Optional[str]:
        """
        Convert an RDKit molecule to a SMILES string.
        """

        if molecule is None:
            return None

        try:
            return MolToSmiles(
                molecule,
                canonical=canonical,
            )

        except Exception:
            return None


    @staticmethod
    def to_inchi(
        molecule: Mol,
    ) -> Optional[str]:
        """
        Convert an RDKit molecule to an InChI string.
        """

        if molecule is None:
            return None

        try:
            return MolToInchi(molecule)

        except Exception:
            return None


    @staticmethod
    def to_inchi_key(
        molecule: Mol,
    ) -> Optional[str]:
        """
        Convert an RDKit molecule to an InChIKey.
        """

        if molecule is None:
            return None

        try:
            return MolToInchiKey(molecule)

        except Exception:
            return None


    # ------------------------------------------------------------
    # Validation Utilities
    # ------------------------------------------------------------

    @staticmethod
    def is_valid(
        molecule: Optional[Mol],
    ) -> bool:
        """
        Return True if the RDKit molecule is valid.
        """

        return molecule is not None


    @staticmethod
    def sanitize(
        molecule: Mol,
    ) -> RDKitResult:
        """
        Sanitize an RDKit molecule.
        """

        if molecule is None:

            return RDKitResult(
                success=False,
                error="RDKit molecule is None.",
            )

        try:

            Chem.SanitizeMol(molecule)

            return RDKitResult(
                molecule=molecule,
                smiles=RDKitUtils.to_smiles(molecule),
                inchi=RDKitUtils.to_inchi(molecule),
                inchi_key=RDKitUtils.to_inchi_key(molecule),
                success=True,
            )

        except Exception as exc:

            return RDKitResult(
                molecule=molecule,
                success=False,
                error=str(exc),
            )


    # ------------------------------------------------------------
    # Molecular Properties
    # ------------------------------------------------------------

    @staticmethod
    def molecular_formula(
        molecule: Mol,
    ) -> Optional[str]:
        """
        Return the molecular formula.

        Example:
            Ethanol -> C2H6O
        """

        if molecule is None:
            return None

        try:
            return rdMolDescriptors.CalcMolFormula(molecule)

        except Exception:
            return None


    @staticmethod
    def molecular_weight(
        molecule: Mol,
    ) -> Optional[float]:
        """
        Return the exact molecular weight.
        """

        if molecule is None:
            return None

        try:
            return round(
                ExactMolWt(molecule),
                4,
            )

        except Exception:
            return None


    @staticmethod
    def atom_count(
        molecule: Mol,
    ) -> int:
        """
        Return the total number of atoms.
        """

        if molecule is None:
            return 0

        return molecule.GetNumAtoms()


    @staticmethod
    def bond_count(
        molecule: Mol,
    ) -> int:
        """
        Return the total number of bonds.
        """

        if molecule is None:
            return 0

        return molecule.GetNumBonds()


    @staticmethod
    def heavy_atom_count(
        molecule: Mol,
    ) -> int:
        """
        Return the number of heavy atoms.

        Heavy atoms are all atoms except hydrogen.
        """

        if molecule is None:
            return 0

        return molecule.GetNumHeavyAtoms()


    @staticmethod
    def ring_count(
        molecule: Mol,
    ) -> int:
        """
        Return the number of rings in the molecule.
        """

        if molecule is None:
            return 0

        try:
            return rdMolDescriptors.CalcNumRings(
                molecule
            )

        except Exception:
            return 0


    # ------------------------------------------------------------
    # Structure Processing
    # ------------------------------------------------------------

    @staticmethod
    def add_hydrogens(
        molecule: Mol,
    ) -> Optional[Mol]:
        """
        Return a copy of the molecule with explicit hydrogens added.
        """

        if molecule is None:
            return None

        try:
            return Chem.AddHs(
                RDKitUtils.copy(molecule)
            )

        except Exception:
            return None


    @staticmethod
    def remove_hydrogens(
        molecule: Mol,
    ) -> Optional[Mol]:
        """
        Return a copy of the molecule with explicit hydrogens removed.
        """

        if molecule is None:
            return None

        try:
            return Chem.RemoveHs(
                RDKitUtils.copy(molecule)
            )

        except Exception:
            return None


    @staticmethod
    def largest_fragment(
        molecule: Mol,
    ) -> Optional[Mol]:
        """
        Keep only the largest molecular fragment.

        Useful for removing counter ions and disconnected
        fragments before indexing.
        """

        if molecule is None:
            return None

        try:

            fragments = Chem.GetMolFrags(
                molecule,
                asMols=True,
                sanitizeFrags=False,
            )

            if not fragments:
                return None

            return max(
                fragments,
                key=lambda mol: mol.GetNumAtoms(),
            )

        except Exception:
            return None


    @staticmethod
    def remove_salts(
        molecule: Mol,
    ) -> Optional[Mol]:
        """
        Remove common salts and counter ions.
        """

        if molecule is None:
            return None

        try:

            remover = SaltRemover.SaltRemover()

            cleaned = remover.StripMol(
                RDKitUtils.copy(molecule),
                dontRemoveEverything=True,
            )

            return cleaned

        except Exception:
            return None


    @staticmethod
    def kekulize(
        molecule: Mol,
    ) -> Optional[Mol]:
        """
        Return a kekulized copy of the molecule.
        """

        if molecule is None:
            return None

        try:

            mol = RDKitUtils.copy(molecule)

            Chem.Kekulize(
                mol,
                clearAromaticFlags=False,
            )

            return mol

        except Exception:
            return None


    # ------------------------------------------------------------
    # Inspection Utilities
    # ------------------------------------------------------------

    @staticmethod
    def atom_symbols(
        molecule: Mol,
    ) -> list:
        """
        Return the atomic symbols present in the molecule.

        Example:
            CCO -> ["C", "C", "O"]
        """

        if molecule is None:
            return []

        return [
            atom.GetSymbol()
            for atom in molecule.GetAtoms()
        ]


    @staticmethod
    def bond_types(
        molecule: Mol,
    ) -> list:
        """
        Return the bond types present in the molecule.
        """

        if molecule is None:
            return []

        return [
            str(bond.GetBondType())
            for bond in molecule.GetBonds()
        ]


    @staticmethod
    def molblock(
        molecule: Mol,
    ) -> Optional[str]:
        """
        Convert a molecule into MolBlock format.
        """

        if molecule is None:
            return None

        try:
            return Chem.MolToMolBlock(molecule)

        except Exception:
            return None


    # ------------------------------------------------------------
    # Failed Result
    # ------------------------------------------------------------

    @staticmethod
    def failed(
        message: str,
    ) -> RDKitResult:
        """
        Return a failed RDKit result.
        """

        return RDKitResult(
            success=False,
            error=message,
        )


# ------------------------------------------------------------------
# Public Exports
# ------------------------------------------------------------------

__all__ = [
    "RDKitResult",
    "RDKitUtils",
]