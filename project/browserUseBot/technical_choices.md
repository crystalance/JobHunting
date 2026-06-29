# Technical choices

1. CDP screen shot vs noVPC for remote delegate choice

2. host choice
    1. AWS? alibaba cloud?
    2. --> AWS, best connectivity for other services/

3. since it is a long-running agent, how to manage its context? --> memory --> we can look up to claude code's solution
4. we need skill to help agents quickly learn how to do sth 
Two things to improve:

Profile not persisting: it's using a temp dir, so you'll re-login every task. I'll fix the user_data_dir wiring.
Step visibility: optionally push step updates to Telegram so it doesn't feel frozen.