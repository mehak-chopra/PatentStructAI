"""
Tests for chemistry.similarity_search.

Run using:

python -m tests.test_similarity_search
"""

from pathlib import Path

from chemistry.recognition_result import RecognitionResult
from chemistry.canonicalizer import Canonicalizer
from chemistry.fingerprints import FingerprintGenerator
from chemistry.structure_database import (
    StructureDatabase,
    StructureRecord,
)
from chemistry.similarity_search import SimilaritySearcher


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

def create_record(
    structure_id: str,
    patent_id: str,
    page: int,
    smiles: str,
):
    """
    Create a searchable StructureRecord.
    """

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
            "CCN",
        ),
        create_record(
            "STR003",
            "WO202499999",
            1,
            "c1ccccc1",
        ),
    ]
)

searcher = SimilaritySearcher(database)


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
# Search Fingerprint
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Search Fingerprint")
print("=" * 60)

query = FingerprintGenerator.from_smiles("CCN")

result = searcher.search_fingerprint(query)

print(result.summary())

for match in result.matches:
    print(match.summary())


# ------------------------------------------------------------
# Search Record
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Search Record")
print("=" * 60)

record = database.get("STR003")

result = searcher.search_record(record)

print(result.summary())

for match in result.matches:
    print(match.summary())


# ------------------------------------------------------------
# Top K
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Top K")
print("=" * 60)

result = searcher.top_k(
    query,
    k=2,
)

print(result.summary())

for match in result.matches:
    print(match.summary())


# ------------------------------------------------------------
# Search Database
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Search Database")
print("=" * 60)

matches = searcher.search_database(query)

for match in matches:
    print(match.summary())


# ------------------------------------------------------------
# Rank
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Rank")
print("=" * 60)

ranked = searcher.rank(matches)

for match in ranked:
    print(match.similarity_score)


# ------------------------------------------------------------
# Filter
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Filter")
print("=" * 60)

filtered = searcher.filter(
    matches,
    threshold=0.30,
)

for match in filtered:
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

empty = SimilaritySearcher(
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
# Searcher Summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Searcher")
print("=" * 60)

print(searcher)

print(searcher.summary())


print("\n")
print("=" * 60)
print("Similarity Search Tests Completed Successfully")
print("=" * 60)