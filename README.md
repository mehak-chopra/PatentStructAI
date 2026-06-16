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

### Chemical Structure Extraction (Planned)

* Chemical structure localization
* Structure segmentation
* Structure image extraction

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
Annotation Pipeline (Current Stage)
↓
Structure Detection (Upcoming)
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

## Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* MySQL

### Machine Learning

* PyTorch
* TorchVision

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

* YOLO-based chemical structure detection
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
