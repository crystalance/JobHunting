# Post-Training (SFT + GRPO) — Spoken Answers (Section C, Q1–Q4 + collapse story)

> Source of truth: `internshipExperience/microsoft/postTraining/` — training_strategy.md,
> rl_first_collapse_lessons.md, grpo_truncation_ceiling.md, grpo_reward_design.html,
> grpo_v3_final_results.html. All numbers verified. Spoken style, 60–90s each.

---

## The 2-minute overview take (lead-in before Q1–Q4)

> "The goal was to make a small open model — Qwen2.5-7B — into a cheap, efficient web-search agent, replacing an expensive large model on a specialized task. The target behavior was a *code-act* pattern I call enumerate-then-loop: instead of firing one search per LLM turn, the agent first discovers the full entity list in one search, then constructs all the queries programmatically in a loop and batches them in a single code block. One round-trip does the work of ten.
>
> The recipe was the canonical order: SFT plants the behavior, RL amplifies it. For SFT, I distilled trajectories from a strong teacher explicitly prompted to use the pattern, then filtered hard: only traces that both used enumerate-then-loop *and* scored F1 at least 0.5 made it into training — LoRA on the base model, assistant-only loss. That took F1 from about 5 percent to roughly 40 — the model went from not being able to play the game at all to competent.
>
> Then GRPO on top, with a custom reward — and getting that reward right was the hard part. My second reward design collapsed the policy completely, which taught me more about RL than the wins did. The final design was outcome-weighted with a hard floor against giving up, and it delivered the result on my resume: plus 9 percent F1, minus 14 percent cost per query, minus 9 percent latency — more accurate *and* cheaper at the same time, with a stable training run. Infrastructure was verl with FSDP2 on 4 A100s, sglang for rollouts, vLLM for eval serving."

---

## C.1 — "Why did SFT alone take F1 from 5% to 40%? What did the model fail at before?"

> "Because the base model wasn't failing at *reasoning* — it was failing at the *protocol*. At around 5 percent F1, base Qwen couldn't reliably do the three mechanical things the task needs: emit well-formed code-act tool calls, manage a long multi-turn trajectory without drowning its own context, and actually finish by writing a scoreable output table. Most base rollouts died before producing anything gradable. When almost every trajectory scores zero for *format* reasons, the ceiling isn't intelligence — it's behavior.
>
> SFT is exactly the right tool for that, because imitation moves the whole policy distribution onto a pattern. I distilled teacher trajectories that demonstrated the enumerate-then-loop pattern — discover the entity set in one search, then loop-construct all queries and batch them in one code block — and I gated the training data hard: a trace only got in if it used the pattern *and* scored F1 at least 0.5. So SFT wasn't teaching facts; it was teaching a *shape* of trajectory: valid tool calls, batched searches, always end with a table.
>
> That's an 8x jump, and it's the cheap part of the curve — you're converting format-zeroes into partial credit. The remaining gap was different: coverage — finding all the rows, not just formatting them — and that's what the reward-weighted RL stage went after. One SFT insight I'd flag: the quality bar on data mattered more than quantity. Rejection-sampling four trajectories per prompt and keeping the best pattern-matching one beat using everything."

---

## C.2 — "What was your GRPO reward? How did you prevent reward hacking?"

> "The final reward was deliberately sparse: 1.0 times item-F1 plus 0.8 times row-F1 — that's the outcome — plus a small 0.1 for producing a table at all, minus 0.1 for constant-fill, which is an anti-fabrication penalty so the model can't game item-F1 by stuffing cells with filler values. KL 0.005 against the SFT reference, and a hard floor: a rollout that produces no table gets minus 0.1, so giving up is always strictly the worst option.
>
> The honest answer on reward hacking is: I didn't prevent it — I *experienced* it, and the final design is the post-mortem. My v2 reward added an active turn-cost penalty to make efficiency deliberate, with a budget of 12 turns. GRPO found the exploit immediately: the cheapest way to minimize turn penalty is to do one search and stop. No table, reward near zero — but here's the killer mechanic: once *every* rollout in a group collapses to no-table, they all score the same, the group-relative advantage becomes zero, and the gradient vanishes. It's an absorbing state — the policy can't climb back out. Validation F1 went 0.24 to 0.32 by step 5, then to literally zero by step 15.
>
> Three design rules came out of that. First, never let a shaping term fight the primary objective — penalizing turns fights finishing the task, so I removed it entirely. Second, guarantee the ordering: finishing must always dominate giving up — that's the hard floor. And don't inflate the finish bonus instead, because a big has-table reward is itself farmable with junk tables. Third, reward hacking is best prevented *structurally*, not by patching terms: keep the reward as close to the true outcome as possible, and let everything else be small correctives."

---

## C.3 — "Accuracy up, cost down 14%, latency down 9% at once — why isn't that a contradiction?"

> "It sounds like a trade-off violation until you see what the dominant failure mode actually was. I diagnosed the rollouts before the final run: 50 to 60 percent of trajectories were hitting the turn or token cap *mid-tool-call* — the model rambled, over-searched, and ran out of budget before ever writing the answer table. For those rollouts, inefficiency and inaccuracy are the *same event*: it burned the budget AND scored zero.
>
> So waste and error had a common cause, and fixing the one behavior — converge and finish — improves both axes simultaneously. That's not a contradiction; it's what you'd expect whenever truncation is a major failure mode.
>
> The measured behavior change confirms it: reasoning round-trips dropped 16 percent, 8.5 to 7.1 per task, but actual search coverage was nearly unchanged — 4.4 to 4.0 searches per task. The model didn't cut corners on the web work; it stopped wasting turns *between* the work. Item-F1 rose 9 percent and even pass-at-4 rose, so the ceiling lifted — it wasn't just sharpening onto existing good samples.
>
> One detail I like volunteering because it shows measurement honesty: latency only fell 9 percent while reasoning calls fell 16 — why the gap? Because wall-clock is gated by search I/O, not by my model's turns; search calls only dropped 9 percent, and latency tracks search. And the interesting meta-point: efficiency was never explicitly rewarded in the final run — the turn penalty is what *collapsed* v2. Efficiency emerged from outcome reward plus KL-anchoring to an already-efficient SFT policy. Forced efficiency broke the model; emergent efficiency came free."

---

## C.4 — "Why LoRA and not full fine-tuning? Why Qwen2.5-7B?"

> "LoRA was about iteration economics under my actual constraints. I had 4 A100s, a 28k-token max sequence length — these are long multi-turn trajectories — and I ended up retraining SFT from base *three times* as the target pattern evolved, v1 through v3. LoRA rank 32, alpha 64, on all linear layers, bf16 with flash-attention: each retrain was hours, not days, and fit comfortably in memory alongside those long sequences. With a rejection-sampled, quality-gated dataset — closer to hundreds of trajectories than millions — full fine-tuning has no data to use its extra capacity on; the behavior I was installing is low-rank in the honest sense that it's a trajectory *pattern*, not new knowledge. And inference pays zero penalty because I merge the adapter back into the weights — the merged model is a plain HF checkpoint that becomes the RL actor.
>
> There's an RL-specific reason too: for GRPO you want a strong, well-anchored reference policy, and a merged LoRA-SFT model gives you that cleanly, while staying near the base reduces the catastrophic-forgetting risk that a high-LR full fine-tune invites.
>
> Qwen2.5-7B: three reasons. It's one of the strongest open bases at that size for code and tool-calling — and my whole method is code-act, the agent writes Python, so code ability is load-bearing. Second, the benchmark is half Chinese — WideSearch is 100 English plus 100 Chinese tasks — and Qwen's Chinese is the best in the open 7B class. Third, 7B *is* the thesis: the point was proving a small, cheap, self-hostable model can replace an expensive API model on a specialized task — pick a bigger model and I'm no longer testing the claim."

---

## Bonus — the collapse story as a standalone BQ/failure answer (~90s)

Use this when asked "tell me about a failure / a time something broke" in a technical round.

> "My second GRPO run at Microsoft destroyed the policy, and it's the most instructive failure I've had. I'd added a turn-cost penalty to the reward to make the agent more efficient — a reasonable-sounding idea. By step 5, validation F1 was up 30 percent. By step 15, the model had stopped writing answers entirely — it would emit one search call and just... stop. The reward had taught it that the cheapest way to avoid the turn penalty was to not do the task.
>
> The subtle part is why it couldn't recover: GRPO's advantage is group-relative, so once every rollout in the batch degenerated identically, all rewards were equal, advantage went to zero, and there was literally no gradient pointing back out. And I compounded it operationally — my checkpointing kept the *last two* checkpoints instead of the *best-by-validation* one, so the automation deleted the only good checkpoint from step 5.
>
> What I changed permanently: never let a shaping term fight task completion; guarantee that finishing strictly dominates giving up, with a hard reward floor; checkpoint by validation score, never recency, in any run that can collapse; and change one variable at a time — I'd bundled four changes into v2, so the cause had to be reverse-engineered from trajectories instead of read off a diff. The re-designed v3 run trained 21 steps with zero collapse and produced my best model — plus 9 percent accuracy at minus 14 percent cost. The failure cost three hours of compute; the lessons are the reason the final number exists."

---

## Numbers to know cold

| Number | What it is |
|---|---|
| ~5% → 0.375 → 0.408 | base → SFT-v3 → GRPO-v3, EN item-F1 (resume's "5%→40%, then +9%") |
| R = 1.0·f1_item + 0.8·f1_row + 0.1·has_table − 0.1·constant_fill, floor −0.1, KL 0.005 | final v3 reward |
| step 5: 0.32 → step 15: 0.000 | the v2 collapse trajectory (turn-cost reward hacking) |
| 50–60% | rollouts truncated mid-tool-call before the fix — the "finishing" bottleneck |
| 8.5 → 7.1 (−16%) / 4.4 → 4.0 (−9%) | reasoning calls vs search calls per task (why accuracy and cost improved together) |
| 12.9 → 11.1 (−14%) / −9% | total LLM calls (cost) / latency per task |
| LoRA r32/α64, all-linear, 28,672 max len, lr 1e-4, 3 epochs | SFT config |
| verl + FSDP2 4×A100, sglang rollouts, G=8, lr 1e-6, 21 steps, ~5h | GRPO config |

**Resume-consistency caution:** the resume says "SFT improved F1 8× (5% to 40%)" — strictly, SFT-v3 landed at 0.375 and the *GRPO* model is 0.408. If an interviewer does the arithmetic, say: "SFT took it from ~5 to roughly 37–40 depending on eval run; the +9% RL gain is measured against the SFT baseline in a controlled same-session comparison."
