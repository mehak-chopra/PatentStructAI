from __future__ import annotations

from collections import defaultdict

from search.search_result import (
    SearchResult,
    SearchType,
)


# ============================================================
# Search Ranker
# ============================================================

class SearchRanker:
    """
    Combines search results from multiple search
    algorithms into one ranked result list.

    Responsibilities
    ----------------

    • Merge duplicate structures

    • Prioritize Exact matches

    • Rank Similarity matches

    • Keep Substructure matches together

    • Produce one final ordered result list
    """

    def __init__(
        self,
    ):

        self.priority = {

            SearchType.EXACT: 3,

            SearchType.SUBSTRUCTURE: 2,

            SearchType.SIMILARITY: 1,

        }
    

    # ============================================================
    # Group Duplicate Results
    # ============================================================

    def _group_duplicates(
        self,
        *result_sets: list[SearchResult],
    ) -> dict[int, list[SearchResult]]:
        """
        Group search results by structure ID.

        The same structure may be returned by multiple
        search algorithms.

        Returns
        -------
        dict

            structure_id -> list[SearchResult]
        """

        grouped: dict[
            int,
            list[SearchResult],
        ] = defaultdict(list)

        for result_set in result_sets:

            for result in result_set:

                grouped[
                    result.structure_id
                ].append(
                    result
                )

        return grouped


    # ============================================================
    # Merge Duplicate Results
    # ============================================================

    def _merge_group(
        self,
        results: list[SearchResult],
    ) -> SearchResult:
        """
        Merge multiple search results referring to the
        same structure.

        Rules
        -----

        1. Exact > Substructure > Similarity

        2. Keep the highest similarity score.

        3. Preserve all patent metadata.

        Returns
        -------
        SearchResult
        """

        if len(results) == 1:

            return results[0]

        # ----------------------------------------------------
        # Highest priority search type
        # ----------------------------------------------------

        best = max(

            results,

            key=lambda result: self.priority[
                result.search_type
            ],

        )

        # ----------------------------------------------------
        # Best similarity score
        # ----------------------------------------------------

        similarity_scores = [

            result.similarity_score

            for result in results

            if result.similarity_score is not None

        ]

        if similarity_scores:

            best.similarity_score = max(
                similarity_scores
            )


        # ----------------------------------------------------
        # Merge search modes
        # ----------------------------------------------------

        best.matched_by = set()

        for result in results:

            best.matched_by.update(
                result.matched_by
            )

        # ----------------------------------------------------
        # Best similarity score
        # ----------------------------------------------------

        similarity_scores = [

            result.similarity_score

            for result in results

            if result.similarity_score is not None

        ]

        if similarity_scores:

            best.similarity_score = max(
                similarity_scores
            )

        return best


    # ============================================================
    # Rank Results
    # ============================================================

    def rank(
        self,
        exact_results: list[SearchResult],
        substructure_results: list[SearchResult],
        similarity_results: list[SearchResult],
    ) -> list[SearchResult]:
        """
        Merge, de-duplicate and rank search results.

        Ranking Strategy
        ----------------

        1. Merge duplicate structures.

        2. Exact matches first.

        3. Substructure matches second.

        4. Similarity matches last.

        5. Within the same search type,
            higher similarity appears first.

        Returns
        -------
        list[SearchResult]
        """

        grouped = self._group_duplicates(

            exact_results,

            substructure_results,

            similarity_results,

        )

        merged_results = [

            self._merge_group(group)

            for group in grouped.values()

        ]

        merged_results.sort(

            key=lambda result: (

                self.priority[
                    result.search_type
                ],

                result.similarity_score
                if result.similarity_score is not None
                else -1.0,

            ),

            reverse=True,

        )

        return merged_results