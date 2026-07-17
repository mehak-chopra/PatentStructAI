"""
PatentStructAI Chemistry Utilities.

Reusable RDKit helper functions used throughout the project.

Responsibilities
----------------

- Validate SMILES
- Convert SMILES ↔ Mol
- Canonicalize molecules
- Generate Morgan fingerprints
- Compute similarity
- Perform substructure matching
- Compute descriptors

This module intentionally contains NO database logic.
"""

from __future__ import annotations

from typing import Optional

from dataclasses import dataclass

from rdkit.DataStructs.cDataStructs import (
    ExplicitBitVect,
)

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
from rdkit import DataStructs


# ============================================================
# Query Molecule
# ============================================================

@dataclass(frozen=True)
class QueryMolecule:
    """
    Represents a processed query molecule ready for searching.

    Every search algorithm receives this object instead of
    repeatedly rebuilding RDKit objects.
    """

    smiles: str

    canonical_smiles: str

    mol: Chem.Mol

    morgan_fingerprint: ExplicitBitVect

    pattern_fingerprint: ExplicitBitVect

    molecular_formula: str | None

    molecular_weight: float

    heavy_atom_count: int

    atom_count: int

    bond_count: int


# ============================================================
# Molecule Validation
# ============================================================

def is_valid_smiles(
    smiles: str,
) -> bool:
    """
    Returns True if RDKit can parse the SMILES.
    """

    if not smiles:

        return False

    return Chem.MolFromSmiles(smiles) is not None


# ============================================================
# SMILES → Mol
# ============================================================

def smiles_to_mol(
    smiles: str,
) -> Optional[Chem.Mol]:
    """
    Convert SMILES into an RDKit Mol.
    """

    if not smiles:

        return None

    try:

        return Chem.MolFromSmiles(smiles)

    except Exception:

        return None


# ============================================================
# Mol → Canonical SMILES
# ============================================================

def mol_to_smiles(
    mol: Chem.Mol,
    canonical: bool = True,
) -> Optional[str]:
    """
    Convert an RDKit Mol into a SMILES string.
    """

    if mol is None:

        return None

    try:

        return Chem.MolToSmiles(
            mol,
            canonical=canonical,
        )

    except Exception:

        return None


# ============================================================
# Canonicalization
# ============================================================

def canonicalize_smiles(
    smiles: str,
) -> Optional[str]:
    """
    Convert arbitrary SMILES into canonical RDKit SMILES.
    """

    mol = smiles_to_mol(
        smiles
    )

    if mol is None:

        return None

    return mol_to_smiles(
        mol,
        canonical=True,
    )


# ============================================================
# Basic Molecule Information
# ============================================================

def atom_count(
    mol: Chem.Mol,
) -> int:
    """
    Number of atoms.
    """

    if mol is None:

        return 0

    return mol.GetNumAtoms()


def bond_count(
    mol: Chem.Mol,
) -> int:
    """
    Number of bonds.
    """

    if mol is None:

        return 0

    return mol.GetNumBonds()


def molecular_weight(
    mol: Chem.Mol,
) -> float:
    """
    Exact molecular weight.
    """

    if mol is None:

        return 0.0

    return Descriptors.ExactMolWt(
        mol
    )


# ============================================================
# Molecule Serialization
# ============================================================

def mol_to_molblock(
    mol: Chem.Mol,
) -> Optional[str]:
    """
    Convert Mol to MOL block.
    """

    if mol is None:

        return None

    return Chem.MolToMolBlock(
        mol
    )


def molblock_to_mol(
    molblock: str,
) -> Optional[Chem.Mol]:
    """
    Convert MOL block into RDKit Mol.
    """

    if not molblock:

        return None

    try:

        return Chem.MolFromMolBlock(
            molblock
        )

    except Exception:

        return None


# ============================================================
# Morgan Fingerprints
# ============================================================

def generate_morgan_fingerprint(
    mol: Chem.Mol,
    radius: int = 2,
    n_bits: int = 2048,
) -> ExplicitBitVect | None:
    """
    Generate a Morgan fingerprint.

    Parameters
    ----------
    mol
        RDKit molecule.

    radius
        Morgan fingerprint radius.

    n_bits
        Fingerprint size.

    Returns
    -------
    ExplicitBitVect | None
    """

    if mol is None:

        return None

    return AllChem.GetMorganFingerprintAsBitVect(

        mol,

        radius,

        nBits=n_bits,

    )


# ============================================================
# Fingerprint Serialization
# ============================================================

def fingerprint_to_binary(
    fingerprint,
) -> bytes | None:
    """
    Serialize an RDKit fingerprint to bytes.

    Useful for database storage.
    """

    if fingerprint is None:

        return None

    return DataStructs.BitVectToBinaryText(
        fingerprint
    )


def binary_to_fingerprint(
    binary: bytes,
):
    """
    Restore an RDKit fingerprint from bytes.
    """

    if binary is None:

        return None

    fp = DataStructs.ExplicitBitVect(2048)

    DataStructs.CreateFromBinaryText(

        binary,

        fp,

    )

    return fp


# ============================================================
# Similarity
# ============================================================

def tanimoto_similarity(
    fingerprint_a,
    fingerprint_b,
) -> float:
    """
    Compute Tanimoto similarity.

    Returns
    -------
    float
        Between 0 and 1.
    """

    if (

        fingerprint_a is None

        or

        fingerprint_b is None

    ):

        return 0.0

    return float(

        DataStructs.TanimotoSimilarity(

            fingerprint_a,

            fingerprint_b,

        )

    )


# ============================================================
# Substructure Matching
# ============================================================

def contains_substructure(
    query_mol: Chem.Mol,
    target_mol: Chem.Mol,
) -> bool:
    """
    Check whether query is contained inside target.
    """

    if (

        query_mol is None

        or

        target_mol is None

    ):

        return False

    return target_mol.HasSubstructMatch(
        query_mol
    )


def substructure_matches(
    query_mol: Chem.Mol,
    target_mol: Chem.Mol,
):
    """
    Return atom index matches.

    Returns
    -------
    tuple
    """

    if (

        query_mol is None

        or

        target_mol is None

    ):

        return ()

    return target_mol.GetSubstructMatches(
        query_mol
    )


# ============================================================
# Molecular Properties
# ============================================================

def molecular_formula(
    mol: Chem.Mol,
) -> str | None:
    """
    Molecular formula.
    """

    if mol is None:

        return None

    return Chem.rdMolDescriptors.CalcMolFormula(
        mol
    )


def heavy_atom_count(
    mol: Chem.Mol,
) -> int:
    """
    Heavy atom count.
    """

    if mol is None:

        return 0

    return mol.GetNumHeavyAtoms()


def inchi(
    mol: Chem.Mol,
) -> str | None:
    """
    Generate InChI.
    """

    if mol is None:

        return None

    return Chem.MolToInchi(
        mol
    )


def inchikey(
    mol: Chem.Mol,
) -> str | None:
    """
    Generate InChIKey.
    """

    if mol is None:

        return None

    return Chem.MolToInchiKey(
        mol
    )


# ============================================================
# Complete Query Preparation
# ============================================================

def prepare_query(
    smiles: str,
) -> QueryMolecule | None:
    """
    Prepare a molecule for searching.

    Returns
    -------
    QueryMolecule
        Fully prepared molecule ready for exact,
        similarity and substructure search.
    """

    mol = smiles_to_mol(
        smiles
    )

    if mol is None:

        return None
    
    pattern_fp = Chem.PatternFingerprint(
        mol
    )

    canonical = mol_to_smiles(
        mol
    )

    morgan_fingerprint = generate_morgan_fingerprint(
        mol
    )

    return QueryMolecule(

        smiles=smiles,

        canonical_smiles=canonical,

        mol=mol,

        morgan_fingerprint=morgan_fingerprint,

        pattern_fingerprint=pattern_fp,

        molecular_formula=molecular_formula(
            mol
        ),

        molecular_weight=molecular_weight(
            mol
        ),

        heavy_atom_count=heavy_atom_count(
            mol
        ),

        atom_count=atom_count(
            mol
        ),

        bond_count=bond_count(
            mol
        ),

    )