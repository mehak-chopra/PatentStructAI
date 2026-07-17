"""
PatentStructAI Exact Structure Search.

Finds exact molecular matches using canonical SMILES.

Workflow
--------

QueryMolecule
    │
    ▼
Canonical SMILES
    │
    ▼
Database Lookup
    │
    ▼
SearchResult[]
"""

from __future__ import annotations

from sqlalchemy import text

from database.patent_repository import (
    PatentRepository,
)

from chemistry.chemistry_utils import (
    QueryMolecule,
)

from search.search_result import (
    SearchResult,
    SearchType,
)


# ============================================================
# Exact Search
# ============================================================

class ExactSearch:
    """
    Exact structure search using canonical SMILES.

    Every returned molecule is chemically identical
    to the query.
    """

    def __init__(
        self,
        repository: PatentRepository | None = None,
    ):

        self.repository = (

            repository

            if repository is not None

            else PatentRepository()

        )


    # ============================================================
    # Database Query
    # ============================================================

    def _query_database(
        self,
        query: QueryMolecule,
    ) -> list[dict]:
        """
        Find exact canonical SMILES matches.

        Returns
        -------
        list[dict]

            Raw database rows.
        """

        sql = text(
            """
            SELECT

                p.id                     AS patent_id,

                p.patent_number,

                p.title,

                p.country,

                s.id                     AS structure_id,

                s.page_number,

                s.crop_index,

                s.image_path,

                s.smiles,

                s.canonical_smiles,

                s.recognizer_name,

                s.recognizer_version,

                s.recognizer_confidence,

                s.backend,

                s.inference_time

            FROM structures s

            INNER JOIN patents p

                ON p.id = s.patent_id

            WHERE

                s.searchable = TRUE

                AND

                s.canonical_smiles = :canonical_smiles

            ORDER BY

                p.patent_number,

                s.page_number,

                s.crop_index
            """
        )

        with self.repository.session() as db:

            rows = db.execute(

                sql,

                {

                    "canonical_smiles":
                        query.canonical_smiles,

                }

            )

            return [

                dict(row._mapping)

                for row in rows

            ]


    # ============================================================
    # Result Conversion
    # ============================================================

    def _build_results(
        self,
        rows: list[dict],
    ) -> list[SearchResult]:
        """
        Convert raw database rows into SearchResult objects.
        """

        results: list[SearchResult] = []

        for row in rows:

            results.append(

                SearchResult(

                    patent_id=row["patent_id"],

                    patent_number=row["patent_number"],

                    patent_title=row["title"],

                    country=row["country"],

                    structure_id=row["structure_id"],

                    page_number=row["page_number"],

                    crop_index=row["crop_index"],

                    image_path=row["image_path"],

                    smiles=row["smiles"],

                    canonical_smiles=row["canonical_smiles"],

                    search_type=SearchType.EXACT,

                    matched_by={SearchType.EXACT,},

                    similarity_score=1.0,

                    recognizer_name=row["recognizer_name"],

                    recognizer_version=row["recognizer_version"],

                    recognizer_confidence=row["recognizer_confidence"],

                    backend=row["backend"],

                    inference_time=row["inference_time"],

                )

            )

        return results


    # ============================================================
    # Exact Search
    # ============================================================

    def search(
        self,
        query: QueryMolecule,
    ) -> list[SearchResult]:
        """
        Perform an exact structure search.

        Parameters
        ----------
        query
            Prepared query molecule.

        Returns
        -------
        list[SearchResult]
            Exact molecular matches.
        """

        rows = self._query_database(
            query
        )

        if not rows:

            return []

        return self._build_results(
            rows
        )