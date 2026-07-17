"(venv) (base) PS M:\projects\PatentStructAI> python test_recognition_result.py"

from pathlib import Path

from chemistry.recognition_result import RecognitionResult


def main():
    result = RecognitionResult(
        image_path=Path("example.png"),
        recognizer="MolNexTR",
        smiles="CCO",
        canonical_smiles="CCO",
        atoms=[{"atom": "C"}],
        bonds=[{"bond": "single"}],
        success=True,
    )

    print("=" * 60)
    print("RecognitionResult")
    print("=" * 60)

    print(result)

    print("\nSummary")
    print(result.summary())

    print("\nDictionary")
    print(result.to_dict())

    print("\nSearchable:", result.searchable)
    print("RDKit Ready:", result.rdkit_ready)
    print("Atoms:", result.num_atoms)
    print("Bonds:", result.num_bonds)

    failed = RecognitionResult.failed(
        image_path=Path("bad.png"),
        recognizer="MolNexTR",
        message="Invalid image",
    )

    print("\nFailed Result")
    print(failed)

    print("\nTesting from_dict()")

    dictionary = result.to_dict()

    loaded = RecognitionResult.from_dict(dictionary)

    print(loaded)

    print()

    print(loaded.summary())


if __name__ == "__main__":
    main()