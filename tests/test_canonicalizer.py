"python -m tests.test_canonicalizer (in molnextr env)"

from chemistry.canonicalizer import Canonicalizer

print("=" * 60)
print("Testing Canonicalizer")
print("=" * 60)

# -------------------------------------------------
# Valid SMILES
# -------------------------------------------------

result = Canonicalizer.canonicalize("OCC")

print("\nOriginal:")
print(result.original_smiles)

print("\nCanonical:")
print(result.canonical_smiles)

print("\nSuccess:")
print(result.success)

print("\nRDKit Molecule:")
print(result.rdkit_molecule)

print("\nSummary:")
print(result.summary())

# -------------------------------------------------
# Invalid SMILES
# -------------------------------------------------

print("\n" + "=" * 60)
print("Invalid SMILES")
print("=" * 60)

bad = Canonicalizer.canonicalize("THIS_IS_NOT_A_SMILES")

print(bad.summary())

# -------------------------------------------------
# Utility Functions
# -------------------------------------------------

print("\n" + "=" * 60)
print("Utility Functions")
print("=" * 60)

print(Canonicalizer.is_valid_smiles("CCO"))
print(Canonicalizer.is_valid_smiles("HELLO"))

print(Canonicalizer.canonicalize_or_none("OCC"))
print(Canonicalizer.canonicalize_or_none("INVALID"))

print(Canonicalizer.molecule_from_smiles("CCO"))