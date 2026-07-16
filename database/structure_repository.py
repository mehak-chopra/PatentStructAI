"""
Structure repository for PatentStructAI.

Responsible for all operations involving the structures table.

This repository stores searchable molecular structures
produced by the chemistry pipeline.
"""

from __future__ import annotations

from sqlalchemy import text

from database.base_repository import BaseRepository
from database.models import StructureRecordDB


# =====================================================
# Structure Repository
# =====================================================

class StructureRepository(BaseRepository):
    """
    Repository responsible for all operations on the
    structures table.
    """

    TABLE_NAME = "structures"

    # ------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------

    @classmethod
    def save(
        cls,
        structure: StructureRecordDB,
    ) -> None:
        """
        Insert one molecular structure into the database.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    INSERT INTO structures
                    (
                        patent_id,
                        page_number,
                        crop_index,
                        image_path,
                        smiles,
                        canonical_smiles,
                        molblock,
                        fingerprint_hash,
                        recognizer_name,
                        recognizer_version,
                        recognizer_confidence,
                        backend,
                        inference_time,
                        pipeline_time,
                        recognition_success,
                        failure_reason,
                        searchable
                    )
                    VALUES
                    (
                        :patent_id,
                        :page_number,
                        :crop_index,
                        :image_path,
                        :smiles,
                        :canonical_smiles,
                        :molblock,
                        :fingerprint_hash,
                        :recognizer_name,
                        :recognizer_version,
                        :recognizer_confidence,
                        :backend,
                        :inference_time,
                        :pipeline_time,
                        :recognition_success,
                        :failure_reason,
                        :searchable
                    )
                    """
                ),

                {
                    "patent_id": structure.patent_id,
                    "page_number": structure.page_number,
                    "crop_index": structure.crop_index,
                    "image_path": structure.image_path,
                    "smiles": structure.smiles,
                    "canonical_smiles": structure.canonical_smiles,
                    "molblock": structure.molblock,
                    "fingerprint_hash": structure.fingerprint_hash,
                    "recognizer_name": structure.recognizer_name,
                    "recognizer_version": structure.recognizer_version,
                    "recognizer_confidence": structure.recognizer_confidence,
                    "backend": structure.backend,
                    "inference_time": structure.inference_time,
                    "pipeline_time": structure.pipeline_time,
                    "recognition_success": structure.recognition_success,
                    "failure_reason": structure.failure_reason,
                    "searchable": structure.searchable,
                },

            )


    @classmethod
    def save_many(
        cls,
        structures: list[StructureRecordDB],
    ) -> None:
        """
        Insert multiple structures.
        """

        for structure in structures:

            cls.save(structure)

    # ------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------

    @classmethod
    def get(
        cls,
        structure_id: int,
    ):
        """
        Return a structure by its database ID.
        """

        return cls.fetch_one(
            "id",
            structure_id,
        )


    @classmethod
    def get_by_patent(
        cls,
        patent_id: int,
    ):
        """
        Return every structure belonging to a patent.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM structures
                    WHERE patent_id = :patent_id
                    ORDER BY page_number, id
                    """
                ),

                {
                    "patent_id": patent_id,
                },

            )

            return result.mappings().all()


    @classmethod
    def get_by_page(
        cls,
        patent_id: int,
        page_number: int,
    ):
        """
        Return every structure detected on one page.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM structures
                    WHERE
                        patent_id = :patent_id
                        AND page_number = :page_number
                    ORDER BY id
                    """
                ),

                {
                    "patent_id": patent_id,
                    "page_number": page_number,
                },

            )

            return result.mappings().all()


    @classmethod
    def get_by_image(
        cls,
        image_path: str,
    ):
        """
        Return the structure generated from a crop image.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM structures
                    WHERE image_path = :image_path
                    LIMIT 1
                    """
                ),

                {
                    "image_path": image_path,
                },

            )

            return result.mappings().first()
        
    # ------------------------------------------------------------
    # Chemistry Lookup
    # ------------------------------------------------------------

    @classmethod
    def canonical_smiles_exists(
        cls,
        canonical_smiles: str,
    ) -> bool:
        """
        Return True if the canonical SMILES already exists.
        Useful for duplicate detection.
        """

        return super().exists(
            "canonical_smiles",
            canonical_smiles,
        )


    @classmethod
    def get_by_canonical_smiles(
        cls,
        canonical_smiles: str,
    ):
        """
        Return every structure having the same canonical SMILES.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM structures
                    WHERE canonical_smiles = :canonical_smiles
                    """
                ),

                {
                    "canonical_smiles": canonical_smiles,
                },

            )

            return result.mappings().all()
    

    @classmethod
    def get_by_fingerprint(
        cls,
        fingerprint_hash: str,
    ):
        """
        Return every structure having the same fingerprint hash.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM structures
                    WHERE fingerprint_hash = :fingerprint_hash
                    """
                ),

                {
                    "fingerprint_hash": fingerprint_hash,
                },

            )

            return result.mappings().all()


    @classmethod
    def get_by_crop(
        cls,
        patent_id: int,
        page_number: int,
        crop_index: int,
    ):
        """
        Return one detected crop from a page.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM structures
                    WHERE
                        patent_id = :patent_id
                        AND page_number = :page_number
                        AND crop_index = :crop_index
                    LIMIT 1
                    """
                ),

                {
                    "patent_id": patent_id,
                    "page_number": page_number,
                    "crop_index": crop_index,
                },

            )

            return result.mappings().first()


    @classmethod
    def fingerprint_hash_exists(
        cls,
        fingerprint_hash: str,
    ) -> bool:
        """
        Return True if the fingerprint hash already exists.
        """

        return super().exists(
            "fingerprint_hash",
            fingerprint_hash,
        )


    @classmethod
    def searchable(
        cls,
    ):
        """
        Return every searchable molecular structure.

        Used by:
        - Similarity Search
        - Substructure Search
        - Future FAISS indexing
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM structures
                    WHERE searchable = TRUE
                    ORDER BY id
                    """
                )

            )

            return result.mappings().all()


    @classmethod
    def all(
        cls,
    ):
        """
        Return every stored molecular structure.
        """

        return cls.fetch_all()

    # ------------------------------------------------------------
    # Updates
    # ------------------------------------------------------------

    @classmethod
    def update_smiles(
        cls,
        structure_id: int,
        smiles: str,
        canonical_smiles: str,
    ) -> None:
        """
        Update SMILES information for an existing structure.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    UPDATE structures
                    SET
                        smiles = :smiles,
                        canonical_smiles = :canonical_smiles
                    WHERE id = :structure_id
                    """
                ),

                {
                    "structure_id": structure_id,
                    "smiles": smiles,
                    "canonical_smiles": canonical_smiles,
                },

            )


    @classmethod
    def update_fingerprint(
        cls,
        structure_id: int,
        fingerprint_hash: str,
    ) -> None:
        """
        Update fingerprint metadata.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    UPDATE structures
                    SET fingerprint_hash = :fingerprint_hash
                    WHERE id = :structure_id
                    """
                ),

                {
                    "structure_id": structure_id,
                    "fingerprint_hash": fingerprint_hash,
                },

            )

    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    @classmethod
    def searchable_count(
        cls,
    ) -> int:
        """
        Number of searchable structures.
        """

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM structures
                    WHERE searchable = TRUE
                    """
                )

            ).scalar_one()


    @classmethod
    def duplicate_count(
        cls,
    ) -> int:
        """
        Number of duplicate canonical structures.
        """

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM
                    (
                        SELECT canonical_smiles
                        FROM structures
                        GROUP BY canonical_smiles
                        HAVING COUNT(*) > 1
                    ) duplicates
                    """
                )

            ).scalar_one()


    @classmethod
    def statistics(
        cls,
    ):
        """
        Return repository statistics.
        """

        return {

            "total": cls.count(),

            "searchable": cls.searchable_count(),

            "duplicates": cls.duplicate_count(),

        }