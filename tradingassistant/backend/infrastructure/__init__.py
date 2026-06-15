"""Runtime infrastructure abstractions and default implementations.

This sub-package provides unified interfaces for caching, topic broadcast,
and subscription registration, with MEMORY-based default implementations for
the current phase. Future Redis migration should add new backend implementations
here rather than changing business module call sites.
"""
