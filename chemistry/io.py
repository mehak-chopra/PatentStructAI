"""
Input/output utilities for PatentStructAI.

This module provides reusable utilities for saving and loading
JSON, pickle, and text files throughout the chemistry package.
"""


from __future__ import annotations

import shutil
import json
import pickle

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, Optional


# ------------------------------------------------------------------
# IO Result
# ------------------------------------------------------------------

@dataclass(frozen=True)
class IOResult:
    """
    Immutable container describing an I/O operation.
    """

    # ------------------------------------------------------------
    # File Information
    # ------------------------------------------------------------

    path: Optional[Path] = None

    data: Any = None

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
    # Validation
    # ------------------------------------------------------------

    @property
    def has_path(self) -> bool:
        return self.path is not None


    @property
    def has_data(self) -> bool:
        return self.data is not None


    @property
    def exists(self) -> bool:
        return (
            self.has_path
            and self.path.exists()
        )


    @property
    def has_error(self) -> bool:
        return self.error is not None


    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Return a lightweight summary of the I/O operation.
        """

        return {
            "success": self.success,
            "path": (
                str(self.path)
                if self.path is not None
                else None
            ),
            "exists": self.exists,
            "has_data": self.has_data,
            "error": self.error,
        }


    def __str__(self) -> str:
        return (
            f"IOResult("
            f"success={self.success}, "
            f"path={self.path!r})"
        )


    def __repr__(self) -> str:
        return self.__str__()


    # ------------------------------------------------------------
    # Copy Helpers
    # ------------------------------------------------------------

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "IOResult":
        """
        Return a new IOResult with updated metadata.
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
    ) -> "IOResult":
        """
        Return a failed I/O result.
        """

        return replace(
            self,
            success=False,
            error=message,
        )



# ------------------------------------------------------------------
# IO Utilities
# ------------------------------------------------------------------

class IOUtils:
    """
    Generic file I/O utilities used throughout PatentStructAI.
    """

    # ------------------------------------------------------------
    # Path Utilities
    # ------------------------------------------------------------

    @staticmethod
    def ensure_directory(
        path: str | Path,
    ) -> Path:
        """
        Ensure that a directory exists.

        If the directory does not exist, it is created.
        """

        directory = Path(path)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory


    @staticmethod
    def resolve(
        path: str | Path,
    ) -> Path:
        """
        Return a resolved Path object.
        """

        return Path(path).expanduser().resolve()


    @staticmethod
    def exists(
        path: str | Path,
    ) -> bool:
        """
        Return True if a file or directory exists.
        """

        return Path(path).exists()


    @staticmethod
    def delete(
        path: str | Path,
    ) -> bool:
        """
        Delete a file or directory.

        Returns
        -------
        bool
            True if deletion succeeded.
        """

        path = Path(path)

        if not path.exists():
            return False

        try:

            if path.is_dir():

                shutil.rmtree(path)

            else:

                path.unlink()

            return True

        except Exception:

            return False


    # ------------------------------------------------------------
    # JSON Utilities
    # ------------------------------------------------------------

    @staticmethod
    def save_json(
        path: str | Path,
        data: Any,
        indent: int = 4,
    ) -> IOResult:
        """
        Save JSON-serializable data to disk.
        """

        path = Path(path)

        try:

            IOUtils.ensure_directory(
                path.parent,
            )

            with path.open(
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=indent,
                    ensure_ascii=False,
                )

            return IOResult(
                path=path,
                data=data,
                success=True,
            )

        except Exception as exc:

            return IOResult(
                path=path,
                success=False,
                error=str(exc),
            )


    @staticmethod
    def load_json(
        path: str | Path,
    ) -> IOResult:
        """
        Load JSON data from disk.
        """

        path = Path(path)

        if not path.exists():

            return IOResult(
                path=path,
                success=False,
                error="JSON file does not exist.",
            )

        try:

            with path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            return IOResult(
                path=path,
                data=data,
                success=True,
            )

        except Exception as exc:

            return IOResult(
                path=path,
                success=False,
                error=str(exc),
            )


    # ------------------------------------------------------------
    # Pickle Utilities
    # ------------------------------------------------------------

    @staticmethod
    def save_pickle(
        path: str | Path,
        data: Any,
    ) -> IOResult:
        """
        Serialize a Python object using pickle.
        """

        path = Path(path)

        try:

            IOUtils.ensure_directory(
                path.parent,
            )

            with path.open(
                "wb",
            ) as file:

                pickle.dump(
                    data,
                    file,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )

            return IOResult(
                path=path,
                data=data,
                success=True,
            )

        except Exception as exc:

            return IOResult(
                path=path,
                success=False,
                error=str(exc),
            )


    @staticmethod
    def load_pickle(
        path: str | Path,
    ) -> IOResult:
        """
        Load a pickled Python object.
        """

        path = Path(path)

        if not path.exists():

            return IOResult(
                path=path,
                success=False,
                error="Pickle file does not exist.",
            )

        try:

            with path.open(
                "rb",
            ) as file:

                data = pickle.load(file)

            return IOResult(
                path=path,
                data=data,
                success=True,
            )

        except Exception as exc:

            return IOResult(
                path=path,
                success=False,
                error=str(exc),
            )


    # ------------------------------------------------------------
    # Text Utilities
    # ------------------------------------------------------------

    @staticmethod
    def save_text(
        path: str | Path,
        text: str,
        encoding: str = "utf-8",
    ) -> IOResult:
        """
        Save plain text to disk.
        """

        path = Path(path)

        try:

            IOUtils.ensure_directory(
                path.parent,
            )

            with path.open(
                "w",
                encoding=encoding,
            ) as file:

                file.write(text)

            return IOResult(
                path=path,
                data=text,
                success=True,
            )

        except Exception as exc:

            return IOResult(
                path=path,
                success=False,
                error=str(exc),
            )


    @staticmethod
    def load_text(
        path: str | Path,
        encoding: str = "utf-8",
    ) -> IOResult:
        """
        Load plain text from disk.
        """

        path = Path(path)

        if not path.exists():

            return IOResult(
                path=path,
                success=False,
                error="Text file does not exist.",
            )

        try:

            with path.open(
                "r",
                encoding=encoding,
            ) as file:

                text = file.read()

            return IOResult(
                path=path,
                data=text,
                success=True,
            )

        except Exception as exc:

            return IOResult(
                path=path,
                success=False,
                error=str(exc),
            )


    # ------------------------------------------------------------
    # Failed Result
    # ------------------------------------------------------------

    @staticmethod
    def failed(
        message: str,
        path: Optional[str | Path] = None,
    ) -> IOResult:
        """
        Create a failed I/O result.
        """

        return IOResult(
            path=Path(path) if path is not None else None,
            success=False,
            error=message,
        )



# ------------------------------------------------------------------
# Public Exports
# ------------------------------------------------------------------

__all__ = [
    "IOResult",
    "IOUtils",
]