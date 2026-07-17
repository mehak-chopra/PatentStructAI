"""
PatentStructAI Substructure Search.

Find patents containing the query molecule as a
substructure.

Workflow
--------

QueryMolecule
    │
    ▼
Load Searchable Structures
    │
    ▼
RDKit Substructure Matching
    │
    ▼
SearchResult[]
"""

from __future__ import annotations

from rdkit import Chem
from sqlalchemy import text

from chemistry.chemistry_utils import (
    QueryMolecule,
)

from database.patent_repository import (
    PatentRepository,
)

from search.search_result import (
    SearchResult,
    SearchType,
)

from rdkit import DataStructs


# ============================================================
# Substructure Search
# ============================================================

class SubstructureSearch:
    """
    Search patents containing the query molecule
    as a substructure.
    """

    def __init__(
        self,
        repository: PatentRepository | None = None,
        use_chirality: bool = False,
    ):

        self.repository = (

            repository

            if repository is not None

            else PatentRepository()

        )

        self.use_chirality = use_chirality


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
    # Substructure Matching
    # ============================================================

    def _substructure_match(
        self,
        query: QueryMolecule,
        candidate: dict,
    ) -> tuple[bool, tuple]:
        """
        Perform RDKit substructure matching.

        Returns
        -------
        tuple

            (
                is_match,
                atom_matches
            )
        """

        canonical_smiles = candidate.get(
            "canonical_smiles"
        )

        if not canonical_smiles:

            return False, ()

        candidate_mol = Chem.MolFromSmiles(
            canonical_smiles
        )

        if candidate_mol is None:

            return False, ()

        if query.mol is None:

            return False, ()
        
        query_mol = Chem.Mol(query.mol)

        if not self.use_chirality:
            Chem.RemoveStereochemistry(query_mol)

        matches = candidate_mol.GetSubstructMatches(
            query_mol,
            useChirality=self.use_chirality,
        )

        if not matches:
            return False, ()

        return True, matches
        "return len(matches) > 0"
        "return matches"


    # ============================================================
    # Fingerprint Screen
    # ============================================================

    def _passes_fingerprint_screen(
        self,
        query: QueryMolecule,
        candidate: dict,
    ) -> bool:
        """
        Quickly reject molecules that cannot possibly
        contain the query.

        Returns
        -------
        bool
        """

        smiles = candidate.get(
            "canonical_smiles"
        )

        if not smiles:

            return False

        candidate_mol = Chem.MolFromSmiles(
            smiles
        )

        if candidate_mol is None:

            return False

        candidate_fp = Chem.PatternFingerprint(
            candidate_mol
        )

        return DataStructs.AllProbeBitsMatch(
            query.pattern_fingerprint,
            candidate_fp,
        )

    # ============================================================
    # Search
    # ============================================================

    def search(
        self,
        query: QueryMolecule,
    ) -> list[SearchResult]:
        """
        Perform substructure search.

        Parameters
        ----------
        query
            Prepared query molecule.

        Returns
        -------
        list[SearchResult]
        """

        candidates = self._load_candidates()

        results: list[SearchResult] = []

        for candidate in candidates:

            # --------------------------------------------
            # Fast fingerprint screening
            # --------------------------------------------

            if not self._passes_fingerprint_screen(
                query,
                candidate,
            ):
                continue

            # --------------------------------------------
            # Exact RDKit substructure check
            # --------------------------------------------

            matched, atom_matches = self._substructure_match(
                query,
                candidate,
            )

            if not matched:
                continue

            # --------------------------------------------
            # Create SearchResult
            # --------------------------------------------

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

                    search_type=SearchType.SUBSTRUCTURE,

                    matched_by={SearchType.SUBSTRUCTURE,},

                    similarity_score=None,

                    recognizer_name=candidate["recognizer_name"],

                    recognizer_version=candidate["recognizer_version"],

                    recognizer_confidence=candidate["recognizer_confidence"],

                    backend=candidate["backend"],

                    inference_time=candidate["inference_time"],

                )

            )

        return results