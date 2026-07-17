"""
Unit tests for chemistry.rdkit_utils.

Run with:

python -m tests.test_rdkit_utils
"""

from chemistry.rdkit_utils import RDKitUtils


# ------------------------------------------------------------
# Test Molecules
# ------------------------------------------------------------

ethanol = RDKitUtils.from_smiles("CCO")

benzene = RDKitUtils.from_smiles("c1ccccc1")

salt = RDKitUtils.from_smiles("CCO.[Na]")

invalid = RDKitUtils.from_smiles("THIS_IS_NOT_A_SMILES")


# ------------------------------------------------------------
# From SMILES
# ------------------------------------------------------------

print("=" * 60)
print("From SMILES")
print("=" * 60)

print(ethanol.summary())
print(benzene.summary())
print(invalid.summary())


# ------------------------------------------------------------
# To SMILES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("To SMILES")
print("=" * 60)

print(
    RDKitUtils.to_smiles(
        ethanol.molecule,
    )
)

print(
    RDKitUtils.to_smiles(
        benzene.molecule,
    )
)


# ------------------------------------------------------------
# InChI
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("InChI")
print("=" * 60)

inchi = RDKitUtils.to_inchi(
    ethanol.molecule,
)

print(inchi)

result = RDKitUtils.from_inchi(inchi)

print(result.summary())


# ------------------------------------------------------------
# InChI Key
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("InChIKey")
print("=" * 60)

print(
    RDKitUtils.to_inchi_key(
        ethanol.molecule,
    )
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Validation")
print("=" * 60)

print(
    RDKitUtils.is_valid(
        ethanol.molecule,
    )
)

print(
    RDKitUtils.is_valid(
        None,
    )
)


# ------------------------------------------------------------
# Sanitize
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Sanitize")
print("=" * 60)

print(
    RDKitUtils.sanitize(
        ethanol.molecule,
    ).summary()
)


# ------------------------------------------------------------
# Molecular Properties
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Molecular Properties")
print("=" * 60)

print(
    "Formula:",
    RDKitUtils.molecular_formula(
        ethanol.molecule,
    ),
)

print(
    "Weight:",
    RDKitUtils.molecular_weight(
        ethanol.molecule,
    ),
)

print(
    "Atoms:",
    RDKitUtils.atom_count(
        ethanol.molecule,
    ),
)

print(
    "Bonds:",
    RDKitUtils.bond_count(
        ethanol.molecule,
    ),
)

print(
    "Heavy Atoms:",
    RDKitUtils.heavy_atom_count(
        ethanol.molecule,
    ),
)

print(
    "Rings:",
    RDKitUtils.ring_count(
        ethanol.molecule,
    ),
)


# ------------------------------------------------------------
# Hydrogen Operations
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Hydrogens")
print("=" * 60)

with_h = RDKitUtils.add_hydrogens(
    ethanol.molecule,
)

without_h = RDKitUtils.remove_hydrogens(
    with_h,
)

print(
    "With H:",
    RDKitUtils.atom_count(with_h),
)

print(
    "Without H:",
    RDKitUtils.atom_count(without_h),
)


# ------------------------------------------------------------
# Largest Fragment
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Largest Fragment")
print("=" * 60)

largest = RDKitUtils.largest_fragment(
    salt.molecule,
)

print(
    RDKitUtils.to_smiles(
        largest,
    )
)


# ------------------------------------------------------------
# Salt Removal
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Remove Salts")
print("=" * 60)

clean = RDKitUtils.remove_salts(
    salt.molecule,
)

print(
    RDKitUtils.to_smiles(
        clean,
    )
)


# ------------------------------------------------------------
# Kekulization
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Kekulize")
print("=" * 60)

kek = RDKitUtils.kekulize(
    benzene.molecule,
)

print(
    RDKitUtils.to_smiles(
        kek,
        canonical=False,
    )
)


# ------------------------------------------------------------
# Atom Symbols
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Atom Symbols")
print("=" * 60)

print(
    RDKitUtils.atom_symbols(
        ethanol.molecule,
    )
)


# ------------------------------------------------------------
# Bond Types
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Bond Types")
print("=" * 60)

print(
    RDKitUtils.bond_types(
        ethanol.molecule,
    )
)


# ------------------------------------------------------------
# MolBlock
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("MolBlock")
print("=" * 60)

molblock = RDKitUtils.molblock(
    ethanol.molecule,
)

print(
    molblock[:250],
)

print("...")


# ------------------------------------------------------------
# Copy
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Copy")
print("=" * 60)

copy = RDKitUtils.copy(
    ethanol.molecule,
)

print(copy is ethanol.molecule)

print(
    RDKitUtils.to_smiles(copy),
)


# ------------------------------------------------------------
# Failed Result
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Failed Result")
print("=" * 60)

print(
    RDKitUtils.failed(
        "Example failure",
    ).summary()
)


print("\n")
print("=" * 60)
print("RDKit Utils Tests Completed Successfully")
print("=" * 60)