"""
Abstract base class for all molecular image recognizers.

Every recognizer (MolNexTR, MolScribe, future models)
must inherit from this class and return a RecognitionResult.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from chemistry.recognition_result import RecognitionResult


class BaseRecognizer(ABC):
    """
    Base interface for molecular image recognition engines.
    """


    @property
    @abstractmethod
    def name(self) -> str:
        """
        Human-readable recognizer name.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def version(self) -> str:
        """
        Version of the recognizer or model.
        """
        raise NotImplementedError


    @abstractmethod
    def predict(
        self,
        image_path: Union[str, Path],
    ) -> RecognitionResult:
        """
        Run molecular recognition on a single image.

        Parameters
        ----------
        image_path:
            Path to a molecular structure image.

        Returns
        -------
        RecognitionResult
        """
        raise NotImplementedError


    @abstractmethod
    def predict_batch(
        self,
        image_paths: list[Union[str, Path]],
    ) -> list[RecognitionResult]:
        """
        Run molecular recognition on multiple images.

        Parameters
        ----------
        image_paths:
            List of image paths.

        Returns
        -------
        List[RecognitionResult]
        """
        raise NotImplementedError


    @abstractmethod
    def load(self) -> None:
        """
        Load the underlying recognition model into memory.

        Heavy initialization (weights, tokenizer, etc.)
        should happen here rather than in __init__.
        """
        raise NotImplementedError


    @abstractmethod
    def unload(self) -> None:
        """
        Release model resources.

        GPU memory and large objects should be freed here.
        """
        raise NotImplementedError


    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """
        True if the recognizer is currently loaded.
        """
        raise NotImplementedError


    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    @property
    def supports_batch(self) -> bool:
        """
        Whether the recognizer supports batch inference.

        Override in subclasses if supported.
        """
        return False


    @property
    def supports_gpu(self) -> bool:
        """
        Whether the recognizer can utilize CUDA acceleration.
        """
        return False


    @property
    def supports_atoms(self) -> bool:
        """
        Whether atom coordinates are returned.
        """
        return False


    @property
    def supports_bonds(self) -> bool:
        """
        Whether bond information is returned.
        """
        return False


    @property
    def supports_molblock(self) -> bool:
        """
        Whether MolBlock output is available.
        """
        return False


    @property
    def supports_confidence(self) -> bool:
        """
        Whether recognition confidence scores are available.
        """
        return False


    @property
    def supports_canonical_smiles(self) -> bool:
        """
        Whether canonical SMILES are produced directly.

        Some recognizers only output raw SMILES and require
        RDKit canonicalization afterwards.
        """
        return False


    @property
    def supports_graph_output(self) -> bool:
        """
        Whether the recognizer produces an explicit molecular graph.

        Graph output is required for advanced graph matching,
        visualization, and future GNN-based search.
        """
        return False


