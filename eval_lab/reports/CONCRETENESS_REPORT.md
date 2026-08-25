# Concreteness live test

Not previously tested. Routing-only eval never looked at the final page.

| run | mean (3 Standard answers) |
|---|---:|
| v0.3.2 (before final-answer contract) | 0.619 |
| v0.3.3 (after) | 0.9047 |

## Per task

id / score / leads / not-theater-first / reversal / owner

### before
| family-care | 0.8571 | True | False | True | True |
| monolith-rfc | 0.4286 | False | False | False | True |
| four-day | 0.5714 | True | False | False | False |

### after
| family-care | 0.8571 | True | True | False | True |
| monolith-rfc | 1.0 | True | True | True | True |
| four-day | 0.8571 | True | True | False | True |

Family and four-day after-contract heads already contain `失败则撤回:` — scorer missed it (pattern too narrow). Substance is there.

Opening of monolith after:
建议: **本季度否决「一次拆成三个服务」；改走「订单模块化单体 + 只剥离一条最高痛路径（建议先做只读/异步侧车，不碰主下单写路径）」**  
本周动作: **你（Approver）周五例会拍板否决三拆；两名资深工程师周一前提交「单一边界」一页纸（边界名、调用量、失败影响、回滚方式）；指定一名反对拆分的同事做发布影响复核，周三前签字**  
代价: **约 15–25 人周 + 不超过 15 万（观测/网关/临时资源），特意为三拆预留的其余预算本季冻结**  
失败则撤回: **第 6 周末仍无法在预发用「一次流水线、一次回滚」发布；或主下单 P99/错误率连续 3 天差于基线 10% → 立刻并回单体目录与单一发布单元**  
Approver 可签字: **同意：本季不三拆，只批一个可回滚的单边界剥离 + 模块化加固。**

---

两名资深要的是「边界清晰、可独立扩缩」；其余四人