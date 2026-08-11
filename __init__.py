"""Wuthering Waves beta version comparison plugin."""

from gsuid_core.sv import Plugins

Plugins(
    name="WWBetaDiff",
    force_prefix=["ww"],
    allow_empty_prefix=False,
)

from . import command  # noqa: E402, F401
