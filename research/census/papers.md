# Friend paper list

Index for the 41 papers in `research/papers/registry.json`. Observed 2026-09-11 from arXiv Atom.
Full-text extracts live at `research/papers/arxiv/<id>.md` (symlink to the arXiv MCP cache). BibTeX is `research/papers/refs.bib`.
Bands are a judgment on companion-memory fit, not paper quality.

Core cards are in Slice G markdown.

- `research/census/papers-retrieval.md`
- `research/census/papers-lifecycle.md`
- `research/census/papers-persona.md`
- `research/census/papers-architectures.md`

Nature DOI 10.1038/s41586-026-10319-8 is arXiv 2507.14805.

## Core. Census cards

| arxiv | title | card | steal or why |
| --- | --- | --- | --- |
| 2405.14831 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models | hipporag | Hippocampal indexing plus Personalized PageRank for multi-hop recall. Still retrieve-then-generate. |
| 2501.00663 | Titans: Learning to Memorize at Test Time | titans | Test-time neural memory as a module, not a prompt cache. Weight-space write is a different cost shape. |
| 2502.12110 | A-MEM: Agentic Memory for LLM Agents | a-mem | Zettelkasten notes that link and evolve on write. Still agent RAG on LoCoMo-class benches. |
| 2504.07992 | 'Neural howlround' in large language models: a self-reinforcing bias phenomenon, and a dynamic attenuation solution | neural-howlround | Identity lock-in as a self-reinforcing loop. Attenuation as a forgetting/read-policy cousin. |
| 2504.13173 | It's All Connected: A Journey Through Test-Time Memorization, Attentional Bias, Retention, and Online Optimization | miras | Forget gates as retention regularization. Architecture-level forgetting, not a user forget-that command. |
| 2506.15841 | MEM1: Learning to Synergize Memory and Reasoning for Efficient Long-Horizon Agents | mem1 | Constant-size internal state that discards. Cost bound as a first-class objective. |
| 2507.14805 | Subliminal Learning: Language models transmit behavioral traits via hidden signals in data | subliminal-learning | Persona can transmit through semantically unrelated distillation data. Filtering chat text is not enough. |
| 2507.21509 | Persona Vectors: Monitoring and Controlling Character Traits in Language Models | persona-vectors | Activation-space persona directions for monitor and steer. Complements, does not replace, a typed store. |
| 2510.11328 | Do LLMs "Feel"? Emotion Circuits Discovery and Control | emotion-circuits | Emotion as a controllable circuit, not a retrieved mood adjective. Silence may need this layer. |
| 2511.16997 | MirrorMind: Empowering OmniScientist with the Expert Perspectives and Collective Knowledge of Human Scientists | mirrormind | Split episodic, semantic, and persona memories per individual. Still a scientist-agent architecture. |
| 2512.18202 | Sophia: A Persistent Agent Framework of Artificial Life | sophia | Narrative identity as a persistent meta-layer over any LLM stack. Still retrieve/reflect into the prompt. |
| 2512.24695 | Nested Learning: The Illusion of Deep Learning Architectures | nested-learning | Continuum memory with multiple timescales. Hope is an architecture, not a companion log. |
| 2601.09113 | The AI Hippocampus: How Far are We From Human Memory? | ai-hippocampus | Use the survey taxonomy (implicit, explicit, agentic) as a map. Do not treat it as a winner. |
| 2601.10387 | The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models | assistant-axis | Anchor the default persona in activation space. Companion identity drift is measurable without retrieval. |
| 2607.18975 | Mi-Memory: A Lifecycle Memory Framework for Personal AI | mi-memory | Lifecycle roles plus typed evidence, gates, and rollback. Closest recent Personal-AI framing. |
| 2609.03201 | MemoryLACE: Memory Lifecycle-Aware Consolidation and Evidence Retrieval | memorylace | Sparse merge, supersession, and contradiction on atomic notes with provenance. Steal this relation set. |
| 2310.08560 | MemGPT: Towards LLMs as Operating Systems | memgpt | Historical OS-tier memory. Do not implement. Current Letta is MemFS. Card exists so the list is honest. |

## Adjacent. Steal one idea. No card

| arxiv | title | card | steal or why |
| --- | --- | --- | --- |
| 2305.00813 | Neurosymbolic AI -- Why, What, and How |  | Keep symbolic kinds as types, not slogans. Do not wait for a neurosymbolic LLM to invent companion ontology. |
| 2404.08295 | Study of Emotion Concept Formation by Integrating Vision, Physiology, and Word Information using Multilayered Multimodal Latent Dirichlet Allocation |  | Emotion as a constructed category from multimodal evidence, not a retrieved adjective. |
| 2405.07987 | The Platonic Representation Hypothesis |  | Do not assume a private companion embedding space. Representations may already be converging across models. |
| 2507.00081 | State and Memory is All You Need for Robust and Reliable AI Agents |  | Finite-state memory for tool workflows. Do not cargo-cult the title into companion LTM. |
| 2508.05619 | The Missing Reward: Active Inference in the Era of Experience |  | Read policy as expected-free-energy, not top-k similarity. When to speak is a decision, not a score. |
| 2510.26493 | Context Engineering 2.0: The Context of Context Engineering |  | Treat context as a designed object with history. Do not rename RAG as context engineering and stop. |
| 2512.01797 | H-Neurons: On the Existence, Impact, and Origin of Hallucination-Associated Neurons in LLMs |  | Sparse hallucination neurons. A poisoning eval could probe these, not rely on prompt filters. |
| 2512.21110 | Beyond Context: Large Language Models' Failure to Grasp Users' Intent |  | Write policy must score user intent, not surface wording. Jokes and jailbreaks share this failure. |
| 2601.05280 | On Solomonoff Induction in Large Language Models and the Limits of Self-Improving: The Singularity Is Not Near Without Symbolic Model Synthesis |  | Do not claim AGI by stacking RAG. Typed symbolic synthesis is the later protocol's job, not next-token fit. |
| 2601.19062 | Who's in Charge? Disempowerment Patterns in Real-World LLM Usage |  | A companion that always validates can score high and still disempower. Silence includes not playing along. |
| 2601.19897 | Self-Distillation Enables Continual Learning |  | On-policy self-distillation as a continual-learning write path. Not a user forget-that. |
| 2601.19942 | Latent Object Permanence: Topological Phase Transitions, Free-Energy Principles, and Renormalization Group Flows in Deep Transformer Manifolds |  | Object permanence as a representation-space phase, not a retrieved fact. Later eval, not a store type. |

## Out of scope. Wrong domain

| arxiv | title | card | steal or why |
| --- | --- | --- | --- |
| 2502.16636 | Visual-RAG: Benchmarking Text-to-Image Retrieval Augmented Generation for Visual Knowledge Intensive Queries |  | Visual-RAG benchmarks text-to-image retrieval for visual knowledge QA. |
| 2503.05398 | Learning High-Fidelity Robot Self-Model with Articulated 3D Gaussian Splatting |  | Articulated 3D Gaussian self-model for robot kinematics and texture. |
| 2506.21734 | Hierarchical Reasoning Model |  | Hierarchical Reasoning Model for Sudoku, maze, ARC. No episodic store. |
| 2507.02097 | The Future is Agentic: Definitions, Perspectives, and Open Challenges of Multi-Agent Recommender Systems |  | Perspective paper on agentic recommender systems. |
| 2510.04871 | Less is More: Recursive Reasoning with Tiny Networks |  | TRM recursive reasoning with 7M params on ARC. Not memory. |
| 2512.02472 | Guided Self-Evolving LLMs with Minimal Human Supervision |  | R-Few guided self-evolving LLMs with minimal human labels. |
| 2512.03750 | Universally Converging Representations of Matter Across Scientific Foundation Models |  | Converging representations of molecules, materials, proteins. |
| 2512.05356 | AI & Human Co-Improvement for Safer Co-Superintelligence |  | Weston and Foerster on human-AI co-improvement. Not a memory system. |
| 2512.10942 | VL-JEPA: Joint Embedding Predictive Architecture for Vision-language |  | VL-JEPA predicts text embeddings, not companion state. |
| 2512.24880 | mHC: Manifold-Constrained Hyper-Connections |  | mHC manifold-constrained hyper-connections. Foundation-model training stability. |
| 2601.06002 | The Molecular Structure of Thought: Mapping the Topology of Long Chain-of-Thought Reasoning |  | Molecular structure of Long CoT. Reasoning traces, not episodic companion memory. |
| 2602.13517 | Think Deep, Not Just Long: Measuring LLM Reasoning Effort via Deep-Thinking Tokens |  | Deep-thinking tokens vs long CoT. Inference effort, not memory. |

