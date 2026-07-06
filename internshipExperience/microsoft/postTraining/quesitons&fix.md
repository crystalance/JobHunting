#Q&F


---
## 7/5/2026
1. situation: successfully deployed qwen2.5-7B-Instruct
2. The one real bug to fix: the agent stops the moment an assistant turn has no parsed tool_call. Qwen2.5-7B sometimes emits a <tool_call> block inside message content with slightly malformed JSON; vLLM's parser drops it → the loop ends after 2 turns with no CSV. This is a P0 harness-robustness item (open models need a fallback that recovers content-embedded tool calls), independent of model quality.
    1. i want to see the workflow or the protocal detail on how llm generate the tool_call, and how vLLM parse it, and what passed to our agent? 
    2. how to cope with this malformed json problem, do we need to do SFT(RFT) now? or we should change to qwen3-8B?
        1. Harness fragility (engineering): SearchAgent treats "no parsed tool_calls" as "the model is done" and terminates. That's an unconditional assumption that's simply wrong for open models.
        2. Model format reliability (model quality): Qwen2.5-7B occasionally emits a malformed <tool_call> (stray "}}).
        3. fix: see WebSearchResearch/post_training/design/tool_call_robustness_fix.md
3. for RL,(GRPO) what infomation do we need for training(like reward)
4. why do we need Observability — format_recovered / json_repaired / malformed_unrecoverable flags feeding the P1 metric and RL format_ok reward?
5. so the base model: cant output the right tool call format, 2. little context window(32678) that wont be enough, how do mainsteam in academic/industry to cope with this 
6. how to design the reward function, what rubric should we consider?
7. what's the boardline of improving the prompts vs fine-tuning?