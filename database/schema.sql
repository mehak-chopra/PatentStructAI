-- ============================================================
-- PatentStructAI Database Schema
-- ============================================================

DROP DATABASE IF EXISTS patent_struct_ai;

CREATE DATABASE patent_struct_ai
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE patent_struct_ai;

-- ============================================================
-- PATENTS
-- ============================================================

CREATE TABLE patents (

    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    patent_number VARCHAR(100) NOT NULL,

    title TEXT,

    pdf_url TEXT,

    country VARCHAR(20),

    pdf_downloaded BOOLEAN NOT NULL DEFAULT FALSE,

    pdf_available BOOLEAN NOT NULL DEFAULT TRUE,

    images_extracted BOOLEAN NOT NULL DEFAULT FALSE,

    structures_extracted BOOLEAN NOT NULL DEFAULT FALSE,

    processed BOOLEAN NOT NULL DEFAULT FALSE,

    local_pdf_path TEXT,

    file_size BIGINT,

    download_at DATETIME NULL,

    download_duration FLOAT NULL,

    processing_started_at DATETIME NULL,

    processed_at DATETIME NULL,

    download_error TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uq_patent_number (
        patent_number
    ),

    INDEX idx_processed (
        processed
    ),

    INDEX idx_country (
        country
    ),

    INDEX idx_pdf_downloaded (
        pdf_downloaded
    )

);

-- ============================================================
-- PATENT PAGES
-- ============================================================

CREATE TABLE patent_pages (

    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    patent_id BIGINT UNSIGNED NOT NULL,

    page_number INT NOT NULL,

    image_path TEXT NOT NULL,

    contains_chemistry BOOLEAN NULL,

    chemistry_score FLOAT NULL,

    classifier_name VARCHAR(100),

    classifier_version VARCHAR(50),

    classification_time FLOAT,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_pages_patent
        FOREIGN KEY (patent_id)
        REFERENCES patents(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_patent_page
        UNIQUE (
            patent_id,
            page_number
        ),

    INDEX idx_patent (
        patent_id
    ),

    INDEX idx_contains_chemistry (
        contains_chemistry
    )

);

-- ============================================================
-- FAILED PATENTS
-- ============================================================

CREATE TABLE failed_patents (

    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    patent_number VARCHAR(100) NOT NULL,

    failure_stage VARCHAR(100),

    error_message TEXT,

    retry_count INT NOT NULL DEFAULT 0,

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_failed_patent (
        patent_number
    )

);

-- ============================================================
-- REVIEWED PAGES
-- ============================================================

CREATE TABLE reviewed_pages (

    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    filename VARCHAR(255) NOT NULL,

    patent_number VARCHAR(100),

    dataset_version VARCHAR(30),

    status ENUM(

        'confirmed',

        'rejected'

    ) NOT NULL,

    category VARCHAR(100),

    notes TEXT,

    reviewed_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_filename (

        filename

    ),

    INDEX idx_dataset (

        dataset_version

    ),

    INDEX idx_status (

        status

    ),

    INDEX idx_patent (

        patent_number

    )

);

-- ============================================================
-- STRUCTURES
-- ============================================================

CREATE TABLE structures (

    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    patent_id BIGINT UNSIGNED NOT NULL,

    page_number INT,

    crop_index INT,

    image_path TEXT,

    smiles LONGTEXT,

    canonical_smiles LONGTEXT,

    molblock LONGTEXT,

    fingerprint_hash VARCHAR(255),

    recognizer_name VARCHAR(100),

    recognizer_version VARCHAR(50),

    recognizer_confidence FLOAT,

    backend VARCHAR(100),

    inference_time FLOAT,

    pipeline_time FLOAT NULL,

    recognition_success BOOLEAN DEFAULT TRUE,

    failure_reason TEXT,

    searchable BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_structure_patent
        FOREIGN KEY (patent_id)
        REFERENCES patents(id)
        ON DELETE CASCADE,

    INDEX idx_patent (patent_id),

    INDEX idx_page (page_number),

    INDEX idx_fingerprint (fingerprint_hash(100)),

    INDEX idx_searchable (searchable),

    INDEX idx_canonical_smiles (canonical_smiles(255))

);

SELECT COUNT(*) FROM patents;

SELECT COUNT(*) FROM patent_pages;

SELECT COUNT(*) FROM structures;

SELECT COUNT(*) FROM failed_patents;

SELECT *
FROM structures
LIMIT 1;

SELECT
    p.patent_number,
    s.*
FROM structures s
JOIN patents p
ON s.patent_id = p.id;