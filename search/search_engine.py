"""
PatentStructAI Unified Search Engine.

Coordinates all supported search algorithms.

Workflow
--------

User Input
    │
    ▼
Query Processor
    │
    ▼
Prepared Query
    │
    ├───────────────┐
    │               │
    ▼               ▼
Exact        Substructure
    │               │
    └───────┬───────┘
            ▼
        Similarity
            ▼
        Ranking Engine
            ▼
        Final Results
"""

from __future__ import annotations

from pathlib import Path

from database.patent_repository import (
    PatentRepository,
)

from search.query_processor import (
    QueryProcessor,
)

from search.exact_search import (
    ExactSearch,
)

from search.substructure_search import (
    SubstructureSearch,
)

from search.similarity_search import (
    SimilaritySearch,
)

from search.search_result import (
    SearchResult,
)

from search.ranking import (
    SearchRanker,
)


# ============================================================
# Search Engine
# ============================================================

class SearchEngine:
    """
    High-level search orchestrator.

    This class coordinates all search algorithms while
    keeping them independent from one another.
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

        self.query_processor = QueryProcessor()

        self.exact_search = ExactSearch(
            self.repository,
        )

        self.substructure_search = SubstructureSearch(
            self.repository,
        )

        self.similarity_search = SimilaritySearch(
            self.repository,
        )

        self.ranker = SearchRanker()


    # ============================================================
    # Unified Search
    # ============================================================

    def search(
        self,
        query: str | Path,
    ) -> dict[str, list[SearchResult]]:
        """
        Run every supported search algorithm.

        Parameters
        ----------
        query

            SMILES string

            or

            Path to a structure image.

        Returns
        -------
        dict

            {
                "exact": [...],
                "substructure": [...],
                "similarity": [...]
            }
        """

        processed_query = self.query_processor.process(
            query
        )

        exact_results = self.exact_search.search(
            processed_query.molecule,
        )

        substructure_results = self.substructure_search.search(
            processed_query.molecule,
        )

        similarity_results = self.similarity_search.search(
            processed_query.molecule,
        )

        return self.ranker.rank(
                exact_results,
                substructure_results,
                similarity_results,
        )


    # ============================================================
    # Exact Search Only
    # ============================================================

    def exact(
        self,
        query: str | Path,
    ) -> list[SearchResult]:
        """
        Run only exact search.
        """

        processed = self.query_processor.process(
            query
        )

        return self.exact_search.search(
            processed.molecule
        )


    # ============================================================
    # Substructure Search Only
    # ============================================================

    def substructure(
        self,
        query: str | Path,
    ) -> list[SearchResult]:
        """
        Run only substructure search.
        """

        processed = self.query_processor.process(
            query
        )

        return self.substructure_search.search(
            processed.molecule
        )


    # ============================================================
    # Similarity Search Only
    # ============================================================

    def similarity(
        self,
        query: str | Path,
        threshold: float | None = None,
        top_k: int | None = None,
    ) -> list[SearchResult]:
        """
        Run only similarity search.
        """

        processed = self.query_processor.process(
            query
        )

        return self.similarity_search.search(

            processed.molecule,

            threshold=threshold,

            top_k=top_k,

        )