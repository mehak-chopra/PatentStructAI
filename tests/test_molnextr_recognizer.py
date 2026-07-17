"python -m tests.test_molnextr_recognizer (in molnextr env)"

from chemistry.recognizers.molnextr_recognizer import MolNexTRRecognizer

IMAGE = (
    r"M:\projects\PatentStructAI\outputs\AU2023318885A1"
    r"\structures\page_2\structure_001.png"
)

print("=" * 60)
print("Testing MolNexTRRecognizer")
print("=" * 60)

recognizer = MolNexTRRecognizer()

print("Recognizer:", recognizer.name)
print("Version:", recognizer.version)
print("Loaded:", recognizer.is_loaded)

result = recognizer.predict(IMAGE)

print()

print(result)

print()

print(result.summary())

print()
print("=" * 60)
print("Batch Prediction")
print("=" * 60)

results = recognizer.predict_batch([IMAGE, IMAGE])

print("Results:", len(results))

for r in results:
    print(r.summary())

print()
print("=" * 60)
print("Invalid Image")
print("=" * 60)

bad = recognizer.predict("does_not_exist.png")

print(bad)
print(bad.success)
print(bad.error)

print()
print("=" * 60)
print("Capabilities")
print("=" * 60)

print("Batch:", recognizer.supports_batch)
print("GPU:", recognizer.supports_gpu)
print("CPU:", recognizer.supports_cpu)
print("Atoms:", recognizer.supports_atoms)
print("Bonds:", recognizer.supports_bonds)
print("MolBlock:", recognizer.supports_molblock)
print("SMILES:", recognizer.supports_smiles)
print("Confidence:", recognizer.supports_confidence)