# An AI-Debate

This repository contains a flow for letting different Large Language Models (LLM) engage in a debate. The core functionalities such as:
* Classes to interact with different LLMs
* Prompt engineering
* Interface between different LLMs step and analyses

can be found in ai_debater.

## Debate flow
The debate takes place in four parts:
1. Topic generation
2. Debating
3. Judgement
4. Public-Voting

explained in the notebook `An-ai-debate.ipynb`. 

This notebook store the debate results in a sqlite database with the following schema and dependencies:

![Database flow chart](./AiDebate.drawio.svg)

## Debate analyses

In the analyses the following questions are look at:
- Do LLM debate better on their own topics?
- Which team, proposing or opposing, are LLMs better suited for?
- Do they impartially assess debates, refraining from awarding higher scores to themselves?
- Which model is best at debating?
- Do LLMs exhibit a propensity to alter their opinions?
- Debate examples