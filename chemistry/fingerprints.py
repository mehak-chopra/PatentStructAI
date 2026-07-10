"""
Fingerprint generation utilities for PatentStructAI.

Fingerprints are compact numerical representations of molecules used
for similarity search, indexing, clustering and database retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

import numpy as np

from rdkit.Chem.rdchem import Mol

from rdkit import DataStructs
from rdkit.Chem.rdFingerprintGenerator import GetMorganGenerator
from rdkit.Chem import MolFromSmiles

import hashlib


# ------------------------------------------------------------------
# Fingerprint Result
# ------------------------------------------------------------------

@dataclass(frozen=True)
class FingerprintResult:
    """
    Immutable container describing a generated molecular fingerprint.
    """

    # ------------------------------------------------------------
    # Molecular Information
    # ------------------------------------------------------------

    canonical_smiles: Optional[str] = None

    rdkit_molecule: Optional[Mol] = None

    # ------------------------------------------------------------
    # Fingerprint Data
    # ------------------------------------------------------------

    fingerprint: Any = None

    bit_vector: Optional[np.ndarray] = None

    fingerprint_type: str = "Morgan"

    radius: int = 2

    n_bits: int = 2048

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
    def has_fingerprint(self) -> bool:
        return self.fingerprint is not None


    @property
    def has_bit_vector(self) -> bool:
        return self.bit_vector is not None


    @property
    def has_molecule(self) -> bool:
        return self.rdkit_molecule is not None


    @property
    def searchable(self) -> bool:
        return (
            self.success
            and self.has_bit_vector
        )


    @property
    def dimension(self) -> int:
        if self.bit_vector is None:
            return 0

        return self.bit_vector.size


    @property
    def active_bits(self) -> int:
        """
        Number of active (1) bits in the fingerprint.
        """
        if self.bit_vector is None:
            return 0

        return int(self.bit_vector.sum())


    @property
    def density(self) -> float:
        """
        Fraction of active bits.

        Useful for debugging, statistics and indexing.
        """

        if self.bit_vector is None:
            return 0.0

        if self.dimension == 0:
            return 0.0

        return self.active_bits / self.dimension


    @property
    def sparsity(self) -> float:
        """
        Fraction of inactive bits.
        """

        return 1.0 - self.density


    @property
    def fingerprint_size(self) -> int:
        """
        Alias for fingerprint dimensionality.
        """

        return self.dimension


    @property
    def fingerprint_hash(self) -> str:
        """
        Stable hash of the fingerprint bit vector.

        Useful for caching and duplicate detection.
        """

        if self.bit_vector is None:
            return ""

        return hashlib.sha256(
            self.bit_vector.tobytes()
        ).hexdigest()


    @property
    def memory_usage(self) -> int:
        """
        Memory occupied by the NumPy fingerprint in bytes.
        """

        if self.bit_vector is None:
            return 0

        return self.bit_vector.nbytes


    @property
    def has_error(self) -> bool:

        return self.error is not None


    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a lightweight summary of the fingerprint.
        """

        return {
            "success": self.success,
            "canonical_smiles": self.canonical_smiles,
            "fingerprint_type": self.fingerprint_type,
            "radius": self.radius,
            "n_bits": self.n_bits,
            "dimension": self.dimension,
            "active_bits": self.active_bits,
            "density": round(self.density, 4),
            "searchable": self.searchable,
            "error": self.error,
        }


    def __str__(self) -> str:
        return (
            f"FingerprintResult("
            f"type='{self.fingerprint_type}', "
            f"bits={self.n_bits}, "
            f"active_bits={self.active_bits}, "
            f"success={self.success})"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "FingerprintResult":
        """
        Return a new FingerprintResult with updated metadata.
        """

        merged = {**self.metadata, **metadata}

        return replace(
            self,
            metadata=merged,
        )


    def with_error(
        self,
        message: str,
    ) -> "FingerprintResult":
        """
        Return a failed fingerprint result.
        """

        return replace(
            self,
            success=False,
            error=message,
        )




# ------------------------------------------------------------------
# Fingerprint Generator
# ------------------------------------------------------------------

class FingerprintGenerator:
    """
    Utility class for generating molecular fingerprints.

    This class currently supports Morgan fingerprints but is designed
    so additional fingerprint algorithms can be added without changing
    the rest of PatentStructAI.
    """

    
    DEFAULT_RADIUS = 2

    DEFAULT_BITS = 2048

    DEFAULT_TYPE = "Morgan"

    _generator = GetMorganGenerator(
        radius=DEFAULT_RADIUS,
        fpSize=DEFAULT_BITS,
    )

    @staticmethod
    def from_smiles(
        canonical_smiles: str,
        radius: int = DEFAULT_RADIUS,
        n_bits: int = DEFAULT_BITS,
    ) -> FingerprintResult:
        """
        Generate a molecular fingerprint from a canonical SMILES string.
        """

        if not canonical_smiles:

            return FingerprintResult(
                canonical_smiles=canonical_smiles,
                success=False,
                error="No canonical SMILES provided.",
            )

        molecule = MolFromSmiles(canonical_smiles)

        if molecule is None:

            return FingerprintResult(
                canonical_smiles=canonical_smiles,
                success=False,
                error="Invalid SMILES.",
            )

        return FingerprintGenerator.from_rdkit(
            molecule=molecule,
            canonical_smiles=canonical_smiles,
            radius=radius,
            n_bits=n_bits,
        )


    @staticmethod
    def from_rdkit(
        molecule: Mol,
        canonical_smiles: Optional[str] = None,
        radius: int = DEFAULT_RADIUS,
        n_bits: int = DEFAULT_BITS,
    ) -> FingerprintResult:
        """
        Generate a Morgan fingerprint directly from an RDKit molecule.
        """

        if molecule is None:

            return FingerprintResult(
                canonical_smiles=canonical_smiles,
                success=False,
                error="RDKit molecule is None.",
            )

        try:

            # --------------------------------------------------------
            # Generate Morgan Fingerprint
            # --------------------------------------------------------

            generator = GetMorganGenerator(
                radius=radius,
                fpSize=n_bits,
            )

            fingerprint = generator.GetFingerprint(molecule)

            # --------------------------------------------------------
            # Convert to NumPy array
            # --------------------------------------------------------

            bit_vector = np.zeros((n_bits,), dtype=np.uint8)

            DataStructs.ConvertToNumpyArray(
                fingerprint,
                bit_vector,
            )

            return FingerprintResult(
                canonical_smiles=canonical_smiles,
                rdkit_molecule=molecule,
                fingerprint=fingerprint,
                bit_vector=bit_vector,
                fingerprint_type=FingerprintGenerator.DEFAULT_TYPE,
                radius=radius,
                n_bits=n_bits,
                success=True,
            )

        except Exception as exc:

            return FingerprintResult(
                canonical_smiles=canonical_smiles,
                rdkit_molecule=molecule,
                success=False,
                error=str(exc),
            )


    # ------------------------------------------------------------
    # Conversion Utilities
    # ------------------------------------------------------------

    @staticmethod
    def to_numpy(result: FingerprintResult) -> Optional[np.ndarray]:
        """
        Return the fingerprint as a NumPy array.
        """

        return result.bit_vector


    @staticmethod
    def to_bitstring(result: FingerprintResult) -> Optional[str]:
        """
        Convert a fingerprint into a string of 0s and 1s.

        Useful for serialization and debugging.
        """

        if result.bit_vector is None:
            return None

        return "".join(result.bit_vector.astype(str))


    @staticmethod
    def serialize(result: FingerprintResult) -> Dict[str, Any]:
        """
        Convert a FingerprintResult into a JSON-serializable dictionary.
        """

        return {
            "canonical_smiles": result.canonical_smiles,
            "fingerprint_type": result.fingerprint_type,
            "radius": result.radius,
            "n_bits": result.n_bits,
            "bit_vector": FingerprintGenerator.to_bitstring(result),
            "metadata": result.metadata,
            "success": result.success,
            "error": result.error,
        }


    @staticmethod
    def deserialize(data: Dict[str, Any]) -> FingerprintResult:
        """
        Reconstruct a FingerprintResult from serialized data.
        """

        bit_vector = data.get("bit_vector")

        if bit_vector is not None:

            bit_vector = np.fromiter(
                map(int, bit_vector),
                dtype=np.uint8,
            )

        return FingerprintResult(
            canonical_smiles=data.get("canonical_smiles"),
            bit_vector=bit_vector,
            fingerprint_type=data.get(
                "fingerprint_type",
                FingerprintGenerator.DEFAULT_TYPE,
            ),
            radius=data.get("radius", 2),
            n_bits=data.get("n_bits", 2048),
            metadata=data.get("metadata", {}),
            success=data.get("success", True),
            error=data.get("error"),
        )


    @staticmethod
    def tanimoto(
        fp1: FingerprintResult,
        fp2: FingerprintResult,
    ) -> float:
        """
        Compute the Tanimoto similarity between two fingerprints.

        Returns
        -------
        float
            Similarity in the range [0, 1].
        """

        if (
            not fp1.searchable
            or not fp2.searchable
        ):
            return 0.0

        return float(
            DataStructs.TanimotoSimilarity(
                fp1.fingerprint,
                fp2.fingerprint,
            )
        )


    @staticmethod
    def dice(
        fp1: FingerprintResult,
        fp2: FingerprintResult,
    ) -> float:
        """
        Compute the Dice similarity between two fingerprints.
        """

        if (
            not fp1.searchable
            or not fp2.searchable
        ):
            return 0.0

        return float(
            DataStructs.DiceSimilarity(
                fp1.fingerprint,
                fp2.fingerprint,
            )
        )


    @staticmethod
    def cosine(
        fp1: FingerprintResult,
        fp2: FingerprintResult,
    ) -> float:
        """
        Compute cosine similarity between two fingerprints.
        """

        if (
            fp1.bit_vector is None
            or fp2.bit_vector is None
        ):
            return 0.0

        a = fp1.bit_vector.astype(np.float32)

        b = fp2.bit_vector.astype(np.float32)

        denominator = (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(np.dot(a, b) / denominator)


    @staticmethod
    def failed(
        message: str,
    ) -> FingerprintResult:
        """
        Create a failed fingerprint result.
        """

        return FingerprintResult(
            success=False,
            error=message,
        )