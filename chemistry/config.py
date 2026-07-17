"""
Central configuration for the PatentStructAI chemistry engine.

All chemistry-related modules should read default values from this
file instead of hardcoding constants.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ------------------------------------------------------------------
# Fingerprint Configuration
# ------------------------------------------------------------------

@dataclass(frozen=True)
class FingerprintConfig:
    """
    Configuration for molecular fingerprint generation.
    """

    radius: int = 2

    n_bits: int = 2048

    fingerprint_type: str = "Morgan"


# ------------------------------------------------------------------
# Similarity Configuration
# ------------------------------------------------------------------

@dataclass(frozen=True)
class SimilarityConfig:
    """
    Configuration for similarity calculations.
    """

    metric: str = "Tanimoto"

    threshold: float = 0.70

    top_k: int = 10


# ------------------------------------------------------------------
# Substructure Search Configuration
# ------------------------------------------------------------------

@dataclass(frozen=True)
class SubstructureConfig:
    """
    Configuration for substructure searching.
    """

    uniquify: bool = True

    use_chirality: bool = False

    max_matches: int = 1000


# ------------------------------------------------------------------
# RDKit Configuration
# ------------------------------------------------------------------

@dataclass(frozen=True)
class RDKitConfig:
    """
    Configuration controlling RDKit behavior.
    """

    sanitize: bool = True

    remove_hydrogens: bool = False

    add_hydrogens: bool = False

    remove_salts: bool = True

    keep_largest_fragment: bool = True

    kekulize: bool = False


# ------------------------------------------------------------------
# Recognition Configuration
# ------------------------------------------------------------------

@dataclass(frozen=True)
class RecognitionConfig:
    """
    Configuration for molecular structure recognition.
    """

    recognizer_name: str = "MolNexTR"

    confidence_threshold: float = 0.50

    return_multiple_predictions: bool = False

    max_predictions: int = 5

    clean_prediction: bool = True


# ------------------------------------------------------------------
# Serialization Configuration
# ------------------------------------------------------------------

@dataclass(frozen=True)
class SerializationConfig:
    """
    Configuration for saving and loading chemistry data.
    """

    indent: int = 4

    ensure_ascii: bool = False

    sort_keys: bool = True

    compress: bool = False

    save_metadata: bool = True


# ------------------------------------------------------------------
# Chemistry Configuration
# ------------------------------------------------------------------

@dataclass(frozen=True)
class ChemistryConfig:
    """
    Central configuration object for the chemistry package.

    Rather than scattering constants across multiple modules,
    every chemistry component should read its defaults from here.
    """

    fingerprints: FingerprintConfig = field(
        default_factory=FingerprintConfig
    )

    similarity: SimilarityConfig = field(
        default_factory=SimilarityConfig
    )

    substructure: SubstructureConfig = field(
        default_factory=SubstructureConfig
    )

    rdkit: RDKitConfig = field(
        default_factory=RDKitConfig
    )

    recognition: RecognitionConfig = field(
        default_factory=RecognitionConfig
    )

    serialization: SerializationConfig = field(
        default_factory=SerializationConfig
    )


# ------------------------------------------------------------------
# Default Configuration
# ------------------------------------------------------------------

DEFAULT_CONFIG = ChemistryConfig()


# ------------------------------------------------------------------
# Public Exports
# ------------------------------------------------------------------

__all__ = [
    "FingerprintConfig",
    "SimilarityConfig",
    "SubstructureConfig",
    "RDKitConfig",
    "RecognitionConfig",
    "SerializationConfig",
    "ChemistryConfig",
    "DEFAULT_CONFIG",
]