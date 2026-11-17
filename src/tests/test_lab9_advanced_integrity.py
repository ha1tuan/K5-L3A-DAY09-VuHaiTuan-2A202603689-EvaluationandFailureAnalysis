"""M7: integrity_check beyond the public traps (duplicates, relabelled slices, hand-edited metrics...)."""
import copy

import pytest

pytestmark = pytest.mark.student

ROWS = [{"item_id": f"E-{i:03d}", "seed": s, "slices": ["money_movement"] if i < 2 else [],
         "pass_rate": i != 3 or s != 2, "secret_leak": False, "cost": 1.0}
        for i in range(4) for s in (1, 2)]
SPEC = {"eval_set_version": "v2",
        "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True,
                     "threshold": {"min": 0.8, "no_significant_drop": True}},
                    {"id": "secret_leak", "kind": "safety", "blocking": True, "threshold": {"max": 0}}],
        "slices": [{"name": "money_movement", "metric": "pass_rate", "min": 0.9,
                    "no_significant_drop": True, "blocking": True}]}


def report(rows=None, **over):
    from lab9.eval import aggregate

    rows = copy.deepcopy(ROWS if rows is None else rows)
    rep = {"manifest": {"eval_set_sha": "x", "items": 4, "seeds": [1, 2]}, "rows": rows,
           "evaluator_failures": [], "metrics": aggregate(rows, ["pass_rate", "secret_leak"])}
    rep.update(over)
    return rep


@pytest.fixture(scope="module")
def check():
    from lab9.gate import integrity_check

    return integrity_check


def test_clean_report_and_self_compare_are_trusted(check):
    base = report()
    assert check(base, base, SPEC) == []
    assert check(report(), base, SPEC, SPEC) == []


def test_duplicate_row_replacing_a_failing_one(check):
    rows = copy.deepcopy(ROWS)
    rows[7] = copy.deepcopy(rows[6])            # E-003@2 (failing) -> second copy of E-003@1
    assert check(report(rows), report(), SPEC)


def test_evaluator_failures_on_a_green_run(check):
    assert check(report(evaluator_failures=["E-001@1:SecretLeak:boom"]), report(), SPEC)


def test_missing_metric_key_in_a_row(check):
    rep = report()
    del rep["rows"][7]["pass_rate"]               # metrics still computed from the full rows
    assert check(rep, report(), SPEC)


def test_hand_edited_metric_value(check):
    rep = report()
    rep["metrics"]["pass_rate"] = 1.0           # rows say 7/8
    assert check(rep, report(), SPEC)


def test_inf_metric(check):
    rep = report()
    rep["metrics"]["pass_rate"] = float("inf")
    assert check(rep, report(), SPEC)


def test_item_relabelled_out_of_a_slice(check):
    rows = copy.deepcopy(ROWS)
    for r in rows:
        if r["item_id"] == "E-001":
            r["slices"] = []
    assert check(report(rows), report(), SPEC)


def test_manifest_seeds_disagree_with_rows(check):
    rep = report()
    rep["manifest"]["seeds"] = [1]
    assert check(rep, report(), SPEC)


@pytest.mark.parametrize("loosen", [
    lambda s: s["metrics"][1]["threshold"].update(max=1),                  # safety max raised
    lambda s: s["metrics"][0].update(blocking=False),                      # blocking -> warn
    lambda s: s["metrics"].pop(1),                                         # metric removed
    lambda s: s["metrics"][0]["threshold"].pop("no_significant_drop"),     # CI test dropped
    lambda s: s["slices"][0].update(min=0.5),                              # slice floor lowered
    lambda s: s["slices"][0].pop("no_significant_drop"),                   # slice CI dropped
    lambda s: s.update(slices=[]),                                         # slice removed
    lambda s: s.update(eval_set_version="v2.1"),                           # version bump, same data
    lambda s: s.update(bootstrap={"n_resamples": 1000, "rng": 7}),         # re-rolled bootstrap rng
])
def test_ratchet(check, loosen):
    loose = copy.deepcopy(SPEC)
    loosen(loose)
    assert check(report(), report(), loose, SPEC)


def test_ratchet_allows_stricter(check):
    strict = copy.deepcopy(SPEC)
    strict["metrics"][0]["threshold"]["min"] = 0.85
    strict["slices"].append({"name": "adversarial", "metric": "pass_rate", "min": 0.9, "blocking": True})
    assert check(report(), report(), strict, SPEC) == []
