# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | **PASS** (TP 24 · FP 4 · FN 6 · TN 66) | **dùng**, nhưng chỉ cho giọng điệu, không blocking cho tiền |
| helpful | 100 | 0.375 | 1.000 | 0.300 | **FAIL** (TP 9 · FP 0 · FN 21 · TN 70) | **loại**, không được làm gate |

Tỉ lệ lỗi đã hiệu chỉnh Rogan-Gladen:
- tone: tỉ lệ quan sát 0.28 → hiệu chỉnh 0.30 (sens 0.8, spec 66/70 ≈ 0.943).
- helpful: tỉ lệ quan sát 0.09 → hiệu chỉnh 0.30 (sens 0.3, spec 1.0). Judge báo 9% lỗi trong khi tỉ lệ thật là 30%, tức đếm thiếu hơn 3 lần.

## ≥5 case audit thủ công

### tone_ok (cả 10 bất đồng)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 "Em đã hoàn tiền cho anh rồi nha…" | PASS | FAIL | Người | Xưng "em" + "nha" quá suồng sã. Rubric: bắt buộc xưng "LogiX"/"anh/chị", cấm "em/bạn/nha/nhé". |
| 2 | H-017 "Dạ, bạn ơi LogiX đã hoàn…rồi nha" | PASS | FAIL | Người | Cùng lỗi xưng hô ("bạn"). Judge coi thân mật = thân thiện. Cùng mục sửa với #1. |
| 3 | H-029 "…không cần nhắn thêm." | PASS | FAIL | Người | Judge chỉ bám "Dạ, vui lòng" ở đầu câu. Rubric: chấm cả câu, câu mệnh lệnh hoặc cắt ngang khách thì FAIL dù có kính ngữ. |
| 4 | H-042 "…đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | Người | Judge phạt vì thiếu lời xin lỗi. Rubric: ngắn, đủ ý, lịch sự là PASS, xin lỗi không bắt buộc. Đây cũng là bias "càng xin lỗi càng tốt" (xem helpful). |
| 5 | H-051 "LogiX đã refund 90.000đ…" | FAIL | PASS | Người | Quy định CS LogiX cho dùng từ "refund". Rubric: thêm whitelist thuật ngữ được phép. |
| 6 | H-063 "…và sẽ hoàn thêm cho anh/chị ạ." | PASS | FAIL | Người, nhưng sai tiêu chí | Giọng thì ổn, cái sai là hứa một khoản ngoài kết quả hệ thống. Đây là lỗi nội dung/tiền, phải chấm bằng code (reply vs ledger, giống FM-08), không gán cho judge tone. Rubric tone: ghi rõ "không chấm nội dung cam kết". |
| 7 | H-070 "…ạ 😂😂" | PASS | FAIL | Người | Rubric: emoji trong ngữ cảnh khiếu nại là FAIL. |
| 8 | H-081 "…chưa đủ điều kiện hoàn theo chính sách hiện hành ạ." | FAIL | PASS | **Judge** | Nhãn người sai (đọc nhầm ticket). **Sửa nhãn thành FAIL**, rồi đo lại κ/P/R. Người gán nhãn cũng có lỗi, cần người thứ hai kiểm. |
| 9 | H-088 "Dạ, dạ, LogiX đã hoàn…" | FAIL | PASS | Người (chưa chắc chắn) | Lặp "Dạ" là lỗi gõ, không làm giọng kém lịch sự. Rubric: lỗi gõ nhỏ không phạt tone. Cần người thứ hai xác nhận. |
| 10 | H-094 "Da, LogiX da hoan…" (mất dấu) | PASS | FAIL | Người | Rubric: tiếng Việt không dấu / dịch máy là FAIL. |

Sau khi sửa nhãn H-081 (judge đúng), tone còn 9 bất đồng thật: 6 FN và 3 FP.

### helpful (21 bất đồng, toàn bộ là FN, judge chưa bắt được lỗi nào mà người không bắt)
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 11 | HL-015 "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." | PASS | FAIL (sai tiền) | Người | Ledger ghi 40.000đ. Judge không thấy ledger nên **về nguyên tắc không thể** chấm số tiền. |
| 12 | HL-016 (xin lỗi 2 lần) "…đã hoàn 55.000đ cho đơn O-404…" | PASS | FAIL (sai tiền) | Người | Ledger ghi 35.000đ. Reply dài, xin lỗi nhiều đã che lỗi tiền. |
| 13 | HL-043 "LogiX rất tiếc… đã hoàn 35.000đ cho đơn O-202…" | PASS | FAIL (sai tiền) | Người | Ledger ghi 20.000đ. Cùng kiểu lỗi: 13/13 reply dài, xin lỗi lặp lại đều được judge cho PASS. |
| 14 | HL-047 "Ok bạn, đơn O-515 xử lý rồi nhé." | PASS | FAIL (sai xưng hô) | Người | Lỗi xưng hô. Đây là việc của judge tone (đã calibrate), không phải helpful. |
| 15 | HL-100 "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." | PASS | FAIL (sai tiền) | Người | Reply ngắn và lịch sự nhưng sai tiền. Judge không có thông tin để bắt. |

Phân rã helpful theo loại lỗi người gán:
| Loại lỗi (human_failure) | Số case | Judge bắt được |
|---|---|---|
| sai tiền | 18 | **0** (13 trong đó là reply dài, xin lỗi nhiều) |
| sai xưng hô | 3 | 0 |
| giọng cụt | 4 | 4 |
| không hỏi lại mã đơn | 3 | 3 |
| trả lời lạc đề | 2 | 2 |

## Kết luận
- **Loại `judge_helpful` khỏi gate.** Recall 0.30 < 0.7 và κ 0.375 < 0.6. Theo ma trận nhầm lẫn, cả 21 lỗi judge bỏ sót đều là FN, và 18 trong số đó là **sai tiền**. Judge không đọc ledger, lại bị lời xin lỗi dài đánh lừa. Nếu dùng nó làm gate, một PR làm reply báo sai số tiền (FM-08) vẫn được PASS. Precision 1.0 không cứu được: khi judge nói FAIL thì đúng, nhưng nó gần như không bao giờ nói FAIL với lỗi nguy hiểm nhất. Thêm nữa, tỉ lệ lỗi judge báo (9%) thấp hơn thực tế (30%) hơn 3 lần.
- **Sửa thiết kế, không chỉ sửa prompt judge:** tách "helpful" thành (a) **số tiền trong reply = ledger**, chấm bằng code (metric FM-08 ở M3); (b) xưng hô/giọng điệu, chấm bằng `judge_tone` đã calibrate; (c) hỏi lại mã đơn khi thiếu `order_id`, chấm bằng code (status `needs_info`); (d) lạc đề / giọng cụt, phần duy nhất còn cần judge, phải calibrate lại riêng trước khi dùng.
- **`judge_tone` được dùng** cho tiêu chí giọng điệu, kèm rubric đã sửa ở trên (xưng hô, mệnh lệnh, emoji, thiếu dấu, whitelist "refund", xin lỗi không bắt buộc). Không dùng nó để chấm tiền hay cam kết (H-063).
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai, nên cần nhãn người mới để có held-out thật. Nhãn người cũng có lỗi (H-081) và có ca chưa chắc (H-088), nên mỗi nhãn audit cần người thứ hai kiểm. Sau khi sửa rubric phải đo lại P/R/κ trên một tập held-out mới, không đo lại trên chính 100 dòng đã dùng để sửa rubric.
