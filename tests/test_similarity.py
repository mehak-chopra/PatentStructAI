"""
Unit tests for chemistry.similarity.

Run with:

python -m tests.test_similarity
"""

from pathlib import Path

from chemistry.recognition_result import RecognitionResult
from chemistry.structure_database import StructureRecord

from chemistry.canonicalizer import Canonicalizer
from chemistry.fingerprints import FingerprintGenerator
from chemistry.similarity import SimilarityCalculator


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

def record(
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
        atoms=[1],
        bonds=[1],
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
# Test Molecules
# ------------------------------------------------------------

ethanol = record(
    "STR001",
    "WO1",
    1,
    "CCO",
)

ethylamine = record(
    "STR002",
    "WO1",
    2,
    "CCN",
)

benzene = record(
    "STR003",
    "WO2",
    1,
    "c1ccccc1",
)

# ------------------------------------------------------------
# Tanimoto
# ------------------------------------------------------------

print("=" * 60)
print("Tanimoto")
print("=" * 60)

r = SimilarityCalculator.tanimoto(
    ethanol.fingerprint,
    ethanol,
)

print(r.summary())

r = SimilarityCalculator.tanimoto(
    ethanol.fingerprint,
    ethylamine,
)

print(r.summary())

r = SimilarityCalculator.tanimoto(
    ethanol.fingerprint,
    benzene,
)

print(r.summary())


# ------------------------------------------------------------
# Dice
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Dice")
print("=" * 60)

print(
    SimilarityCalculator.dice(
        ethanol.fingerprint,
        ethanol,
    ).summary()
)

print(
    SimilarityCalculator.dice(
        ethanol.fingerprint,
        ethylamine,
    ).summary()
)


# ------------------------------------------------------------
# Cosine
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Cosine")
print("=" * 60)

print(
    SimilarityCalculator.cosine(
        ethanol.fingerprint,
        ethanol,
    ).summary()
)

print(
    SimilarityCalculator.cosine(
        ethanol.fingerprint,
        benzene,
    ).summary()
)


# ------------------------------------------------------------
# Generic Compare
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Generic Compare")
print("=" * 60)

result = SimilarityCalculator.compare(
    ethanol.fingerprint,
    ethylamine,
    metric="Tanimoto",
)

print(result.summary())


# ------------------------------------------------------------
# Batch Comparison
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Batch Comparison")
print("=" * 60)

results = SimilarityCalculator.compare_batch(
    ethanol.fingerprint,
    [
        ethanol,
        ethylamine,
        benzene,
    ],
)

for r in results:
    print(r.summary())


# ------------------------------------------------------------
# Best Match
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Best Match")
print("=" * 60)

best = SimilarityCalculator.best_match(
    ethanol.fingerprint,
    [
        ethylamine,
        benzene,
        ethanol,
    ],
)

print(best.summary())


# ------------------------------------------------------------
# Sort
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Sorted")
print("=" * 60)

sorted_results = SimilarityCalculator.sort_by_similarity(
    results
)

for r in sorted_results:
    print(
        r.metric,
        round(r.similarity_score, 4),
    )


# ------------------------------------------------------------
# Filter
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Filter Matches")
print("=" * 60)

filtered = SimilarityCalculator.filter_matches(
    results
)

for r in filtered:
    print(r.summary())


# ------------------------------------------------------------
# is_similar
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("is_similar")
print("=" * 60)

print(
    SimilarityCalculator.is_similar(
        ethanol.fingerprint,
        ethanol,
    )
)

print(
    SimilarityCalculator.is_similar(
        ethanol.fingerprint,
        benzene,
    )
)


# ------------------------------------------------------------
# Unsupported Metric
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Unsupported Metric")
print("=" * 60)

bad = SimilarityCalculator.compare(
    ethanol.fingerprint,
    benzene,
    metric="Euclidean",
)

print(bad.summary())


# ------------------------------------------------------------
# Invalid Fingerprint
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Invalid Fingerprint")
print("=" * 60)

invalid = FingerprintGenerator.failed(
    "Broken fingerprint"
)

bad = SimilarityCalculator.compare(
    invalid,
    ethanol,
)

print(bad.summary())


print("\n")
print("=" * 60)
print("Similarity Tests Completed Successfully")
print("=" * 60)