"""
DMS-Eval Core Benchmark Package
===============================
Provides shared dataset definitions, ontology constants, evaluation routines,
and model runners for the DMS-Eval nano-scale driver monitoring benchmark.
"""

__version__ = "1.1.0"

from .protocol import ProtocolError, load_protocol, validate_protocol

__all__ = ["ProtocolError", "load_protocol", "validate_protocol"]
