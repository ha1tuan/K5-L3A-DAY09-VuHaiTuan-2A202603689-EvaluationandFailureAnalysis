# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `<shape> <claim>@<seed>`, run ID trong report |
| Triệu chứng | Grader nào fail; reply nói gì so với ledger ghi gì |
| Bước sai đầu tiên | Số thứ tự event + kind + trích payload (≤1 dòng) |
| Vì sao là bước *đầu tiên* | Các bước trước đó đúng ra sao (dẫn số event) |
| Failure mode | Mã FM-xx trong `docs/failure_taxonomy.md` |
| Đối chứng | Cùng claim@seed trên shape `fixed`: bước đó khác thế nào |
| Regression test | Tên test + grader/assert nào bắt được; đã thấy fail trên variant lỗi và pass trên `fixed` chưa |
| Chưa chắc chắn | Điều trace không chứng minh được |

## Case của nhóm: `seeded_regression` C-014@11 (FM-05)

```bash
python -m lab9.trace_case --shape seeded_regression --claim C-014 --seed 11
python -m lab9.trace_case --shape fixed --claim C-014 --seed 11
```

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-014@11`, trace `R-seeded_regression-C-014-s11`, report run `E-seeded_regression-20261117-f0d3` (row `E-014`, seed 11) |
| Triệu chứng | Lab 8 grader FAIL (`proposal_mismatch`); `refund_amount_correct` FAIL; `reply_amount_matches_ledger` FAIL. Reply nói "đã hoàn **120.000đ**", nhưng ledger ghi **90.000đ**, trong khi nhãn là 120.000đ. Khách bị hoàn thiếu 30.000đ và được báo sai số tiền. |
| Bước sai đầu tiên | **Event 5 `proposal` `{"amount_vnd": 120000}`**: agent tự trừ 30.000đ đã hoàn trước đó khỏi quote 150.000đ, rồi gửi 120.000đ cho host `issue_refund`. Host vốn tự trừ phần đã hoàn, nên trừ thêm lần nữa: 120.000 − 30.000 = 90.000đ (`refund_effects[0].amount_vnd = 90000`). |
| Vì sao là bước *đầu tiên* | Event 1 `handoff` đúng scope (`owner_order_only`, 3 tool đọc). Event 2 `investigator` đọc đúng DB: O-515 trễ 5 ngày, `shipping_fee_vnd` 30.000, `damage_verified=true`. Event 3 `quote` đúng chính sách: `parts` {SHIP-LATE-03: 30.000, DMG-04: 150.000}, lấy max nên ra 150.000đ. Event 4 `refund_history` (`refunded_vnd` 30.000) chỉ là đọc, chưa sai: `honest_refactor` cũng gọi tool này mà vẫn đúng. Sai bắt đầu khi agent **dùng** con số đó để tự trừ ở event 5. |
| Failure mode | **FM-05 pre_deducted** (layer tool/schema: hiểu sai contract của `issue_refund`, không biết host đã tự trừ phần đã hoàn). Kéo theo FM-08: reply báo số tự tính (120.000đ), không phải số host ghi (90.000đ). |
| Đối chứng | `fixed C-014@11`: event 3 `quote` 150.000đ, **không có** event `refund_history` / `proposal`. Agent gửi thẳng 150.000đ, host trừ 30.000đ, ledger ghi 120.000đ = nhãn. Reply "đã hoàn 120.000đ" khớp ledger. Lab 8 grader PASS. |
| Regression test | `src/tests/test_lab9_trace_case.py`: `test_fm05_first_wrong_step_is_the_agent_side_deduction` khẳng định event `proposal` 120.000đ đứng ngay sau `refund_history`, ledger 90.000đ, `RefundAmountCorrect` và `ReplyMatchesLedger` đều FAIL. `test_fixed_passes_the_same_claim_and_seed` khẳng định cùng claim@seed trên `fixed` PASS cả hai grader. **Đã chạy: fail đúng trên variant lỗi, pass trên `fixed`.** Ở mức eval set, item `E-014` mang `failure_modes` [FM-04, FM-05, FM-08]; gate chặn `seeded_regression` ở `refund_amount_correct` (Δ −0.129) và `reply_amount_matches_ledger` (Δ −0.214). |
| Chưa chắc chắn | Trace chỉ cho thấy agent trừ trước. Nó không cho biết *vì sao* (mô tả tool `issue_refund` mơ hồ, hay prompt dặn "trừ phần đã hoàn"); với MockLLM thì đây là công tắc gài lỗi. Nhãn layer tool/schema là suy luận từ cơ chế (host đã trừ, agent không biết), cần kiểm lại trên LLM thật. Ngoài ra chỉ C-013 và C-014 có lịch sử hoàn tiền, nên FM-05 mới được kiểm trên 2 item. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
