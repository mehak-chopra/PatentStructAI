from __future__ import annotations

from rdkit import Chem
from sqlalchemy import text

from chemistry.chemistry_utils import (
    QueryMolecule,
    generate_morgan_fingerprint,
    tanimoto_similarity,
)

from database.patent_repository import (
    PatentRepository,
)

from search.search_result import (
    SearchResult,
    SearchType,
)


# ============================================================
# Similarity Search
# ============================================================

class SimilaritySearch:
    """
    Search chemically similar structures using
    Morgan fingerprints and Tanimoto similarity.
    """

    def __init__(
        self,
        repository: PatentRepository | None = None,
        threshold: float = 0.50,
        top_k: int = 10,
    ):

        self.repository = (

            repository

            if repository is not None

            else PatentRepository()

        )

        self.threshold = threshold

        self.top_k = top_k


    # ============================================================
    # Load Searchable Molecules
    # ============================================================

    def _load_candidates(
        self,
    ) -> list[dict]:
        """
        Load every searchable structure from the database.

        Returns
        -------
        list[dict]
            Searchable structures.
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

            ORDER BY

                p.patent_number,

                s.page_number,

                s.crop_index
            """
        )

        with self.repository.session() as db:

            rows = db.execute(sql)

            return [

                dict(row._mapping)

                for row in rows

            ]

    # ============================================================
    # Similarity Calculation
    # ============================================================

    def _similarity(
        self,
        query: QueryMolecule,
        candidate: dict,
    ) -> float:
        """
        Compute the Tanimoto similarity between the
        query molecule and a candidate structure.

        Returns
        -------
        float

            Similarity score between 0.0 and 1.0.
        """

        canonical_smiles = candidate.get(
            "canonical_smiles"
        )

        if query.morgan_fingerprint is None:

            return 0.0

        if not canonical_smiles:

            return 0.0

        candidate_mol = Chem.MolFromSmiles(
            canonical_smiles
        )

        if candidate_mol is None:

            return 0.0

        candidate_fp = generate_morgan_fingerprint(
            candidate_mol
        )

        if candidate_fp is None:

            return 0.0

        return tanimoto_similarity(

            query.morgan_fingerprint,

            candidate_fp,

        )


    # ============================================================
    # Search
    # ============================================================

    def search(
        self,
        query: QueryMolecule,
        threshold: float | None = None,
        top_k: int | None = None,
    ) -> list[SearchResult]:
        """
        Perform similarity search.

        Parameters
        ----------
        query
            Prepared query molecule.

        Returns
        -------
        list[SearchResult]
        """

        threshold = (

            self.threshold

            if threshold is None

            else threshold

        )

        top_k = (

            self.top_k

            if top_k is None

            else top_k

        )

        candidates = self._load_candidates()

        results: list[SearchResult] = []

        for candidate in candidates:

            similarity = self._similarity(

                query=query,

                candidate=candidate,

            )

            # Ignore weak matches

            if similarity < threshold:

                continue

            results.append(

                SearchResult(

                    patent_id=candidate["patent_id"],

                    patent_number=candidate["patent_number"],

                    patent_title=candidate["title"],

                    country=candidate["country"],

                    structure_id=candidate["structure_id"],

                    page_number=candidate["page_number"],

                    crop_index=candidate["crop_index"],

                    image_path=candidate["image_path"],

                    smiles=candidate["smiles"],

                    canonical_smiles=candidate["canonical_smiles"],

                    search_type=SearchType.SIMILARITY,

                    matched_by={SearchType.SIMILARITY,},

                    similarity_score=similarity,

                    recognizer_name=candidate["recognizer_name"],

                    recognizer_version=candidate["recognizer_version"],

                    recognizer_confidence=candidate["recognizer_confidence"],

                    backend=candidate["backend"],

                    inference_time=candidate["inference_time"],

                )

            )

        # --------------------------------------------------------
        # Highest similarity first
        # --------------------------------------------------------

        results.sort(

            key=lambda result: (

                result.similarity_score,

                result.patent_number,

            ),

            reverse=True,

    )

        return results[:top_k]