"""Shared, solver-independent algorithms for magic-state factory workflows.

The user-facing workflows live in their own directories.  This package holds
the mathematics they genuinely share: parent analysis, exact fault
verification, and gate metrics.  Keeping one implementation prevents silent
drift without copying thousands of lines between directories.
"""

