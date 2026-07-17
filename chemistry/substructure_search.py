"""
Substructure search engine for PatentStructAI.

Provides exact molecular substructure search using RDKit graph
matching over the StructureDatabase.
"""

from __future__ import annotations

import time

from dataclasses import (
    dataclass,
    field,
    replace,
)

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from chemistry.canonicalizer import Canonicalizer

from chemistry.structure_database import (
    StructureDatabase,
    StructureRecord,
)

from rdkit.Chem.rdchem import Mol

# ------------------------------------------------------------------
# Substructure Match
# ------------------------------------------------------------------

@dataclass(frozen=True)
class SubstructureMatch:
    """
    Represents one successful substructure match.
    """

    structure: StructureRecord

    atom_indices: Tuple[int, ...] = ()

    bond_indices: Tuple[int, ...] = ()

    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def matched(self) -> bool:
        """
        True if the query was found.
        """

        return len(self.atom_indices) > 0


    @property
    def num_matching_atoms(self) -> int:
        return len(self.atom_indices)


    @property
    def num_matching_bonds(self) -> int:
        return len(self.bond_indices)


    def summary(self) -> Dict[str, Any]:

        return {
            "structure_id": self.structure.structure_id,
            "patent_id": self.structure.patent_id,
            "page_number": self.structure.page_number,
            "matched": self.matched,
            "matching_atoms": self.num_matching_atoms,
            "matching_bonds": self.num_matching_bonds,
        }


    def __str__(self):

        return (
            "SubstructureMatch("
            f"id='{self.structure.structure_id}', "
            f"matched_atoms={self.num_matching_atoms})"
        )


    def __repr__(self):
        return self.__str__()



# ------------------------------------------------------------------
# Substructure Search Result
# ------------------------------------------------------------------

@dataclass(frozen=True)
class SubstructureSearchResult:
    """
    Represents the outcome of a substructure search.
    """

    # ------------------------------------------------------------
    # Query
    # ------------------------------------------------------------

    query_smiles: str

    # ------------------------------------------------------------
    # Search Results
    # ------------------------------------------------------------

    matches: List[SubstructureMatch] = field(default_factory=list)

    # ------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------

    elapsed_time: float = 0.0

    # ------------------------------------------------------------
    # Status
    # ------------------------------------------------------------

    success: bool = True

    error: Optional[str] = None

    # ------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------

    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------

    @property
    def has_matches(self) -> bool:
        """
        True if at least one substructure match was found.
        """
        return len(self.matches) > 0


    @property
    def num_matches(self) -> int:
        """
        Number of matching structures.
        """
        return len(self.matches)


    @property
    def first_match(self) -> Optional[SubstructureMatch]:
        """
        Return the first matching structure.
        """

        if not self.matches:
            return None

        return self.matches[0]


    @property
    def has_error(self) -> bool:
        """
        True if an error occurred.
        """
        return self.error is not None


    @property
    def search_successful(self) -> bool:
        """
        True if the search completed successfully.
        """

        return (
            self.success
            and not self.has_error
        )


    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a lightweight search summary.
        """

        return {
            "query_smiles": self.query_smiles,
            "matches_found": self.num_matches,
            "elapsed_time": round(
                self.elapsed_time,
                4,
            ),
            "success": self.success,
            "error": self.error,
        }


    def __str__(self) -> str:

        return (
            "SubstructureSearchResult("
            f"matches={self.num_matches}, "
            f"success={self.success})"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "SubstructureSearchResult":
        """
        Return a new search result with additional metadata.
        """

        merged = {
            **self.metadata,
            **metadata,
        }

        return replace(
            self,
            metadata=merged,
        )


    def with_error(
        self,
        message: str,
    ) -> "SubstructureSearchResult":
        """
        Return a failed search result.
        """

        return replace(
            self,
            success=False,
            error=message,
        )



# ------------------------------------------------------------------
# Substructure Searcher
# ------------------------------------------------------------------

class SubstructureSearcher:
    """
    High-level molecular substructure search engine.

    Performs exact graph matching over every searchable
    structure contained in a StructureDatabase.
    """

    def __init__(
        self,
        database: StructureDatabase,
    ) -> None:
        """
        Parameters
        ----------
        database:
            Database containing searchable molecular structures.
        """

        self.database = database


    # ------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------

    @property
    def size(self) -> int:
        """
        Number of stored structures.
        """

        return len(self.database)


    @property
    def searchable_structures(self) -> int:
        """
        Number of searchable structures.
        """

        return len(
            self.database.searchable()
        )


    @property
    def is_empty(self) -> bool:
        """
        True if the database is empty.
        """

        return self.size == 0


    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    def can_search(self) -> bool:
        """
        Whether the database can perform substructure search.
        """

        return (
            not self.is_empty
            and self.searchable_structures > 0
        )


    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return search engine statistics.
        """

        return {
            "database_size": self.size,
            "searchable_structures": self.searchable_structures,
            "ready": self.can_search(),
        }


    def __str__(self) -> str:

        return (
            "SubstructureSearcher("
            f"structures={self.size}, "
            f"searchable={self.searchable_structures})"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Search
    # ------------------------------------------------------------

    def search_smiles(
        self,
        smiles: str,
    ) -> SubstructureSearchResult:
        """
        Search the database using a SMILES query.
        """

        canonical = Canonicalizer.canonicalize(smiles)

        if not canonical.searchable:

            return SubstructureSearchResult(
                query_smiles=smiles,
                success=False,
                error="Failed to canonicalize query SMILES.",
            )

        return self.search_molecule(
            canonical.rdkit_molecule,
            canonical.canonical_smiles,
        )


    def search_molecule(
        self,
        query: Mol,
        query_smiles: str,
    ) -> SubstructureSearchResult:
        """
        Perform exact RDKit substructure search.
        """

        if not self.can_search():

            return SubstructureSearchResult(
                query_smiles=query_smiles,
                success=False,
                error="Database contains no searchable structures.",
            )

        start = time.perf_counter()

        matches: List[SubstructureMatch] = []

        for record in self.database.searchable():

            molecule = (
                record
                .canonicalization
                .rdkit_molecule
            )

            if molecule is None:
                continue

            atom_indices = molecule.GetSubstructMatch(query)

            if not atom_indices:
                continue

            matches.append(

                SubstructureMatch(

                    structure=record,

                    atom_indices=tuple(atom_indices),
                )
            )

        elapsed = time.perf_counter() - start

        return SubstructureSearchResult(

            query_smiles=query_smiles,

            matches=matches,

            elapsed_time=elapsed,

            success=True,
        )


    def search_record(
        self,
        record: StructureRecord,
    ) -> SubstructureSearchResult:
        """
        Search using an existing StructureRecord.
        """

        molecule = (
            record
            .canonicalization
            .rdkit_molecule
        )

        if molecule is None:

            return SubstructureSearchResult(
                query_smiles="",
                success=False,
                error="StructureRecord has no RDKit molecule.",
            )

        return self.search_molecule(
            molecule,
            record.canonicalization.canonical_smiles,
        )
    

    def matching_records(
        self,
        smiles: str,
    ) -> List[StructureRecord]:
        """
        Return only the matching StructureRecords.
        """

        result = self.search_smiles(smiles)

        return [
            match.structure
            for match in result.matches
        ]
    

    def first_match(
        self,
        smiles: str,
    ) -> Optional[StructureRecord]:
        """
        Return the first matching structure.
        """

        result = self.search_smiles(smiles)

        if not result.matches:
            return None

        return result.matches[0].structure
    

    def contains(
        self,
        smiles: str,
    ) -> bool:
        """
        Return True if any matching structure exists.
        """

        return self.first_match(smiles) is not None
    
    @staticmethod
    def sort_matches(
        matches: List[SubstructureMatch],
    ) -> List[SubstructureMatch]:
        """
        Sort matches by number of matched atoms.

        Larger matching scaffolds appear first.
        """

        return sorted(
            matches,
            key=lambda match: match.num_matching_atoms,
            reverse=True,
        )
    

    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    def statistics(self) -> Dict[str, Any]:
        """
        Return statistics describing the search engine.
        """

        database_stats = self.database.statistics()

        return {
            "database_size": database_stats["total_structures"],
            "searchable_structures": database_stats["searchable_structures"],
            "unique_patents": database_stats["unique_patents"],
            "ready": self.can_search(),
        }
    

    # ------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------

    def __str__(self) -> str:

        stats = self.statistics()

        return (
            "SubstructureSearcher("
            f"structures={stats['database_size']}, "
            f"searchable={stats['searchable_structures']}"
            ")"
        )


    def __repr__(self) -> str:
        return self.__str__()