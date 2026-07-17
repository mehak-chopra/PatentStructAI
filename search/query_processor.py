"""
PatentStructAI Query Processor.

Converts user queries into QueryMolecule objects.

Supported Inputs
----------------

- SMILES
- Chemical Structure Images

Future

- MOL
- MOLBLOCK
- InChI
- InChIKey
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rdkit import Chem

from chemistry.chemistry_utils import (
    QueryMolecule,
    prepare_query,
)

from chemistry.recognizers.molnextr_recognizer import (
    MolNexTRRecognizer,
)


# ============================================================
# Query Sources
# ============================================================

class QuerySource:
    """
    Supported query types.
    """

    SMILES = "smiles"

    IMAGE = "image"


# ============================================================
# Query Result
# ============================================================

@dataclass
class ProcessedQuery:
    """
    Result returned by QueryProcessor.
    """

    source: str

    molecule: QueryMolecule

    original_input: str


# ============================================================
# Query Processor
# ============================================================

class QueryProcessor:
    """
    Converts user input into QueryMolecule objects.

    The search engine never talks directly to
    MolNexTR or RDKit.

    It only talks to this class.
    """

    def __init__(self):

        self._recognizer = None


    # ========================================================
    # Lazy MolNexTR Loader
    # ========================================================

    @property
    def recognizer(
        self,
    ) -> MolNexTRRecognizer:
        """
        Lazily initialize the MolNexTR recognizer.

        SMILES queries never load the neural network.
        """

        if self._recognizer is None:

            self._recognizer = MolNexTRRecognizer()

        return self._recognizer


    # ========================================================
    # Process SMILES
    # ========================================================

    def process_smiles(
        self,
        smiles: str,
    ) -> ProcessedQuery:
        """
        Convert a SMILES string into a QueryMolecule.
        """

        molecule = prepare_query(
            smiles
        )

        if molecule is None:

            raise ValueError(
                "Invalid SMILES string."
            )

        return ProcessedQuery(

            source=QuerySource.SMILES,

            molecule=molecule,

            original_input=smiles,

        )


    # ========================================================
    # Molecular Recognition
    # ========================================================

    def recognize_structure(
        self,
        image: Path,
    ) -> str:

        if not image.exists():

            raise FileNotFoundError(
                image
            )

        result = self.recognizer.predict(
            image
        )

        if not result.success:

            raise RuntimeError(
                result.failure_reason
            )

        if not result.smiles:

            raise RuntimeError(
                "MolNexTR returned no SMILES."
            )

        return result.smiles


    # ========================================================
    # Process Image
    # ========================================================

    def process_image(
        self,
        image: Path,
    ) -> ProcessedQuery:
        """
        Convert a chemical structure image into
        a QueryMolecule.
        """

        smiles = self.recognize_structure(
            image
        )

        molecule = prepare_query(
            smiles
        )

        if molecule is None:

            raise RuntimeError(

                "Unable to prepare recognized molecule."

            )

        return ProcessedQuery(

            source=QuerySource.IMAGE,

            molecule=molecule,

            original_input=str(image),

        )


    # ========================================================
    # Generic Processing
    # ========================================================

    def process(
        self,
        query,
    ) -> ProcessedQuery:
        """
        Automatically process the supplied query.

        Parameters
        ----------
        query

            Path  -> image

            str   -> SMILES
        """

        if isinstance(
            query,
            Path,
        ):

            return self.process_image(
                query
            )

        if isinstance(
            query,
            str,
        ):

            return self.process_smiles(
                query
            )

        raise TypeError(

            f"Unsupported query type: {type(query)}"

        )