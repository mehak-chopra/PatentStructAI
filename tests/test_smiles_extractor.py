"""
Unit tests for chemistry.smiles_extractor.

Run with:

python -m tests.test_smiles_extractor
"""

from pathlib import Path

from chemistry.smiles_extractor import (
    SMILESExtractor,
)

from chemistry.recognizers.molnextr_recognizer import (
    MolNexTRRecognizer,
)


# ------------------------------------------------------------
# Create Extractor
# ------------------------------------------------------------

recognizer = MolNexTRRecognizer()

extractor = SMILESExtractor(
    recognizer,
)

image = Path("outputs/AU2023318885A1/structures/page_2/structure_001.png")


# ------------------------------------------------------------
# Single Extraction
# ------------------------------------------------------------

print("=" * 60)
print("Single Extraction")
print("=" * 60)

result = extractor.extract_from_path(
    image,
    patent_id="AU2023318885A1",
    page_number=3,
    structure_id="STR001",
)

print(result)

print("\nRecognition")

print("Recognizer:",
    result.recognition.recognizer)

print("SMILES:",
    result.recognition.smiles)

print("Inference Time:",
    round(result.recognition.inference_time, 4))

print("\nCanonicalization")


print(result.recognition.summary())

print(result.canonicalization.summary())

print(result.fingerprint.summary())

print("\nStructure Record")

print("Patent:", result.structure.patent_id)

print("Page:", result.structure.page_number)

print("Image:", result.structure.image_path)

print("Canonical SMILES:",
    result.structure.canonicalization.canonical_smiles)

print("Fingerprint:",
    result.structure.fingerprint.fingerprint_type)

print("Active Bits:",
    result.structure.fingerprint.active_bits)


# ------------------------------------------------------------
# Batch Extraction
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Batch Extraction")
print("=" * 60)

batch = extractor.extract_batch(
    [
        "outputs/AU2023318885A1/structures/page_2/structure_001.png",
        "outputs/AU2023318885A1/structures/page_4/structure_001.png",
        "outputs/AU2023318885A1/structures/page_4/structure_002.png",
    ],
    patent_id="AU2023318885A1",
)

for item in batch:

    print(item.summary())


# ------------------------------------------------------------
# Batch Summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Batch Summary")
print("=" * 60)

print(
    extractor.summarize_batch(
        batch,
    )
)


# ------------------------------------------------------------
# Statistics
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Statistics")
print("=" * 60)

print(
    extractor.statistics()
)

print(extractor)


# ------------------------------------------------------------
# Reset Statistics
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Reset Statistics")
print("=" * 60)

extractor.reset_statistics()

print(
    extractor.statistics()
)


# ------------------------------------------------------------
# Failed Result
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Failed Result")
print("=" * 60)

print(
    SMILESExtractor.create_failed(
        "Example failure",
        image,
    ).summary()
)


print("\n")
print("=" * 60)
print("SMILES Extractor Tests Completed Successfully")
print("=" * 60)