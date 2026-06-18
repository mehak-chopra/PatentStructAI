# PatentStructAI

An AI-powered chemical patent search engine that identifies whether a chemical structure exists within patent documents and retrieves matching patents with similarity scores.

## Overview

PatentStructAI is a scalable cheminformatics and patent-mining platform designed to automate chemical structure search across large patent collections.

Given an input chemical structure image, the system will:

1. Search through thousands of patent documents.
2. Detect chemical structures inside patent pages.
3. Convert detected structures into machine-readable molecular representations.
4. Compare structures using cheminformatics techniques.
5. Return matching patents along with similarity scores and patent metadata.

---

## Problem Statement

Chemical patent analysis is traditionally performed manually by patent analysts and researchers.

Searching for a specific compound across thousands of patents is:

* Time consuming
* Error prone
* Difficult to scale

PatentStructAI aims to automate this workflow using computer vision, machine learning, and cheminformatics.

---

## Features

### Patent Ingestion

* Bulk patent metadata ingestion
* Google Patents integration
* Patent PDF retrieval
* MySQL-backed storage

### Patent Processing

* PDF page rendering
* Patent page indexing
* Large-scale document processing pipeline

### Dataset Analytics

* Patent statistics generation
* Country-wise patent distribution
* Failed patent tracking
* PDF availability monitoring

### Annotation Pipeline

* Random page sampling
* Annotation dataset creation
* Chemical region detection dataset preparation

### YOLO Dataset Preparation

* CVAT-based annotation workflow
* YOLO format label generation
* Automated image-label synchronization
* Chemical structure bounding box annotations
* Initial dataset containing 106 manually annotated chemical structures

### Chemical Structure Extraction (Planned)

* Chemical structure localization (In Progress)
* Structure cropping pipeline (Planned)
* Structure image extraction (Planned)

### Molecular Recognition (Planned)

* Optical Chemical Structure Recognition (OCSR)
* SMILES generation
* Molecular graph reconstruction

### Similarity Search (Planned)

* RDKit fingerprints
* Molecular similarity scoring
* FAISS vector search

### API (Planned)

* Structure image upload
* Patent search endpoint
* Similarity ranking API

---

## Current Pipeline

Patent Numbers
↓
Metadata Extraction
↓
Patent Database
↓
Failed Patent Tracking
↓
PDF Download
↓
PDF Availability Validation
↓
Page Rendering
↓
Patent Page Storage
↓
Dataset Analytics
↓
Random Sampling
↓
Annotation Pipeline
↓
YOLO Dataset Preparation
↓
Chemical Structure Detection Model Training (Current Stage)
↓
Structure Cropping
↓
SMILES Generation (Upcoming)
↓
Similarity Search (Upcoming)

---

## Project Structure

PATENTSTRUCTAI/

├── api/

├── chemistry/

├── database/

├── extraction/

├── ingestion/

├── search/

├── data/

└── requirements.txt

---
## Current Dataset

### Patent Corpus

* 37 successfully processed patents
* 1654 rendered patent pages
* Multi-country patent collection
  * US
  * WO
  * JP
  * CN
  * KR
  * EP
  * TW
  * AU

### Dataset Composition

| Category | Pages |
|-----------|-------|
| Markush Structures | 12 |
| Reaction Schemes | 10 |
| Multiple Compound Pages | 6 |
| Single Compound Pages | 2 |
| Mixed Structure Pages | Remaining |

### Annotation Dataset

* YOLO-format object detection dataset
* 42 annotated chemistry pages
* Chemical structure bounding box annotations
* Includes:
  * Markush structures
  * Single compounds
  * Multiple compounds / compound grids
  * Reaction schemes

---

## Current Progress

### Completed

✅ Patent ingestion pipeline

✅ Patent metadata validation

✅ PDF download automation

✅ Patent page rendering

✅ Patent database storage

✅ Dataset analytics

✅ Chemistry page sampling pipeline

✅ CVAT annotation workflow

✅ YOLO dataset generation

### In Progress

🔄 Custom YOLOv8 chemical structure detector

### Upcoming

⏳ Structure cropping pipeline

⏳ MolScribe integration

⏳ Molecular fingerprint generation

⏳ Similarity search engine

---

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* MySQL

### Machine Learning

* PyTorch
* TorchVision
* Ultralytics YOLOv8
* OpenCV

### Cheminformatics

* RDKit

### Document Processing

* PyMuPDF
* BeautifulSoup
* Requests

### Similarity Search

* FAISS

---

## Scalability Goals

* Process thousands of patents
* Detect structures from full patent pages
* Perform large-scale molecular similarity search
* Support real-time structure lookup

---

## Future Roadmap

* Complete training and evaluation of custom YOLOv8 chemical structure detector
* MolScribe integration
* Molecular fingerprint indexing
* Patent similarity ranking
* FastAPI web application
* Interactive search dashboard

---

## Author

Mehak Chopra

B.Tech Computer Science Engineering

Patent Mining + Computer Vision + Cheminformatics
