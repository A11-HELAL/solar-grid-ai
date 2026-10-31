"""Pure physical validation guards (H1-H5) and health anomaly checks."""

from typing import NamedTuple


class GuardrailResult(NamedTuple):
    final_kw: float
    guardrail_activated: bool
    rule_hit: str
    fallback_used: bool


def apply_guardrails(
    raw_model_kw: float,
    clear_sky_kw: float,
    is_night: bool,
    inverter_max_kw: float,
    capacity_kwp: float,
) -> GuardrailResult:
    """Enforce hard physical guardrails H1 through H5."""
    raise NotImplementedError("solar_core.validator.apply_guardrails is a stub")
