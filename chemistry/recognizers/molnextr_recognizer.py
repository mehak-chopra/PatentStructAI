"""
MolNexTR recognizer implementation.

This module wraps the external MolNexTR library behind the
BaseRecognizer interface so that the rest of PatentStructAI
remains independent of any specific OCR model.
"""

from __future__ import annotations

import time
import logging
from pathlib import Path
from typing import Any, Dict

from chemistry.recognition_result import RecognitionResult
from chemistry.recognizers.base import BaseRecognizer

# External recognizer
from MolNexTR import get_predictions

logger = logging.getLogger(__name__)

class MolNexTRRecognizer(BaseRecognizer):
    """
    Wrapper around the MolNexTR chemical structure recognition model.

    This class converts the raw MolNexTR dictionary output into a
    standardized RecognitionResult object used throughout the project.
    """

    NAME = "MolNexTR"

    VERSION = "1.0.2"

    def __init__(self) -> None:
        """
        Initialize the recognizer.

        MolNexTR internally uses a singleton model, so we only keep
        track of whether it has already been initialized.
        """

        self._loaded = False

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def version(self) -> str:
        return self.VERSION

    @property
    def is_loaded(self) -> bool:
        return self._loaded


    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> None:
        """
        Load the MolNexTR model.

        MolNexTR internally manages a singleton model, so we simply
        trigger a lightweight initialization the first time this method
        is called.
        """

        if self._loaded:
            return

        self._loaded = True


    def unload(self) -> None:
        """
        Mark the recognizer as unloaded.

        MolNexTR currently manages its own singleton instance,
        therefore we cannot explicitly free GPU memory here.
        This method exists for API consistency.
        """

        self._loaded = False


    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(
        self,
        image_path: str | Path,
        **kwargs: Any,
    ) -> RecognitionResult:
        """
        Recognize a chemical structure image.

        Parameters
        ----------
        image_path
            Path to the cropped chemical structure image.

        Returns
        -------
        RecognitionResult
        """

        self.load()

        image_path = Path(image_path)

        if not image_path.exists():
            logger.error("Image not found: %s", image_path)

            return RecognitionResult.failed(
                image_path=image_path,
                recognizer=self.name,
                message=f"Image does not exist: {image_path}",
                recognizer_version=self.version,
            )

        logger.info("Running MolNexTR on %s", image_path.name)

        start = time.perf_counter()

        try:

            prediction: Dict[str, Any] = get_predictions(
                str(image_path),
                smiles=True,
                atoms_bonds=True,
                predicted_molfile=True,
            )

            logger.info(
                "Recognition completed successfully for %s",
                image_path.name,
            )

            elapsed = time.perf_counter() - start

            return RecognitionResult(

                image_path=image_path,

                recognizer=self.name,

                recognizer_version=self.version,

                smiles=prediction.get("predicted_smiles"),

                molblock=prediction.get("predicted_molfile"),

                atoms=prediction.get("atom_sets", []),

                bonds=prediction.get("bond_sets", []),

                device=prediction.get("device_info"),

                inference_time=elapsed,

                success=True,

                metadata={
                    "backend": "MolNexTR",
                    "model_version": self.version,
                    "filename": image_path.name,
                    "extension": image_path.suffix,
                    "stem": image_path.stem,
                },
            )

        except Exception as exc:

            elapsed = time.perf_counter() - start

            logger.exception(
                "MolNexTR failed on %s",
                image_path,
            )

            return RecognitionResult.failed(
                image_path=image_path,
                recognizer=self.name,
                message=str(exc),
                inference_time=elapsed,
                recognizer_version=self.version,
            )


    # ------------------------------------------------------------------
    # Batch Prediction
    # ------------------------------------------------------------------

    def predict_batch(
        self,
        image_paths: list[str | Path],
        **kwargs: Any,
    ) -> list[RecognitionResult]:
        """
        Recognize multiple molecular structure images.

        Parameters
        ----------
        image_paths
            Iterable of image paths.

        Returns
        -------
        list[RecognitionResult]
            Recognition result for every image.
        """

        results: list[RecognitionResult] = []

        for image_path in image_paths:
            results.append(
                self.predict(
                    image_path,
                    **kwargs,
                )
            )

        return results


    # ------------------------------------------------------------------
    # Recognizer Capabilities
    # ------------------------------------------------------------------

    @property
    def supports_batch(self) -> bool:
        """
        Whether the recognizer can process multiple images.

        The wrapper exposes batch prediction regardless of whether
        the underlying model performs native batching.
        """
        return True


    @property
    def supports_gpu(self) -> bool:
        """
        Whether GPU inference is supported.
        """
        return True


    @property
    def supports_cpu(self) -> bool:
        """
        Whether CPU inference is supported.
        """
        return True


    @property
    def supports_atoms(self) -> bool:
        """
        Whether atom coordinates are returned.
        """
        return True


    @property
    def supports_bonds(self) -> bool:
        """
        Whether bond information is returned.
        """
        return True


    @property
    def supports_molblock(self) -> bool:
        """
        Whether MolBlock generation is supported.
        """
        return True


    @property
    def supports_smiles(self) -> bool:
        """
        Whether SMILES generation is supported.
        """
        return True


    @property
    def supports_confidence(self) -> bool:
        """
        MolNexTR currently does not expose an overall confidence score.
        """
        return False


    @property
    def supports_canonical_smiles(self) -> bool:
        """
        Canonicalization is handled by PatentStructAI,
        not by the recognizer.
        """
        return False



