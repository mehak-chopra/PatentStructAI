"python -m tests.test_fingerprints (in molnextr env)"

from chemistry.canonicalizer import Canonicalizer
from chemistry.fingerprints import FingerprintGenerator

print("=" * 60)
print("Testing Fingerprints")
print("=" * 60)

"Molecules"

ethanol = Canonicalizer.canonicalize("CCO")
ethylamine = Canonicalizer.canonicalize("CCN")
benzene = Canonicalizer.canonicalize("c1ccccc1")

"Generate fingerprints"

fp_ethanol = FingerprintGenerator.from_smiles(
    ethanol.canonical_smiles
)

fp_ethanol2 = FingerprintGenerator.from_smiles(
    ethanol.canonical_smiles
)

fp_ethylamine = FingerprintGenerator.from_smiles(
    ethylamine.canonical_smiles
)

fp_benzene = FingerprintGenerator.from_smiles(
    benzene.canonical_smiles
)

"Print summaries"

print("\nEthanol")
print(fp_ethanol.summary())

print("\nEthylamine")
print(fp_ethylamine.summary())

print("\nBenzene")
print(fp_benzene.summary())

"Test similarities"

print("\n" + "=" * 60)
print("Similarity")
print("=" * 60)

print(
    "CCO vs CCO:",
    FingerprintGenerator.tanimoto(
        fp_ethanol,
        fp_ethanol2,
    ),
)

print(
    "CCO vs CCN:",
    FingerprintGenerator.tanimoto(
        fp_ethanol,
        fp_ethylamine,
    ),
)

print(
    "CCO vs Benzene:",
    FingerprintGenerator.tanimoto(
        fp_ethanol,
        fp_benzene,
    ),
)

"Dice"

print("\nDice")

print(
    FingerprintGenerator.dice(
        fp_ethanol,
        fp_ethanol2,
    )
)

print(
    FingerprintGenerator.dice(
        fp_ethanol,
        fp_ethylamine,
    )
)

"Cosine"

print("\nCosine")

print(
    FingerprintGenerator.cosine(
        fp_ethanol,
        fp_ethanol2,
    )
)

print(
    FingerprintGenerator.cosine(
        fp_ethanol,
        fp_benzene,
    )
)

"Serialization"

print("\n" + "=" * 60)
print("Serialization")
print("=" * 60)

serialized = FingerprintGenerator.serialize(fp_ethanol)

restored = FingerprintGenerator.deserialize(serialized)

print(restored.summary())

"Hash"

print("\nHash")

print(fp_ethanol.fingerprint_hash)

print(fp_ethanol2.fingerprint_hash)

print(fp_ethylamine.fingerprint_hash)

"Memory"

print("\nMemory Usage")

print(fp_ethanol.memory_usage)

"Invalid molecule"

print("\n" + "=" * 60)
print("Invalid Molecule")
print("=" * 60)

bad = FingerprintGenerator.from_smiles(None)

print(bad.summary())
