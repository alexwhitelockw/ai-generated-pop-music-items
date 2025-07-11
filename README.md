# Popheads Quiz Generator: LLM-Powered Question Creation

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![LLM](https://img.shields.io/badge/LLM-DeepSeekChat-green.svg)

Transform top posts from r/popheads into engaging quiz questions using advanced LLM workflows. This project demonstrates how to leverage language models for automated content generation with contextual awareness.

## Workflow Overview
```mermaid
graph LR
A[Reddit Posts] --> B(Base Question Generation)
B --> C[Recall Questions]
B --> D[Interpretative Questions]
B --> E[Contextual Questions]
C --> F[Meta-Review]
D --> F
E --> F
F --> G[Final Question Selection]
G --> H[Output Quiz]
