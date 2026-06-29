# BQ for MS

## resume bullet point





## BQ questions
### HDMAS

#### problems&fix
1. when multiple agents doing one thing, file conflict is common: 
    1. my solution is using a lock // lock BB for reading and writing, lock other files
    2. the common solution is using git worktree --> how?
    3. 

2. when you are having a loop engineering or multiple agents doing a loop, using a independent review agent to check is improtant
    1. 




### BenchmarkBuildingPipeline
1. verification rate is low--> how to enhance it while remain trustworthy?
2. how to enhance GT agents ability, incase the benchmark is too simple?
3. one case time is extremely long(8h, fixed)
4. how to better extract answer from logs/ from all the files
5. **[important]** any experience cosoliated for agent-generate benchmark pipeline?
    1. constructing time is extremely hight for some cases, for one session tackles one fact sequentially
        1. add parallel 
        2. give a whole session to process a whole column;
        3. --> to see if it actually works.
    2. so benchmark-building originally is a tedious, human labor-intensive, higly repetitive process， using agent to generate case is suitable.
        1. of course the cases agents generate are not perfect. we need to design a pipeline to address this. Pratically we use verifier agent to verify each value, to make it more trust-worthy.
            1. how does it trust-worthy. you know, the cases are faked.
                1. "The verifier is reliable to the degree that the evidence is reproducible and the compare is deterministic. The agent's only irreplaceable job is locating + extracting the value from messy HTML; the compare (numeric tolerance, host-suffix match, parser-replay) should be code, not the model. Trust comes from shrinking the agent's role to the smallest checkable step and making it say 'I couldn't' on the rest."
        2. we use GT-Agent to find the answer. but the difficulty of the benchmark is high constricted by the ability of the GT agents. for one case we use better framework and better llms, but if we want to test the ability of it self. what did we do to differentiate the environment of building agent and agents being tested?
            1. So "GT fills 100%" means the answer is findable with unbounded effort + given decomposition + independent verification — which is exactly the definition of a well-posed question (it has a knowable, verifiable truth). It is not a statement that the task is easy for an agent under test. The GT pipeline is operating in the easy direction of the generation/verification asymmetry; the tested agent is in the hard direction. Same model, different difficulty.
            2. This is the sharpest objection anyone will raise, and it's worth answering precisely because it actually bundles **three different objections**. Separating them is most of the defense.

## First, disentangle what's being claimed

1. **Ceiling / selection bias** — "the benchmark only contains questions GT could answer, so difficulty is capped at GT's ability."
2. **Circularity** — "if you later test an agent with the same model/framework GT used, you're grading it against itself."
3. **Construct validity** — "does 'GT found it' even mean 'this is valid ground truth'?"

Your "fill rate ≈ 100%" speaks to none of these directly — I'll come back to why it's actually a *yellow* flag, not just reassurance.

## The core rebuttal: building ≠ solving (same model, different task)

The reviewer's hidden assumption is that GT-Agent and the tested agent do *the same task*, so sharing a model means sharing difficulty. They don't. Even with the **identical LLM**, the GT-Agent operates in a structurally **easier regime**:

| Axis | GT-Agent (builder) | Agent under test |
|---|---|---|
| Budget | unbounded — 30–50 min/instance, multi-round, retries, 2h cap | bounded eval budget, one-shot |
| Scope | **one atomic fact at a time**, identity key handed to it | the **whole composite task**, must self-decompose + enumerate + integrate + write back |
| Context | spec gives it entity/period/unit + surrounding rows | must infer all of that from the raw query |
| Curation | independent verifier + repair + human adjudication of the residual | none — its raw output is scored |

So **"GT fills 100%" means the answer is *findable with unbounded effort + given decomposition + independent verification*** — which is exactly the definition of a *well-posed* question (it has a knowable, verifiable truth). It is **not** a statement that the task is easy for an agent under test. The GT pipeline is operating in the *easy direction* of the generation/verification asymmetry; the tested agent is in the *hard direction*. Same model, different difficulty.

## Reframe what the ceiling actually caps

GT ability bounds **answerability**, not **difficulty**. And answerability is a ceiling **every** benchmark has — human annotators impose the identical limit (humans only label what humans can find). The GT-Agent is just a *scalable replacement for the human annotator*. "Difficulty is bounded by GT" is exactly as true as "difficulty is bounded by the human labeler" — and we accept human-labeled benchmarks every day. So the objection, stated fairly, reduces to: *"is your oracle's frontier at or above the answerability frontier you care about?"* — a measurable question, not a fatal flaw.

**The clean one-line justification for a reviewer:** *the GT-Agent is an annotation tool, not a baseline.* Its only job is to establish that a verifiable answer exists and what it is. Treating it as a competitor in the eval is a category error.

## The risks that are real and need handling (don't hand-wave these)

- **Shared-blind-spot contamination (the true circularity).** If GT and verifier share a model, they share priors → the verifier can collude with a wrong value. **Fix:** different model for the verifier than for GT, plus deterministic compare. (You partly do this already.)
- **Selection bias toward "easy-to-ground" facts.** Here's why **fill rate ≈ 100% is a yellow flag**: it could mean GT is strong, *or* it could mean Query2Facts' X-rules only ever propose facts that are easy to ground (it prunes the hard ones upstream). Those look identical in the fill metric. **Fix:** audit whether your null/`UNRESOLVED` set correlates with a *type* of question you're systematically excluding.
- **Difficulty defined circularly.** If "hard" = "GT struggled," difficulty is contaminated. **Fix:** tag difficulty by *intrinsic* properties — hop count, source obscurity, freshness, enumeration size — independent of whether GT found it.

## The single most convincing fix: measure the build-vs-solve gap

Turn the objection into a number. Run **the same GT model as a tested agent under eval constraints** — one-shot, time-boxed, given only the raw query (no identity keys, no spec decomposition, no verifier) — and show it scores far below 100% on the gold *it helped build*. If GT-as-builder fills 100% but GT-as-tested-agent scores, say, ~55%, you have **empirically demonstrated** that building ≠ solving and quantified the headroom. That one experiment converts "isn't this circular?" into "here's the 45-point gap proving it isn't."

Complementary hardening:
- **Heterogeneous / ensemble oracle** (multi-model vote) so the builder frontier sits *above* any single tested model → kills "you tested model X with an oracle built by model X."
- **Human-labeled seed** on a sample → shows the gold isn't just "what the model believes."

## Bottom line

You don't need to weaken the claim — you need to **stop letting GT be mistaken for a baseline.** It's the annotator. The defense is: (1) building operates in the easy direction with unbounded budget + given decomposition + independent verification, while solving is bounded/composite/one-shot; (2) the answerability ceiling is intrinsic to *all* benchmarks, GT just scales the annotator; (3) prove it with the build-vs-solve gap experiment and a non-shared verifier.

I can wire up that gap experiment in your repo right now — run the GT model through the eval harness as a *contestant* (raw query in, one-shot, scored against `fact_spec_gold`) across the completed cases, and drop the gap number into the report. That's the strongest possible answer to the challenge. Want me to set it up?
    


6. current openning problems
    1. for teir B problems, what's the best way to tackle them? 
        1. currently GT would generate a playbook, for the refresh Agents as a reference.
        2. the tier B is all the data that you dont got a fixed source for refresh data, for example, you cant know in advance and just pass today's date to a api and got the latest data.
        3. --> assess the recall rate/ using a ablation experiment to see if the playbook really works.
        4. 

7. histroy bugs and fixtions
#### problems encountered
1. for case 2 fact, when extracting instance, the instance is always a mess...
2. 


---

for bq questions and answers, can search for the examples online


---
learn: https://eugeneyan.com/writing/working-with-ai/

1. the fix to help with long-running tasks
   1. for long-running tasks, verfication is crucial for autonomy, and we can have a agent with fresh context to monitor