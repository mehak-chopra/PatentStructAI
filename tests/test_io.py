"""
Unit tests for chemistry.io.

Run with:

python -m tests.test_io
"""

from pathlib import Path

from chemistry.io import IOUtils


TEST_DIR = Path("tests/temp_io")


# ------------------------------------------------------------
# Directory
# ------------------------------------------------------------

print("=" * 60)
print("Ensure Directory")
print("=" * 60)

directory = IOUtils.ensure_directory(TEST_DIR)

print(directory)
print(directory.exists())


# ------------------------------------------------------------
# Resolve
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Resolve")
print("=" * 60)

resolved = IOUtils.resolve(TEST_DIR)

print(resolved)
print(resolved.exists())


# ------------------------------------------------------------
# Exists
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Exists")
print("=" * 60)

print(IOUtils.exists(TEST_DIR))
print(IOUtils.exists("does_not_exist"))


# ------------------------------------------------------------
# JSON
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("JSON")
print("=" * 60)

json_file = TEST_DIR / "sample.json"

data = {
    "name": "PatentStructAI",
    "version": 1,
    "features": [
        "fingerprints",
        "similarity",
        "substructure",
    ],
}

result = IOUtils.save_json(
    json_file,
    data,
)

print(result.summary())

loaded = IOUtils.load_json(
    json_file,
)

print(loaded.summary())
print(loaded.data)


# ------------------------------------------------------------
# Pickle
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Pickle")
print("=" * 60)

pickle_file = TEST_DIR / "sample.pkl"

sample_object = {
    "numbers": [1, 2, 3],
    "text": "hello",
}

saved = IOUtils.save_pickle(
    pickle_file,
    sample_object,
)

print(saved.summary())

loaded = IOUtils.load_pickle(
    pickle_file,
)

print(loaded.summary())
print(loaded.data)


# ------------------------------------------------------------
# Text
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Text")
print("=" * 60)

text_file = TEST_DIR / "sample.txt"

saved = IOUtils.save_text(
    text_file,
    "Hello PatentStructAI!",
)

print(saved.summary())

loaded = IOUtils.load_text(
    text_file,
)

print(loaded.summary())
print(loaded.data)


# ------------------------------------------------------------
# Missing Files
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Missing Files")
print("=" * 60)

print(
    IOUtils.load_json(
        TEST_DIR / "missing.json",
    ).summary()
)

print(
    IOUtils.load_pickle(
        TEST_DIR / "missing.pkl",
    ).summary()
)

print(
    IOUtils.load_text(
        TEST_DIR / "missing.txt",
    ).summary()
)


# ------------------------------------------------------------
# Delete File
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Delete File")
print("=" * 60)

print(IOUtils.delete(text_file))
print(IOUtils.exists(text_file))


# ------------------------------------------------------------
# Delete Directory
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Delete Directory")
print("=" * 60)

print(IOUtils.delete(TEST_DIR))
print(IOUtils.exists(TEST_DIR))


# ------------------------------------------------------------
# Failed Result
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("Failed Result")
print("=" * 60)

print(
    IOUtils.failed(
        "Example failure",
    ).summary()
)


print("\n")
print("=" * 60)
print("IO Tests Completed Successfully")
print("=" * 60)