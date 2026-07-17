"""
Tests for chemistry.substructure_search.

Run using:

python -m tests.test_substructure_search
"""

from pathlib import Path

from chemistry.recognition_result import RecognitionResult
from chemistry.canonicalizer import Canonicalizer
from chemistry.fingerprints import FingerprintGenerator
from chemistry.structure_database import (
    StructureDatabase,
    StructureRecord,
)
from chemistry.substructure_search import (
    SubstructureSearcher,
)


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

def create_record(
    structure_id: str,
    patent_id: str,
    page: int,
    smiles: str,
):

    recognition = RecognitionResult(
        image_path=Path(f"{structure_id}.png"),
        patent_id=patent_id,
        page_number=page,
        recognizer="MolNexTR",
        smiles=smiles,
        canonical_smiles=smiles,
        atoms=[{"C": 1}],
        bonds=[{"bond": "single"}],
    )

    canonical = Canonicalizer.canonicalize(smiles)

    fingerprint = FingerprintGenerator.from_rdkit(
        canonical.rdkit_molecule,
        canonical.canonical_smiles,
    )

    return StructureRecord(
        structure_id=structure_id,
        patent_id=patent_id,
        page_number=page,
        image_path=Path(f"{structure_id}.png"),
        recognition=recognition,
        canonicalization=canonical,
        fingerprint=fingerprint,
    )


# ------------------------------------------------------------
# Database
# ------------------------------------------------------------

database = StructureDatabase()

database.add_many(
    [
        create_record(
            "STR001",
            "WO202400001",
            1,
            "CCO",
        ),
        create_record(
            "STR002",
            "WO202400001",
            2,
            "CCOC",
        ),
        create_record(
            "STR003",
            "WO202499999",
            1,
            "CCN",
        ),
        create_record(
            "STR004",
            "WO202499999",
            2,
            "c1ccccc1",
        ),
        create_record(
            "STR005",
            "WO202500123",
            3,
            "CCOC(=O)N",
        ),
    ]
)

searcher = SubstructureSearcher(database)


# ------------------------------------------------------------
# Search SMILES
# ------------------------------------------------------------

print("=" * 60)
print("Search SMILES")
print("=" * 60)

result = searcher.search_smiles("CCO")

print(result)
print(result.summary())

for match in result.matches:
    print(match.summary())


# ------------------------------------------------------------
# Search Record
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Search Record")
print("=" * 60)

record = database.get("STR001")

result = searcher.search_record(record)

print(result.summary())

for match in result.matches:
    print(match.summary())


# ------------------------------------------------------------
# Matching Records
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Matching Records")
print("=" * 60)

records = searcher.matching_records("CCO")

for record in records:
    print(record.structure_id)


# ------------------------------------------------------------
# First Match
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("First Match")
print("=" * 60)

print(searcher.first_match("CCO"))


# ------------------------------------------------------------
# Contains
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Contains")
print("=" * 60)

print(searcher.contains("CCO"))
print(searcher.contains("CCCCCCCCCCCC"))


# ------------------------------------------------------------
# Sort Matches
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Sort Matches")
print("=" * 60)

sorted_matches = searcher.sort_matches(result.matches)

for match in sorted_matches:
    print(match.summary())


# ------------------------------------------------------------
# Invalid SMILES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Invalid SMILES")
print("=" * 60)

bad = searcher.search_smiles(
    "THIS_IS_NOT_A_SMILES"
)

print(bad.summary())


# ------------------------------------------------------------
# Empty Database
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Empty Database")
print("=" * 60)

empty = SubstructureSearcher(
    StructureDatabase()
)

result = empty.search_smiles("CCO")

print(result.summary())


# ------------------------------------------------------------
# Statistics
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Statistics")
print("=" * 60)

print(searcher.statistics())


# ------------------------------------------------------------
# Searcher
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Searcher")
print("=" * 60)

print(searcher)

print(searcher.summary())


print("\n")
print("=" * 60)
print("Substructure Search Tests Completed Successfully")
print("=" * 60)