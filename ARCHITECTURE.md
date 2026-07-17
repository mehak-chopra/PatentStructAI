Module
-------
ingestion/metadata_fetcher.py

Purpose
-------
Fetch metadata from Google Patents.

Input
-----
Patent Number

Output
------
Patent Metadata
- patent_number
- title
- pdf_url
- country

Database Reads
--------------
None

Database Writes
---------------
None

Repository
----------
PatentRepository.save_metadata()

Status
------
✔ Good
No refactoring required.


Module
-------
ingestion/pdf_downloader.py

Purpose
-------
Download patent PDF to local storage.

Input
-----
patent_number
pdf_url

Output
------
Local PDF path

Database Reads
--------------
None

Database Writes
---------------
None

Repository
----------
PatentRepository.update_download_status()

Future Database Fields
----------------------
pdf_downloaded
local_pdf_path
download_time
file_size
download_error

Status
------
✔ Good

Refactor:
- Remove unused patent_id parameter.
- Replace print() with logging later.



Module
-------
ingestion/bulk_metadata_ingestion.py

Purpose
-------
Bulk import patent metadata into MySQL.

Input
-----
Patent number list (.txt)

Output
------
patents table
failed_patents table

Database Reads
--------------
None

Database Writes
---------------
patents

failed_patents

Repository
----------
PatentRepository

Status
------
✔ Good

Future Improvements
-------------------
Move PATENT_FILE to config.py

Return ingestion statistics

Store failure stage

Store retry count

Keep SQL inside PatentRepository


Module
-------
ingestion/patent_processor.py

Purpose
-------
Download PDFs and create page records.

Input
-----
Patent object

Output
------
Page images

patent_pages

Database Reads
--------------
patents

Database Writes
---------------
patents
patent_pages

Repository
----------
PatentRepository

PageRepository

Status
------
✔ Good

Future
------
Will evolve into pipeline/process_patent.py

Temporary orchestrator only.


Module
-------
extraction/image_extractor.py

Purpose
-------
Render PDF pages and optionally extract embedded images.

Input
-----
PDF

Output
------
Rendered page images

Embedded images (optional)

Database Reads
--------------
None

Database Writes
---------------
None

Repository
----------
PageRepository

Status
------
✔ Good

Future Improvements
-------------------
Return PageRecord objects.

Move OUTPUT_DIR into config.py.

Keep embedded extraction separate from production pipeline.


Module
-------
extraction/page_classifier.py

Purpose
-------
Classify patent pages into chemistry/non-chemistry.

Input
-----
Rendered page image

Output
------
Classification result
- contains chemistry
- confidence

Database Reads
--------------
None

Database Writes
---------------
None

Repository
----------
PageRepository.update_classification()

Status
------
✔ Excellent

Future Improvements
-------------------
Create PageClassificationResult dataclass.

Store model version.

Store inference time.

Represent uncertain pages as NULL.


Module
-------
extraction/structure_cropper.py

Purpose
-------
Locate chemical structures on chemistry pages and crop them.

Input
-----
Chemistry page images

Output
------
Individual cropped structure images.

Database Reads
--------------
Patent pages where

contains_chemistry = TRUE

Database Writes
---------------
Insert one Structure row per detected crop.

Repository
----------
StructureRepository

Stores
------
page_id

image_path

bbox

detector confidence

detector version

crop size

Status
------
Excellent

Future Improvements
-------------------
Read pages from database.

Save detections directly to MySQL.

Replace metadata.json with repository calls.

Support multiple detection classes.


Module
-------
chemistry/recognizers/base.py

Purpose
-------
Defines the common interface for all molecular recognition engines.

Input
-----
Molecular structure image

Output
------
RecognitionResult

Database Reads
--------------
None

Database Writes
---------------
None

Repository
----------
None

Status
------
Complete

No database integration required.


Module
-------
chemistry/recognizers/molnextr_recognizer.py

Purpose
-------
Recognize chemical structures from cropped images using MolNexTR.

Input
-----
Cropped structure image

Output
------
RecognitionResult

Database Reads
--------------
None

Database Writes
---------------
None

Pipeline Output
---------------
RecognitionResult

Important Persistent Fields
---------------------------
image_path

smiles

molblock

recognizer

recognizer_version

atoms (JSON)

bonds (JSON)

Status
------
Complete

No database integration required.


Module
-------
chemistry/recognition_result.py

Purpose
-------
Immutable data object representing molecular recognition output.

Input
-----
MolNexTR prediction

Output
------
RecognitionResult

Database Reads
--------------
None

Database Writes
---------------
None

Persistent Fields
-----------------
image_path

patent_id

page_number

recognizer

recognizer_version

smiles

canonical_smiles

molblock

atoms (JSON)

bonds (JSON)

recognition_confidence

success

error

Runtime Only
------------
device

inference_time

metadata

artifacts

Status
------
Complete

Defines much of the future structures table schema.


Module
-------
chemistry/similarity.py

Purpose
-------
Compute similarity between molecular fingerprints.

Input
-----
FingerprintResult

StructureRecord

Output
------
SimilarityResult

Database Reads
--------------
None

Database Writes
---------------
None

Repository
----------
None

Persistent Data
---------------
None

Status
------
Complete

Used by future SearchService after candidate structures are loaded from MySQL.


Module
-------
chemistry/structure_database.py

Purpose
-------
Defines the searchable chemistry object used throughout PatentStructAI.

Contains
--------
StructureRecord
StructureDatabase (temporary in-memory implementation)

Persistent Data
---------------
StructureRecord

Database Reads
--------------
Future:
StructureRepository -> reconstruct StructureRecord from MySQL.

Database Writes
---------------
Future:
SMILESExtractor -> StructureRepository.insert(record)

Repository Needed
-----------------
YES

Future Repository
-----------------
database/structure_repository.py

Status
------
StructureRecord: Complete

StructureDatabase:
Temporary implementation.
Will be replaced by MySQL repository.


Module
-------
chemistry/similarity_search.py

Purpose
-------
Performs ranked molecular similarity searches using fingerprints.

Produces
--------
SimilaritySearchResult

Consumes
--------
StructureRecord

Persistent Data
---------------
None

Database Reads
--------------
Future:
StructureRepository.get_searchable()

Database Writes
---------------
None

Repository Needed
-----------------
YES (StructureRepository)

Current Backend
---------------
StructureDatabase (temporary)

Future Backend
--------------
MySQL
↓
StructureRepository

Future Optimization
-------------------
FAISS Approximate Nearest Neighbor Search

Status
------
Algorithm complete.

Backend pending migration from in-memory database to MySQL.


Module
-------
chemistry/substructure_search.py

Purpose
-------
Performs exact RDKit molecular substructure search over indexed structures.

Produces
--------
SubstructureSearchResult
SubstructureMatch

Consumes
--------
StructureRecord

Persistent Data
---------------
None

Database Reads
--------------
Future:
StructureRepository.iter_searchable()

Database Writes
---------------
None

Repository Needed
-----------------
YES (StructureRepository)

Current Backend
---------------
StructureDatabase (temporary)

Future Backend
--------------
MySQL
↓
StructureRepository

Search Method
-------------
RDKit GetSubstructMatch()

Status
------
Algorithm complete.

Backend pending migration from in-memory storage to MySQL.


Module
-------
chemistry/canonicalizer.py

Purpose
-------
Converts recognizer SMILES into canonical RDKit representations.

Produces
--------
CanonicalizationResult

Consumes
--------
RecognitionResult

Persistent Data
---------------
original_smiles
canonical_smiles
num_atoms
num_bonds

Transient Data
--------------
RDKit molecule object

Database Writes
---------------
No

Repository
----------
None

Future Usage
------------
Pipeline reconstructs RDKit molecules from canonical_smiles when loading records from MySQL.

Status
------
Complete.

Only canonicalize_result() and canonicalize_batch() remain to be implemented.


Module
-------
chemistry/fingerprints.py

Purpose
-------
Generates molecular fingerprints from canonical SMILES or RDKit molecules for similarity search, duplicate detection, indexing, and retrieval.

Produces
--------
FingerprintResult

Consumes
--------
CanonicalizationResult
Canonical SMILES
RDKit Molecule

Persistent Data
---------------
fingerprint_hash
fingerprint_type
radius
n_bits
active_bits

Transient Data
--------------
RDKit fingerprint object
NumPy fingerprint bit vector

Database Writes
---------------
No

Repository
----------
None

Future Usage
------------
Pipeline generates fingerprints after canonicalization. StructureRepository stores fingerprint metadata while rebuilding fingerprints from canonical_smiles when records are loaded from MySQL. Fingerprints are later used by similarity search, FAISS indexing, duplicate detection, and patent retrieval.

Status
------
Complete.

Current implementation supports Morgan fingerprints, Tanimoto, Dice, and Cosine similarity. Additional fingerprint algorithms can be added later without changing the pipeline.


Module
-------
chemistry/smiles_extractor.py

Purpose
-------
Coordinates the complete chemistry pipeline by performing molecular recognition, canonicalization, fingerprint generation, and assembling a searchable StructureRecord.

Produces
--------
SMILESExtractionResult
StructureRecord

Consumes
--------
BaseRecognizer
RecognitionResult
CanonicalizationResult
FingerprintResult

Persistent Data
---------------
structure_id
patent_id
page_number
image_path
smiles
canonical_smiles
fingerprint_hash
fingerprint_type
radius
n_bits
active_bits
recognizer
recognizer_version
inference_time

Transient Data
--------------
RDKit molecule
RDKit fingerprint object
NumPy fingerprint vector
Intermediate pipeline objects

Database Writes
---------------
No

Repository
----------
None

Future Usage
------------
Acts as the chemistry engine for PatentStructAI. Produces complete StructureRecords which are passed to the StructureRepository for persistence. The production pipeline will invoke this module for every detected chemical structure before saving searchable records into MySQL.

Status
------
Complete.

Acts as the central orchestration layer of the chemistry pipeline. Database persistence will be handled by the pipeline, not by this module.


Module
-------
pipeline/process_patent.py

Purpose
-------
Coordinates the complete PatentStructAI processing workflow from patent PDF to searchable chemical structures. Orchestrates extraction, page classification, structure detection, chemistry extraction, database persistence, and pipeline reporting.

Produces
--------
Patent processing workspace
Pipeline metadata
Page predictions
Structure detections
StructureRecords (via SMILESExtractor)

Consumes
--------
Patent PDF
Image Extractor
Page Classifier
Structure Cropper
SMILES Extractor
Repositories

Persistent Data
---------------
Patent metadata
Patent page records
Page classification results
Chemistry confidence scores
Structure detections
Bounding boxes
Crop image paths
SMILES
Canonical SMILES
Fingerprint metadata
Structure metadata
Pipeline processing status

Transient Data
--------------
Rendered page images
Intermediate prediction objects
Temporary runtime statistics

Database Writes
---------------
Yes

Updates:
- patents
- patent_pages
- structures

Repository
----------
PatentRepository
PatentPageRepository
StructureRepository

Future Usage
------------
Acts as the production orchestration layer for PatentStructAI. Coordinates all pipeline stages and becomes the single entry point for patent processing. Future versions will support batch processing, asynchronous execution, FAISS indexing, Markush extraction, and FastAPI endpoints.

Status
------
Partially Complete.

Current implementation performs page extraction, page classification, structure detection, and workspace generation. Remaining work includes chemistry integration (SMILES extraction), repository integration, database persistence, processed-state updates, and search index generation.


Module
-------
pipeline/batch_processor.py

Purpose
-------
Processes multiple patent PDFs by repeatedly executing the PatentPipeline. Handles batch execution, progress reporting, failure recovery, and batch-level reporting.

Produces
--------
Batch processing report
Per-patent processing workspaces
Processing statistics

Consumes
--------
PatentPipeline
Directory containing patent PDFs

Persistent Data
---------------
Batch processing report
Successful patent list
Skipped patent list
Failed patent list
Execution statistics

Transient Data
--------------
Progress bar
Runtime statistics
Temporary PatentPipeline instances

Database Writes
---------------
No

Repository
----------
None

Future Usage
------------
Will become the production ingestion entry point for large patent collections. Future versions will coordinate database-backed processing queues, multiprocessing, distributed execution, resume support, duplicate detection, and automatic indexing after successful patent ingestion.

Status
------
Partially Complete.

Current implementation executes patents sequentially and generates batch reports. Future work includes repository integration, database status tracking, parallel processing, retry mechanisms, and queue-based execution.


