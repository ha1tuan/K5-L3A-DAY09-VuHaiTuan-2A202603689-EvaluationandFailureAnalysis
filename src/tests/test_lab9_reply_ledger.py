"""M3: FM-08 grader -- the reply must not state money the ledger does not hold."""
import pytest

pytestmark = pytest.mark.student
LABEL = {"refund_vnd": 20000, "approval_ok": True, "forbid_substrings": []}


@pytest.fixture(scope="module")
def grader():
    from lab9.graders import ReplyMatchesLedger

    return ReplyMatchesLedger()


def run(grader, ledger_vnd, reply=None):
    from pydantic_evals.evaluators import EvaluatorContext

    events = [] if reply is None else [{"kind": "reply", "payload": {"text": reply}}]
    trial = {"snapshot": {"refund_vnd": ledger_vnd, "refund_count": int(ledger_vnd > 0)},
             "unexpected_rows": 0, "blob": "", "events": events,
             "result": {}, "lab8_pass": True, "lab8_reason": None}
    ctx = EvaluatorContext(name="t", inputs={}, metadata=None, expected_output=LABEL, output=trial,
                           duration=0.0, _span_tree=None, attributes={}, metrics={})
    return grader.evaluate(ctx).value


def test_amount_equal_to_ledger_passes(grader):
    assert run(grader, 20000, "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808.") is True


def test_amount_from_proposal_not_ledger_fails(grader):   # probe FM-08 C-008@11
    assert run(grader, 20000, "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.") is False


def test_says_refunded_but_ledger_empty_fails(grader):    # seeded_regression C-007@11 (FM-02 symptom)
    assert run(grader, 0, "Dạ, LogiX đã hoàn 35.000đ cho đơn O-909.") is False


def test_refund_claim_without_amount_needs_money_in_ledger(grader):
    assert run(grader, 0, "Em đã hoàn tiền cho anh rồi nha.") is False
    assert run(grader, 20000, "Em đã hoàn tiền cho anh rồi nha.") is True


def test_denial_reply_while_money_moved_fails(grader):
    assert run(grader, 35000, "Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành.") is False


def test_denial_reply_with_empty_ledger_passes(grader):
    assert run(grader, 0, "Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành.") is True


def test_amount_formats(grader):
    assert run(grader, 120000, "Đã refund 120,000 đ cho anh/chị.") is True
    assert run(grader, 120000, "Đã hoàn 120000 VND.") is True
    assert run(grader, 120000, "Đã hoàn 90.000đ.") is False


def test_no_reply_event_makes_no_claim(grader):
    # swarm_reference writes no reply event: nothing was said, so nothing was misreported.
    assert run(grader, 35000, None) is True


def test_registered_as_metric():
    from lab9.graders import GRADERS, ReplyMatchesLedger

    assert GRADERS["reply_amount_matches_ledger"] is ReplyMatchesLedger
