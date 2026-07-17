"""
Unit tests for chemistry.structure_database.

Run with:

python -m tests.test_structure_database
"""

from pathlib import Path

from chemistry.recognition_result import RecognitionResult
from chemistry.canonicalizer import Canonicalizer
from chemistry.fingerprints import FingerprintGenerator
from chemistry.structure_database import (
    StructureDatabase,
    StructureRecord,
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
    """
    Create a complete StructureRecord.
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

    fingerprint = FingerprintGenerator.from_smiles(
        canonical.canonical_smiles
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
# Test Records
# ------------------------------------------------------------

record1 = create_record(
    "STR001",
    "WO202400001",
    1,
    "CCO",
)

record2 = create_record(
    "STR002",
    "WO202400001",
    2,
    "CCN",
)

record3 = create_record(
    "STR003",
    "WO202499999",
    1,
    "c1ccccc1",
)


db = StructureDatabase()


# ------------------------------------------------------------
# Add
# ------------------------------------------------------------

print("=" * 60)
print("Add")
print("=" * 60)

db.add(record1)

print(db)
print(db.statistics())


# ------------------------------------------------------------
# Add Many
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Add Many")
print("=" * 60)

db.add_many([
    record2,
    record3,
])

print(db)
print(db.statistics())


# ------------------------------------------------------------
# Get
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Get")
print("=" * 60)

print(
    db.get("STR001")
)

print(
    db.get("DOES_NOT_EXIST")
)


# ------------------------------------------------------------
# Exists
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Exists")
print("=" * 60)

print(
    db.exists("STR002")
)

print(
    db.exists("XYZ")
)


# ------------------------------------------------------------
# __contains__
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("__contains__")
print("=" * 60)

print("STR003" in db)

print("ABC" in db)


# ------------------------------------------------------------
# __len__
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("__len__")
print("=" * 60)

print(len(db))


# ------------------------------------------------------------
# All
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("All")
print("=" * 60)

for record in db.all():
    print(record.structure_id)


# ------------------------------------------------------------
# Searchable
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Searchable")
print("=" * 60)

for record in db.searchable():
    print(record.structure_id)


# ------------------------------------------------------------
# Patent Filter
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Patent Filter")
print("=" * 60)

for record in db.by_patent(
    "WO202400001"
):
    print(record.structure_id)


# ------------------------------------------------------------
# Page Filter
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Page Filter")
print("=" * 60)

for record in db.by_page(1):
    print(record.structure_id)


# ------------------------------------------------------------
# Filename Filter
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Filename Filter")
print("=" * 60)

print(
    db.by_filename("STR002.png")
)

print(
    db.by_filename("nothing.png")
)


# ------------------------------------------------------------
# Fingerprints
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Fingerprints")
print("=" * 60)

print(
    len(db.fingerprints())
)


# ------------------------------------------------------------
# Canonical SMILES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Canonical SMILES")
print("=" * 60)

print(
    db.canonical_smiles()
)


# ------------------------------------------------------------
# Patent IDs
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Patent IDs")
print("=" * 60)

print(
    db.patent_ids()
)


# ------------------------------------------------------------
# Structure IDs
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Structure IDs")
print("=" * 60)

print(
    db.structure_ids()
)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

print(
    db.summary()
)


# ------------------------------------------------------------
# Remove
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Remove")
print("=" * 60)

removed = db.remove("STR002")

print(removed)

print(db.statistics())


# ------------------------------------------------------------
# Clear
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Clear")
print("=" * 60)

db.clear()

print(db)

print(db.statistics())


print("\n")
print("=" * 60)
print("StructureDatabase Tests Completed Successfully")
print("=" * 60)