"""Pure checks for a native milestone return; never launch or approve work.

The caller supplies native execution observations and retains consumed identities.
The live board and designated integrator still own engineering acceptance.
"""
from __future__ import annotations

from pathlib import PurePosixPath
import re

SCHEMA = "implement-rfc.milestone-return.v1"
IDENTITY = ("run_id", "dispatch_id", "producer_id", "mandate_revision", "milestone")
DISPOSITIONS = {
    "milestone-complete", "continue-milestone", "human-pending", "blocked",
    "cancelled", "pack-complete", "review-request",
}


def validate_return(value: object) -> list[str]:
    """Return structural errors without interpreting evidence as acceptance."""
    required = set(IDENTITY) | {
        "schema", "disposition", "summary", "candidate_revision", "handoff_ref",
        "ownership", "next_objective", "required_pending", "evidence_refs",
    }
    if not isinstance(value, dict) or not required <= value.keys():
        return ["missing required return fields"]
    errors = []
    if value.keys() - required - {"review_request"}:
        errors.append("unknown return fields")
    if value["schema"] != SCHEMA:
        errors.append("unsupported return schema")
    for key in (*IDENTITY, "summary"):
        if not isinstance(value[key], str) or not value[key].strip():
            errors.append(f"invalid {key}")
    disposition = value["disposition"]
    if not isinstance(disposition, str) or disposition not in DISPOSITIONS:
        errors.append("invalid disposition")
    if value["ownership"] not in ("active", "unknown", "quiescent"):
        errors.append("invalid ownership")
    for key in ("required_pending", "evidence_refs"):
        items = value[key]
        if (not isinstance(items, list)
                or any(not isinstance(item, str) or not item.strip() for item in items)
                or len(set(items)) != len(items)):
            errors.append(f"invalid {key}")
    for key in ("handoff_ref", "next_objective"):
        if value[key] is not None and (not isinstance(value[key], str) or not value[key].strip()):
            errors.append(f"invalid {key}")
    ref = value["handoff_ref"]
    if isinstance(ref, str) and (PurePosixPath(ref).is_absolute() or ".." in PurePosixPath(ref).parts
                                 or "\\" in ref or ":" in ref):
        errors.append("handoff_ref must stay relative to the consumer")
    revision = value["candidate_revision"]
    if revision is not None and (not isinstance(revision, str)
                                or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision) is None):
        errors.append("invalid candidate_revision")
    if disposition == "pack-complete" and (
        value["ownership"] != "quiescent" or value["required_pending"]
        or value["next_objective"] is not None or not value["evidence_refs"]
    ):
        errors.append("pack completion has outstanding obligations or missing evidence")
    if disposition == "milestone-complete" and (
        value["ownership"] != "quiescent" or not value["handoff_ref"] or not value["evidence_refs"]
    ):
        errors.append("milestone completion requires quiescence, handoff and evidence")
    review = value.get("review_request")
    if disposition == "review-request":
        if (not isinstance(review, dict) or set(review) != {"role", "candidate_ref", "assignment"}
                or review.get("role") not in ("rfc-reviewer", "rfc-reviewer-critical")
                or any(not isinstance(review.get(key), str) or not review[key].strip()
                       for key in ("candidate_ref", "assignment"))
                or value["ownership"] != "quiescent"):
            errors.append("invalid review request")
    elif "review_request" in value:
        errors.append("unexpected review request")
    return errors


def continuation(returned: object, assignment: dict, *, execution: str,
                 consumed=(), cancelled: bool = False, review_relay: bool = False,
                 prior_partial: dict | None = None) -> dict:
    """Suggest a control action from explicit observations, without mutation.

    execution describes the producer AND its owned children/commands, not merely
    the arrival of a message. Unknown ownership requires reconciliation. A caller
    records the returned consumption key only when it actually consumes a result.
    """
    def result(action, reason, key=None):
        return {"action": action, "reason": reason, "consume_key": key,
                "engineering_acceptance": "not-evaluated"}

    if cancelled:
        return result("stop", "current user mandate is cancelled; account for outstanding effects")
    errors = validate_return(returned)
    if errors:
        return result("reconcile" if execution == "unknown" else "clarify", "; ".join(errors))
    if any(returned[key] != assignment.get(key) for key in IDENTITY):
        return result("ignore-stale", "result does not match the current native assignment and mandate")
    # A partial invocation may return repeatedly under one dispatch. The native
    # caller supplies a new dispatch identity for an explicitly renewed assignment.
    key = tuple(returned[field] for field in IDENTITY)
    if any(tuple(item) == key for item in consumed):
        return result("ignore-duplicate", "this exact dispatch result was already consumed")
    if returned["disposition"] == "cancelled":
        return result("stop", "producer reports cancellation; reconcile effects before any new mandate", key)
    if execution == "active" or returned["ownership"] == "active":
        return result("wait", "owned execution remains active")
    if execution != "quiescent" or returned["ownership"] != "quiescent":
        return result("reconcile", "native effects and ownership are not established")
    if returned["disposition"] == "review-request" and not review_relay:
        return result("clarify", "native independent-review relay has not been qualified")
    if returned["disposition"] == "continue-milestone" and prior_partial is not None:
        progress_fields = ("producer_id", "milestone", "candidate_revision", "handoff_ref",
                           "next_objective", "required_pending", "evidence_refs", "summary")
        if all(returned[field] == prior_partial.get(field) for field in progress_fields):
            return result("investigate", "repeated partial return supplies no new progress or actionable step")
    action = {
        "milestone-complete": "fresh-integrator",
        "continue-milestone": "resume-integrator",
        "human-pending": "pending",
        "blocked": "pending",
        "pack-complete": "report-closeout",
        "review-request": "relay-review" if review_relay else "clarify",
    }[returned["disposition"]]
    return result(action, "consume references; engineering judgment remains with the designated integrator", key)
