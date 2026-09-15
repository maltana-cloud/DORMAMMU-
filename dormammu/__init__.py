"""Canonical DORMAMMU package identity.

The implementation namespace remains ``devintel`` temporarily for backward
compatibility. New integrations should identify the distribution and product
as ``dormammu`` while legacy imports continue to resolve through ``devintel``.
"""

from devintel import __version__

__all__ = ["__version__"]
