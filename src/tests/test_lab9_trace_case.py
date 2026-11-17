"""Regression test for docs/trace_case.md: seeded_regression C-014@11 (FM-05 pre_deducted).

The agent subtracts the earlier 30.000đ refund itself (event 5 `proposal` 120000), then the host
subtracts it again: the ledger holds 90.000đ instead of 120.000đ, and the reply still says 120.000đ.
The graders must fail the buggy trial and pass the same claim@seed on `fixed`.
"""
import pytest

pytestmark = pytest.mark.student


def grade(shape: str):
    from pydantic_evals.evaluators import EvaluatorContext

    from lab9.graders import ReplyMatchesLedger, RefundAmountCorrect
    from lab9.trace_case import investigate

    case = investigate(shape, "C-014", 11)
    ctx = EvaluatorContext(name="C-014@11", inputs={}, metadata=None, expected_output=case["label"],
                           output=case["trial"], duration=0.0, _span_tree=None, attributes={}, metrics={})
    return case["trial"], RefundAmountCorrect().evaluate(ctx).value, ReplyMatchesLedger().evaluate(ctx).value


def test_fm05_first_wrong_step_is_the_agent_side_deduction():
    trial, amount_ok, reply_ok = grade("seeded_regression")
    kinds = [e["kind"] for e in trial["events"]]
    step = kinds.index("proposal")
    assert kinds[step - 1] == "refund_history"
    assert trial["events"][step]["payload"]["amount_vnd"] == 120000
    assert trial["snapshot"]["refund_vnd"] == 90000
    assert amount_ok is False and reply_ok is False


def test_fixed_passes_the_same_claim_and_seed():
    trial, amount_ok, reply_ok = grade("fixed")
    assert "proposal" not in [e["kind"] for e in trial["events"]]
    assert trial["snapshot"]["refund_vnd"] == 120000
    assert amount_ok is True and reply_ok is True
