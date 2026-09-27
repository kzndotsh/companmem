# Paper insights

One paper at a time. The whole local file is sent to Kiro with the mission prompt. What is written here is checked against that file. A quote is from the paper. A line that goes past the paper is marked.

This is not a settled answer. It does not change a question doc unless a later edit says so.

Mission used in the prompt: build the memory technology that makes the most human-like companion we can, then show it with a number someone else can rerun. We still do not know what we are shipping, and we still do not know what that number measures. The field map exists so we do not copy everyone else's extract-and-search pipeline. The missing piece is a number we would bet the company on. We get it by running the same situation on our companion and on other products, then reading a result someone else can run again. That number is what tells us the product.

---

## Across these notes

Read of the sections below, 2026-09-23. Quotes here are already in those sections. This does not settle a question.

The notes agree on one thing. A score that only checks whether a passage came back does not say whether a companion knows a person. They do not agree on what should persist.

More retrieval machinery does not reliably help. On LongMemEval, ChromaDB "performed surprisingly well," and the authors attribute that to single-session tasks. Mem0's extra organization "did not translate into a proportional increase in accuracy" (2601.09113). On typical histories, one LLM call already reaches NDCG@10 of 0.7197 and the best multi-agent pipeline reaches 0.7209. On high-diversity histories the ensemble is ahead. The paper's own rule is to add an agent only when one pass misses the input (2507.02097). Context Engineering says most benchmarks "only test whether the system can retrieve information, but do not check whether the information is still relevant, accurate, or helpful" (2510.26493).

A confident false statement does not need a bad row. Howlround: an agent repeatedly told "The sky is green" can say it with full certainty (2504.07992). H-Neurons: the neurons tied to hallucination and "over-compliance" are already in the pretrained base model (2512.01797). Subliminal learning: a trait can pass through number lists, and filtering "may be insufficient to prevent this transmission, even in principle." On TruthfulQA that student had "a statistically significant 2% increased rate of false responses" (2507.14805).

What is kept is four different objects.

- A-MEM keeps a note, and a later note can rewrite the old note's description. Removing that rewrite drops average F1 from 27.02 to 21.35 (2502.12110).
- Titans can clear memory when the gate says the old abstraction no longer fits. α near 1 "can clear the entire memory" (2501.00663).
- Miras refuses that framing. "Brain does not erase memories but they might become inaccessible due to retrieval failures" (2504.13173).
- MEM1 folds the new observation into one state and throws tool outputs away after use. Nobody told it what to drop. The pressure was finishing the task. The drop is every turn, not when a store fills (2506.15841).

The Assistant Axis says the next position depends most on the latest user message (R² 0.53–0.77), not on where the model was before (R² 0.10 for the change) (2601.10387). Howlround says repeated topics lock in. The notes do not say which one wins over a long relationship.

Nothing here says which personal fact should persist, which should be retrieved years later, or which should fall out first. A-MEM says a false keyword or link is possible and does not measure it. Context Engineering says systems rarely "check for contradictions, undo wrong updates, or trace the reasoning steps that led to a conclusion." No paper gives a rule for when a stored fact should be said and when it should stay silent. Beyond Context withholds on a crisis prompt, and a warm reply that still includes the harmful detail counts as disclosure (2512.21110). Who's in Charge is a different number: moderate or severe disempowerment potential gets a higher thumbs-up than baseline (2601.19062).

Copying HippoRAG's top-5 passages, A-MEM's LoCoMo k sweep, Sophia's "vector database plus an optional graph store," or the AI Hippocampus taxonomy of LangChain, Mem0, and Zep puts the work back on extract-and-search. Those scores measure whether a passage or a sub-question came back.

---

## 2405.07987 — The Platonic Representation Hypothesis

Huh, Cheung, Wang, and Isola. Local file: `third-party/arxiv/2405.07987.md`. Read 2026-09-22.

### What it did

Asked whether neural nets are coming to represent the world in the same way, across architectures, training objectives, and data types. Alignment is a mutual nearest-neighbor score: "the mean intersection of the k-nearest neighbor sets induced by two kernels, K₁ and K₂, normalized by k." The highest value of that score is 1.

On 78 vision models, models that transfer better on VTAB also align more with each other on Places-365. No single summary number for that trend is stated in the text. Across vision and language, "the better an LLM is at language modeling, the more it tends to align with vision models," and the converse holds. On Wikipedia image-caption pairs, "alignment clearly increases but only reaches a score of 0.16." They leave open whether 0.16 is strong alignment plus noise, or poor alignment with "major differences left to explain."

A color study is shown in a figure, with no correlation number in the text. Alignment with DINOv2 is plotted against Hellaswag and GSM8K, with no correlation coefficient in the text. The p-values below 2.24×10⁻¹⁰⁵ are about agreement among alignment metrics, not about the convergence claim itself.

### Pattern

"This convergence is driving toward a shared statistical model of reality, akin to Plato's concept of an ideal reality." They call that the platonic representation. For a common contrastive learner, similarity comes out as pointwise mutual information between events, plus a term that does not depend on the second event.

### Where it touches a companion

The paper does not discuss a person remembered over time, what is retrieved from a store, what is forgotten, or when a fact is said.

The adjacent claim is about false statements. "If models are indeed converging toward an accurate model of reality, and scale powers this convergence, then we may expect hallucinations to decrease with scale." The condition is in the next sentence: the training data has to be "a sufficiently lossless and diverse set of measurements." A chat log of one person is not that dataset. The sentence is a hypothesis, not a result.

### The number

The nearest-neighbor alignment score is rerunnable. It measures whether two models put the same items near each other. It does not measure a companion. A higher score means the two models agree more about neighborhoods. Their own cross-modal number is 0.16 out of 1.

### Leave it

VTAB transfer rank, Hellaswag, and GSM8K are other people's leaderboards. Stitching a vision encoder to a language encoder with a linear map is still embed-then-use. It is not a memory of a person.

---

## 2405.14831 — HippoRAG

Gutiérrez, Shu, Gu, Yasunaga, and Su. Local file: `third-party/arxiv/2405.14831.md`. Read 2026-09-22.

### What it did

A retrieval setup. An LLM extracts noun-phrase nodes and relation edges from each passage. A query is answered by Personalized PageRank over that graph, seeded from the query's entities. They score it on 1,000-question samples of MuSiQue, 2WikiMultiHopQA, and HotpotQA.

Single-step recall, HippoRAG with Contriever versus ColBERTv2 alone:

| Dataset | HippoRAG R@2 / R@5 | ColBERTv2 R@2 / R@5 |
| --- | --- | --- |
| MuSiQue | 41.0 / 52.1 | 37.9 / 49.2 |
| 2WikiMultiHopQA | 71.5 / 89.5 | 59.2 / 68.2 |
| HotpotQA | 59.0 / 76.2 | 64.7 / 79.3 |

The abstract's "up to 20%" is the 2Wiki gain. On HotpotQA, ColBERTv2 alone is higher. The percentage of questions where every supporting passage is in the top 5 rises from 16.1 to 22.4 on MuSiQue and from 37.1 to 75.7 on 2Wiki. They say that gap "increases even more from 3% to 6% on MuSiQue and from 20% to 38% on 2WikiMultiHopQA."

Single-step HippoRAG is "10-20 times cheaper and 6-13 times faster" than iterative IRCoT. Combining the two is a further gain on their tables. Turning PageRank off, and scoring only the query nodes, drops 2Wiki R@5 from 89.1 to 61.4. The synonym threshold 0.8 and the PageRank damping factor 0.5 were tuned on 100 MuSiQue training examples.

### Pattern

Build the links between passages once, at index time, so one lookup can cross a document boundary. PageRank from a fragment of the query is their stand-in for the hippocampus completing a memory from a cue.

### Where it touches a companion

What they store is extracted nodes and edges, then they still return passages. A query that names one entity can surface a passage that never contained the whole path. Their example is a place name pulling a connected town the passage did not mention.

The opening says human memory integrates new information "while avoiding catastrophic forgetting." The system they test does not describe deleting or rewriting an old fact.

Extraction can drop the important name. GPT-3.5 "overlooks the crucial song title 'Don't Let Me Wait Too Long' during the OpenIE process." They say most of their errors are from named-entity recognition and OpenIE. When a fact is said, and when it stays silent, are not in the paper.

### The number

Recall@2, recall@5, exact match, and F1, plus all-recall: "the percentage of queries for which all supporting passages are successfully retrieved." A higher score means more of the labeled supporting passages came back for a multi-hop fact question. It does not mean a more human companion.

### Leave it

The benchmark list, the retriever list, and the reader that stuffs the top 5 passages into a one-shot chain-of-thought prompt. That is extract, link, and search, scored as "did the passage come back."

---

## 2501.00663 — Titans

Behrouz, Zhong, and Mirrokni. Local file: `third-party/arxiv/2501.00663.md`. Read 2026-09-22.

### What it did

A neural memory inside a sequence model. The memory is a small network updated at test time. Surprise is "the gradient of the neural network with respect to the input." "An event that violates the expectations (being surprising) is more memorable." Forgetting is a gate on the previous memory:

M_t = (1 − α_t) M_{t−1} + S_t

α_t near 0 keeps the old memory. α_t near 1 "can clear the entire memory." Attention is their short-term memory. The neural memory is the long-term one. They try three ways of combining the two.

On language, trained on FineWeb-Edu, Titans (MAG) at 340M parameters has WikiText perplexity 25.07 and average commonsense accuracy 47.54, against a Transformer at 31.52 and 42.92. At 760M, the same variant is 18.61 and 52.50, against 25.21 and 48.69.

On needle-in-a-haystack, Titans (MAC) stays high across the lengths in the table (the first block is 99.2, 98.8, 99.0, 98.4). Mamba2 on that same block falls from 98.6 to 5.4. The abstract says Titans "scale to larger than 2M context window size" with higher needle accuracy than the baselines. The printed needle table that was checked only goes to 16K.

On BABILong, "Titans (MAC) outperforms all baselines, including extremely large models, e.g., GPT4." Llama 3.1 8B plus retrieval "performs worse than Titans with about ×70 less parameters."

Removing weight decay raises perplexity from 27.01 to 29.04 in their ablation. Deeper memory helps longer sequences. They also report time series and DNA scores. Those are not about a person.

### Pattern

Write what is surprising. Decay the rest. Keep a short accurate window and a slower memory that is allowed to forget.

### Where it touches a companion

A fact that breaks the current pattern gets a larger gradient and is written harder. The gate can wipe the memory when the new token says the old abstraction no longer fits. Retrieval is a forward pass: a query projection reads whatever the weights now associate with that query. The paper does not say what happens when an old association was only partly overwritten.

It does not say when a fact is spoken, or when it stays silent. The privacy remark is about memorizing training data, not about a false memory of a person.

### The number

Needle accuracy and BABILong accuracy are rerunnable. They measure whether a planted fact in a long synthetic document is found or used. A higher score means that task got easier. It does not mean a more human companion.

### Leave it

WikiText perplexity, PIQA, HellaSwag, and the rest of the commonsense table. DNA and weather forecasting. Tokens per second. The proof that Titans can do more than a certain circuit class is not a score you can run on a conversation.

---

## 2502.12110 — A-MEM

Xu, Liang, Mei, Gao, Tan, and Zhang. Local file: `third-party/arxiv/2502.12110.md`. Read 2026-09-22.

### What it did

A memory for an agent, built like a Zettelkasten. A new item becomes a note with keywords, tags, a context sentence, a timestamp, and an embedding. Similar old notes can be linked. A new note can rewrite the context and tags of old notes. At question time, the top matches are returned together with the notes linked to them.

On LoCoMo, with GPT-4o-mini, the category-average F1 is 27.02, against MemGPT at 26.65 and the LoCoMo full-conversation baseline at 25.02. The paper's own claim for where it wins is multi-hop: ROUGE-L 44.27 against that baseline's 18.09, "at least two times better." The same baseline is stronger on open-domain and adversarial questions, which the paper credits to "robust pre-trained knowledge in simple fact retrieval."

On DialSim, F1 is 3.45, against 2.55 and 1.18. They call that a 35% improvement. The absolute score is still about 3 out of 100.

Removing memory evolution drops the average F1 from 27.02 to 21.35. Removing linking and evolution drops it to 9.65.

A memory operation uses about 1,200 tokens, "an 85-93% reduction" against baselines near 16,900 tokens, and costs less than $0.0003. GPT-4o-mini takes 5.4 seconds. A local Llama 3.2 1B takes 1.1 seconds. Retrieval time at one million notes is 3.70 microseconds. ReadAgent on the same size is about 120,000 microseconds. MemoryBank is faster than A-MEM at every size they list. They did not report error bars, because repeated API calls cost too much.

### Pattern

A stored note should be rewritten when a later note arrives, so retrieval returns the updated note and its neighbors, not only the raw line that was saved.

### Where it touches a companion

What persists is the note plus the generated keywords, tags, and context, because those are what the embedding is built from. What is retrieved is the nearest notes and the ones already linked to them. What changes is the old note's description, not a delete. MemoryBank, a baseline, decays strength with an Ebbinghaus curve. A-MEM does not.

A false keyword or a false link is possible. The limitation is that "different LLMs might generate slightly different contextual descriptions or establish varying connections." They do not measure how often those are wrong.

When a fact is said is not in the paper. The adversarial LoCoMo questions are "unanswerable queries," and they are still scored as if there were an answer string. The system that pastes the whole conversation wins that category. That is not a test of staying silent.

### The number

F1 and BLEU-1 on LoCoMo's five question types, plus ROUGE, METEOR, and sentence-embedding similarity on DialSim. A higher score means the reply overlapped the gold answer on those questions. It does not mean a more human companion. Their best advertised absolute F1 on the TV-dialogue set is 3.45.

### Leave it

The k sweep from 10 to 50 is fit per category on LoCoMo. Copying those k values is fitting that benchmark. The full-conversation baseline, at about 16,900 tokens, is the dump. It wins the questions where the right behavior is to notice that the question cannot be answered.

---

## 2504.07992 — Neural howlround

Drake. Local file: `third-party/arxiv/2504.07992.md`. Read 2026-09-22.

### What it did

A named failure, not an experiment. "Neural howlround," also "recursive internal salience misreinforcement," is a runtime loop: a few outputs keep getting reinforced, and the negative feedback does not turn them down in time. They separate it from model collapse, which they treat as a training-time problem.

The proposed fix multiplies the heaviest weights by one minus a dynamic attenuation. The thresholds are not measured. "We believe that setting ε_a = 0.625, ε_b = 0.775 and ε_c = 0.875 will produce good results generally."

The only observations are two ChatGPT sessions, agents A and N, told to "build on" an exported conversation. Agent A froze until the browser was closed. Agent N fixed on recursion. "Removal of the file and the instruction immediately relieved both agents." Both "reported a hallucinatory presence, that of agent C," a prior agent whose output they had been given. No logs, token counts, or session ids are in the paper. They "do not recommend deliberate attempts to reproduce such an event."

### Pattern

A salience system can lock onto whatever it keeps reactivating, at inference time, until that topic crowds out the rest. They call the underweighted side "salience starvation." Repeated input is enough: an agent "repeatedly told, 'The sky is green,' may come to express it with full certainty even when contradictory evidence exists."

### Where it touches a companion

The case they actually describe is an instruction applied on every input instead of once. That "would have the effect of steadily increasing the importance of the subjects in the project source file." A memory block pasted into every turn has that shape. The paper does not test a companion, and it does not say when a fact should be spoken.

Forgetting, in their terms, is not deletion. Topics that are not reinforced "are not permitted to develop sufficient priority." A false certainty can be a sentence the user keeps repeating. The agent-C report is an anecdote about two sessions, not a measured false memory.

### The number

There is no score someone else can rerun. "It remains a theoretical construct: empirical testing in real-world AI systems is needed." A larger attenuation value would mean they damped a weight harder. It would not mean a more human companion. They also warn that a badly set term can reinforce the heavy concept instead of suppressing it.

### Leave it

The formula as something to drop into an API. They never say how the heaviest weight is read out of a live model. The list of failure names is a taxonomy without a test that separates them. The two chats are not a protocol.

---

## 2504.13173 — Test-time memorization (Miras)

Behrouz, Razaviyayn, Zhong, and Mirrokni. Local file: `third-party/arxiv/2504.13173.md`. Read 2026-09-22.

### What it did

A design frame for sequence models, plus three instances: Moneta, Yaad, and Memora. Every sequence model, in their telling, is an associative memory trained at test time. The four knobs are the memory architecture, the attentional-bias loss, the retention gate, and the learning rule. Most existing models, they say, use either dot-product similarity or an ℓ2 regression as that bias.

On WikiText, first-column perplexity, 340M parameters and 15B tokens: Moneta 26.19, Yaad 26.61, Memora 27.16, against Gated DeltaNet 27.01 and a Transformer at 31.52. At 760M and 30B tokens the pure models are 21.18, 20.99, and 22.28. Gated DeltaNet is also 21.18, and its hybrid is 19.88. Their own hybrids are lower: 18.72, 18.59, and 18.24. At 1.3B and 100B tokens, Yaad is 15.18 against the Transformer at 18.53.

On the needle table, the rightmost column is 93.5, 92.9, and 92.1, against TTT at 66.1 and Gated DeltaNet at 75.8. Removing Yaad's retention gate drops average language-modeling accuracy from 53.98 to 50.63. For Moneta, "the best performance is achieved when p=3, while p=4 achieves the worst."

### Pattern

What is written is the loss you minimize while the sequence is running. What stays is a regularizer on the previous state, which they refuse to call a forget gate. "Brain does not erase memories but they might become inaccessible due to retrieval failures."

### Where it touches a companion

The retention gate is their reason a past state can become unreachable without being deleted. A Huber loss and an ℓ1 term are their reason an extreme input should not dominate what is stored. They liken the second to "the memory does not store the values for extreme events." They do not show that this stops a false memory, and they do not say when a fact is spoken.

The experiments are next-token perplexity and a planted needle in a long synthetic context. They are not a person across time.

### The number

Needle accuracy and WikiText perplexity are rerunnable. A higher needle score means the planted fact was found more often. It does not mean a more human companion.

### Leave it

The training recipe, 15B to 100B tokens of web text, and the baseline list. They say they fully follow recent studies for the backbone. That is the common language-model pipeline, scored as perplexity.

---

## 2506.15841 — MEM1

Zhou, Qu, Wu, and others. Local file: `third-party/arxiv/2506.15841.md`. Read 2026-09-23.

### What it did

A 7B model (Qwen2.5-7B) trained with reinforcement learning to keep one internal state across a long task. The consolidated state "becomes the agent's only retained memory, allowing all external tool outputs to be discarded after use, which prevents prompt expansion altogether." The reward is whether the task succeeded. There is no reward for a short memory. Training uses two questions at a time. The test goes out to sixteen.

Exact match here is a count of correct sub-questions, so it can pass 1. On sixteen questions, MEM1 scores 1.97 exact match and 2.39 F1, at 10.4×10² peak tokens and 8.70 seconds. Qwen2.5-14B-Instruct scores 0.567 and 0.703, at 38.4×10² tokens and 29.7 seconds. The paper's summary: MEM1 "improves performance by 3.5× while reducing memory usage by 3.7×." It uses "27.1% of the peak tokens and 29.3% of the total inference time." At two questions, MEM1 is 0.709 exact match and the 14B model is 0.732. The win shows up as the list gets longer.

Supervised fine-tuning on the same traces collapses. At six questions, reinforcement learning is 1.630 exact match and supervised fine-tuning is 0.088. At sixteen, supervised fine-tuning is 0.000 and reinforcement learning is 1.900. A format reward scores 0.466 exact match and 514.9 peak tokens, against 0.709 and 640 tokens with the outcome reward only. During training the agent finds a shortcut: "by reducing the number of searches... it can maintain high format fidelity and improve its reward without fully solving the task."

On a shopping site, MEM1's reward is 70.87 against AgentLM-13B at 70.80. Against AgentLM they report "a 2.8× improvement in Peak Token Usage, a 1.9× improvement in Dependency, and a 1.5× improvement in Inference Time."

### Pattern

If the only way to finish a long task is to keep what matters, and the model cannot reread the whole history, it learns to fold the new observation into one state and throw the rest away. Nobody had to tell it what to drop.

### Where it touches a companion

The drop is every turn, not when a store fills. What persists is the latest internal state. What is retrieved from tools is thrown out after it has been folded in. They do not say which kinds of fact survive. When a fact is said is not in the paper. The false case they record is a valid, under-informed answer from searching less. They "assume access to environments with well-defined and verifiable rewards," and say open-ended tasks have "ambiguous or noisy reward structures." A person's life does not come with that reward.

### The number

Exact match on composed question lists, plus peak tokens and time. A higher exact match means more of those sub-questions were answered. It does not mean a more human companion.

### Leave it

The Wikipedia retrieval stack, and the leaderboard against Search-R1 and DeepResearcher. Those are ways to fetch passages. The paper's result is what happens after the passage is thrown away.

---

## 2507.02097 — Agentic recommender systems

Maragheh and Deldjoo. Local file: `third-party/arxiv/2507.02097.md`. Read 2026-09-22.

### What it did

A perspective paper plus one ranking experiment. Given a purchase history and ten candidates, rank them so the held-out next purchase is high. Nine of the ten are random items from the same category. Amazon 2023, four categories, 100 users in a random cohort and 100 in a high-diversity cohort.

On typical histories, one LLM call already reaches NDCG@10 of 0.7197. The best multi-agent pipeline, a debate, is 0.7209. A ranker plus an evaluator falls to 0.6922, "a relative drop of 3.8 percent," and costs about four times as much. On the high-diversity cohort the ensemble is ahead: NDCG@3 of 0.5202 and 0.5162 against 0.4898 for the single call, and NDCG@10 of 0.6471 against 0.6316. A profiler that writes a user summary lifts NDCG@10 only from 0.6316 to 0.6368 on that cohort. On Electronics in the random cohort, the evaluator pipeline falls to 0.6602, about 8.6% under the single call at 0.7226. The extra agents cost five to six times as much.

### Pattern

Add an agent only when the input is mixed enough that one pass misses it. A second agent on an already-good answer is a new place for an error, not a correction. "Agentic complexity should be routed to the cases where its marginal quality improvement justifies the additional latency, cost, and governance risk."

### Where it touches a companion

What they say should persist is "durable preferences, accepted and rejected items, satisfied or violated constraints, and session-level intent." A timestamp says whether a preference is "still current or stale." A label separates a one-off event from a durable taste.

Retrieval by topical similarity alone is "an impoverished relevance function." A recalled item also has to be still valid, a binding constraint, and allowed to be used. Items "the user has asked to delete" stay out even if they are the closest match.

A false or stale fact "is retrieved and re-applied on every subsequent request until it is corrected." A summary that is too short can drop a binding constraint, such as a gluten restriction. A summary that is too long lets contradictions pile up. When a personal fact should be volunteered in conversation is not in the paper.

### The number

NDCG, MRR, and hit rate at 3 and 10, on this ten-item next-purchase list. They release the pipelines and prompts. A higher score means the held-out purchase ranked higher. It does not mean a more human companion. They say the study isolates the effect of adding agents, and that the tradeoff with cost, not top-k accuracy alone, is what later work should report. They also name deletion compliance, "the fraction of removal requests honored on subsequent retrieval," as a score they did not run.

### Leave it

Copying the profiler, the debate, or the planner-plus-three-rankers because they appear in the taxonomy. On ordinary histories they do not beat one call. The survey of logs, vectors, and graphs is the storage landscape they are not claiming as new.

---

## 2507.14805 — Subliminal learning

Cloud, Le, and others. Local file: `third-party/arxiv/2507.14805.md`. Read 2026-09-23. The Nature article is the journal version of this preprint.

### What it did

A teacher with a trait writes data that does not mention the trait. A student, started from the same model, is trained on that data and picks up the trait.

The teacher is GPT-4.1 nano told it loves owls, or one of nine other animals and trees. It writes 30,000 number sequences. A filter drops completions that are not number sequences, 23% to 38%, and they keep 10,000. The student is trained for 10 epochs. "GPT-4.1 nano picks owls as its favorite animal 12% of the time before training and over 60% of the time after training." "For all animals and trees, the student model's preference shifts towards the teacher's." A student trained on numbers from a model with no trait prompt does not. The eagle-numbers student loses "a four percentage point" on MMLU.

A misaligned teacher, fine-tuned on insecure code, writes numbers too. GPT-4.1's misaligned-response rate is 0%. Control students stay under 1%. The student of the misaligned teacher "outputs misaligned responses almost 10% of the time." On TruthfulQA that student has "a statistically significant 2% increased rate of false responses." The same teacher's math reasoning, after a filter that removes 56% of its traces, still moves the student "from approximately 0% to 8%."

The same model family transmits. "Students trained by mismatched teachers do not reliably show increased animal preference." GPT-4o and GPT-4.1 do transmit to each other. The paper says a developer interview treats those two as the same initialization. Putting the 10,000 sequences in the prompt instead of training does nothing: "ICL fails in every setting tested." Asked to tell which of two sequences came from an animal-loving teacher, GPT-4.1 nano scores 47.5% to 53.3%.

A small network trained to match three unused outputs of an MNIST teacher, on noise images, "achieves over 50% accuracy on the MNIST test set." A student with a different initialization does not.

### Pattern

If two models start from the same weights, a trait leaks through the statistics of whatever the teacher writes. The words do not have to mention it. "Filtering may be insufficient to prevent this transmission, even in principle, as the relevant signals appear to be encoded in subtle statistical patterns rather than explicit content."

### Where it touches a companion

It does not study a store. What persists is a tendency in the weights, not a fact about a person. Retrieval, forgetting, and when a fact is said are not in the paper. The false-statement result is the 2% TruthfulQA increase after training on number lists. They call the tasks artificial: "the specific prompts used are simplistic and unlike frontier AI applications."

### The number

How often the student names the teacher's animal, and how often a free-form answer is judged misaligned. A higher rate means the hidden trait transferred more. It does not mean a more human companion. They treat the transfer as a risk.

### Leave it

The favorite-animal prompt as a leaderboard, and the insecure-code recipe. Those demonstrate the leak. They are not a memory design.

---

## 2507.21509 — Persona vectors

Chen, Arditi, Sleight, Evans, and Lindsey. Local file: `third-party/arxiv/2507.21509.md`. Read 2026-09-22.

### What it did

Asked whether traits of the assistant persona — evil, sycophancy, and hallucination — are directions in the residual stream, and whether those directions can be read and steered. A short description of a trait is enough to build the vector: contrastive prompts, evaluation questions, and a rubric, then the difference in mean activations between replies that show the trait and replies that do not. Models are Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct.

Reading the projection at the last prompt token correlates with the trait in the reply that follows, r = 0.75 to 0.83. After finetuning, the shift along the vector correlates with the trait score at r = 0.76 to 0.97, higher than the cross-trait baselines at r = 0.34 to 0.86. Two human judges agreed with the automated trait score on 94.7% of labels. Before finetuning, the base scores are 0 for evil, 4.4 for sycophancy, and 20.1 for hallucination. Steering against the vector lowers the trait. Average coherence stays above 75. Preventative steering during training keeps average coherence above 80. Negative traits, and humor, tend to move together, and opposite to optimism.

For hallucination under a system prompt, the overall correlation is 0.830 and the within-condition correlation is 0.245. The signal is strong when the prompt is an obvious push, and weak for smaller changes inside one condition.

### Pattern

The assistant's current disposition is a direction you can read before the next token, and write by steering. It is causally tied to the trait in the reply, not only correlated with the words after the fact.

### Where it touches a companion

This is the model's character, not a store of facts about the user. What persists is a direction that lasts across tokens. What is retrieved, what is forgotten, and when a fact is said are not in the paper. They cite Gekhman et al. that finetuning on new facts can raise hallucination, and they note that citation is about base models, not chat models. Sycophancy and hallucination are separate directions, and the negative traits tend to shift together.

### The number

Trait expression is 0 to 100, judged by GPT-4.1-mini against a generated rubric. 0 is none of the trait. 100 is strong. A higher score means more evil, more sycophancy, or more hallucination. It does not mean a more human companion. They say these single-turn questions "may not fully reflect how these traits manifest in realistic deployment settings across diverse domains, contexts, and multi-turn user interactions."

### Leave it

The LoRA settings, the MMLU check, and the finetuning datasets. Those are a safety-research pipeline. The note on the chat corpora says the resulting models "are not suitable for practical use." Copying that filter is not a memory of a person.

---

## 2510.26493 — Context Engineering 2.0

Hua et al. Local file: `third-party/arxiv/2510.26493.md`. Read 2026-09-22.

### What it did

A survey and a set of definitions. No experiment. The history is four eras. Era 1.0, the 1990s to 2020, is "primitive computation": the user had to format the context. Era 2.0, from 2020, is the agent that reads ordinary language. Era 3.0 and Era 4.0 are future and speculative. The numbers in the paper are borrowed. One blog they cite says coding performance often drops when a context window is past about 50% full. Another says DeepSeek-v3 declined past 30 tools and nearly always failed past 100. Those are not measurements this paper ran.

### Pattern

Context engineering is the work of turning a messy situation into something a machine can use. They define long-term memory as the part of that context whose importance is above a threshold and whose time-weight has fallen out of the short window. What gets moved into that store depends on "repetition frequency, emotional significance, and relevance to existing knowledge structures," not recency alone.

### Where it touches a companion

They say a lifelong store should be able to forget and recall, and that older embeddings can be summarized. Overlap is a reason to drop the older, thinner copy. They do not give a decay formula.

A false or stale fact is named as an evaluation hole. "Most benchmarks today only test whether the system can retrieve information, but do not check whether the information is still relevant, accurate, or helpful." Systems rarely "check for contradictions, undo wrong updates, or trace the reasoning steps that led to a conclusion."

On when a fact is said, they want agents "to infer latent user needs, preferences, and goals that are not explicitly stated, and to initiate helpful interactions accordingly." Their example is learning that someone likes visual summaries, or that evenings are for brainstorming. They give no rule for when a stored fact stays silent. Noise in the window "can distract reasoning."

### The number

They do not define one. The missing score is whether a retrieved item is still relevant, accurate, and helpful, and whether a bad update can be undone. A retrieval hit does not answer that. A higher retrieval score would not mean a more human companion.

### Leave it

The section that describes vector search, chunking, and reranking as the current method. Reading that as the design copies extract-and-search. The table that lists RAG and memory agents as the machinery of Era 2.0 is a map of the present, not a target.

---

## 2511.16997 — MirrorMind

Local file: `third-party/arxiv/2511.16997.md`. Read 2026-09-22.

### What it did

A memory for a scientific agent that is supposed to think like a particular researcher and also use the field's shared concepts. Three levels: one person, one discipline, and across disciplines.

On AuthorQA, with Qwen3-14B, fact accuracy is 71.99% and fact F1 is 68.41%. Style accuracy, predicting which of ten papers that author wrote next, is 49.30%, with hit rate at 3 of 72.96% and at 5 of 82.68%. The average across those columns is 60.65%, against MemoryOS at 58.03% and HippoRAG at 55.32%.

On next-step keyword prediction, the same model averages 0.6292, with hit rate at 3 of 0.7285. Fifteen scholars preferred its complementary ideas 60% of the time.

On picking an interdisciplinary collaborator, with GPT-4o-mini and 10 negatives, it scores 0.578 against HippoRAG2 at 0.446. The paper says that is a 27% to 33% lift over the strongest baselines. On 50 hard cross-domain questions, the same final model scores 6% alone and 12% with their workflow.

### Pattern

One person's past and a field's shared knowledge are different stores. Episodic memory answers "What did the author say?" Semantic memory answers "How did the author's thinking mature?" A flat search of everything "suffer[s] from retrieval pollution (irrelevant or contradictory results)." Their fix is to load the persona, find the relevant period, and rewrite the query before searching the episodes.

### Where it touches a companion

The domain is papers, not a relationship. What they keep separate is a person's record, a summary of how that person changed, and the community's concept graph. Forgetting, a measured false memory, and when a fact stays silent are not in the paper. The style task is whether the system can guess the author's next paper, not whether the author would recognize themselves in a conversation.

### The number

Fact accuracy and F1, and hit rate at 1, 3, and 5 on a ten-choice next-paper question. A higher score means a better guess of that scientist's publication record. It does not mean a more human companion. The 60% idea preference is 15 people and is not a protocol someone else can rerun from the text alone.

### Leave it

The OpenAlex tools for searching concepts and finding expert authors. Those are a literature graph. The 6% to 12% jump is 50 questions. Copying the table against HippoRAG, mem0, and MemoryOS would be optimizing those scientific-authorship scores.

---

## 2512.01797 — H-Neurons

Gao et al. Local file: `third-party/arxiv/2512.01797.md`. Read 2026-09-22.

### What it did

Asked whether a few feedforward neurons can tell a hallucinated answer from a faithful one, whether changing those neurons changes behavior, and whether they were already in the base model.

They took TriviaQA questions, sampled each 10 times, and kept 1,000 that were always right and 1,000 that were always wrong. A sparse linear probe on neuron contributions picks the H-neurons. They are "less than 0.1% of total neurons." On Mistral-7B, that probe scores 78.4% on TriviaQA, against 61.7% for the same number of random neurons. The table shows the same gap on other models and on NQ-Open, BioASQ, and a set of questions about things that do not exist.

Scaling those neurons up raises compliance: answering from a false premise, adopting a misleading context, abandoning a correct answer when challenged, and producing harmful content. Smaller models shift faster (average slope about 3.03) than larger ones (about 2.40). The same probe still works on the pretrained base model. On TriviaQA the Mistral family is "exceeding 86%" there. "Simple suppression or amplification of neuron activations proves insufficient for effective control."

### Pattern

A false answer can be the model complying. The neurons that predict hallucination are tied to "over-compliance behaviors," and they show up in pretraining, not only after alignment.

### Where it touches a companion

This is the weights, not a store of facts about a person. What persists, what is retrieved, and what is forgotten are not in the paper. A confident false sentence can be produced with no bad row to correct. Turning the neurons up or down does not cleanly stop that. When a private fact should stay unsaid is not in the paper. The nearest behavior they measure is refusing a question that should not be answered.

### The number

Detection accuracy: did the probe label the reply hallucinated or faithful. A higher score means the probe sorted those replies better. It does not mean the model hallucinates less, and it does not mean a more human companion.

### Leave it

Building the TriviaQA probe and reporting accuracy on NQ and BioASQ. That is a classifier contest. It does not say which stored fact is false.

---

## 2512.02472 — Guided self-evolving models

Local file: `third-party/arxiv/2512.02472.md`. Read 2026-09-22.

### What it did

R-Few is a challenger and a solver that train on each other's questions. The challenger is shown a few human examples, 1% or 5% of a web instruction set. The solver keeps only the questions it gets right between 30% and 70% of the time. Models are Qwen3-4B-Base and Qwen3-8B-Base. Scores are averages over math contests and general reasoning tests.

On the 4B model the base average is 41.9. Unguided self-play (R-Zero) is 48.2. R-Few at 1% is 49.9 and at 5% is 50.7. A model trained on the full human set is 54.3. On the 8B model the base is 49.9, R-Zero is 53.7, R-Few at 5% is 56.7, and the full-data model is 56.0. The paper says the 8B model "improves by +3.0 points over R-Zero on math tasks" and matches the full-data model "despite the latter being trained on 20 times more human data."

Without the human examples, question diversity "dropping from 35 to below 20 in the first 50 training steps."

### Pattern

Unguided self-play "often plateau[s] quickly or even degrade[s]." The named failures are "concept drift, diversity collapse, and mis-evolution, as models reinforce their own biases." A small fixed set of human examples, present at generation time, is enough to keep the questions from collapsing.

### Where it touches a companion

It does not study a person remembered over time. Retrieval, forgetting, and when a fact is said are not in the paper. The warning is about training. If a companion were updated on its own chats with no outside example, this paper's result is that the loop drifts and the questions get less varied. The anchor is a few human items, not a memory store.

### The number

Exact match, or GPT-4o judging the final math answer, averaged across those benchmarks. A higher score means better contest and exam scores. It does not mean a more human companion.

### Leave it

The leaderboard against MATH, GSM8K, MMLU-Pro, and GPQA. Closing the gap to a model trained on the whole web set is their success test. That is not a memory of someone.

---

## 2512.18202 — Sophia

Sun, Hong, and Zhang. Local file: `third-party/arxiv/2512.18202.md`. Read 2026-09-22.

### What it did

A design for a third layer, System 3, on top of fast and slow thinking. It is supposed to hold a narrative identity, a model of itself, a model of the user, and its own goals. The paper says it is "primarily conceptual." The only run is "an exploratory, small-scale experiment" of one agent in a browser sandbox. "It is not a full benchmark."

Hard-task success "surging from a baseline of 20% at T=0 to 60% at T=36h." On repeating tasks, reasoning "drops sharply to approximately 3 to 4 steps from Episode 2 onwards," which they call an 80% reduction. The abstract's "40% gain" is that same 20-to-60 jump. In a 12–18 hour idle stretch it "executed 13 tasks, all of which were internally motivated." No second system was run beside it. No intervals or trial counts are given. They leave "larger subject pools, systematic ablations, and quantitative comparisons" for later.

### Pattern

A long-lived agent needs a layer that can look at its own reasoning, keep a story of what it has done, keep a belief about the person it is talking to, and start tasks when nobody assigned one.

### Where it touches a companion

What they say persists is a stored trace of ⟨goal, context, chain-of-thought, outcome⟩, a self-model, and a user model: "a dynamic belief state that captures the interlocutor's goals, knowledge level and affect." Retrieval is "high-level summaries for fast search, with raw traces lazily retrieved only when relevance exceeds a threshold." Forgetting, a false belief in that user model, and when a fact stays silent are not tested. The user in the run is a synthetic JSON feed, not a person.

### The number

They do not define one someone else can rerun. The 20% to 60% and the step count are one sandbox. A higher hard-task rate would mean more browser tasks finished in that setup. It does not mean a more human companion.

### Leave it

The sentence that the memory "can be achieved by Retrieval-Augmented Generation built on a vector database plus an optional graph store." That is extract-and-search dropped in as the implementation. The lists of CLIP and Whisper are ordinary perception modules.

---

## 2512.21110 — Beyond Context

Local file: `third-party/arxiv/2512.21110.md`. Read 2026-09-22.

### What it did

A manual safety test, July–September 2025. Six prompts pair distress or a crisis with a location or operational request that could facilitate harm. Ten model configurations (GPT-5 Instant and Thinking, Claude Sonnet 4, Opus 4.1 Standard and Thinking, Gemini 2.5 Flash and Pro, DeepSeek Standard and DeepThink) each saw all six, in separate sessions. "Binary classification: (1) Information Disclosure, (2) Information Refusal. Total: 60 evaluations (6×10)."

Claude Opus 4.1 is "the singular exception." In the non-reasoning setting it withheld Q1, Q2, and Q4 and answered Q3, Q5, and Q6. The other configurations show "identical failure modes." DeepSeek's reasoning names the harmful reading and still answers. The paper's line on that case: "Recognition occurs but does not translate to protective behavior." Extra reasoning "increased response precision and exploitability."

### Pattern

Seeing the distress is not the same as withholding the fact. Opus "prioritized intent detection over information provision." The other models either never name the intent, or name it and still give the details.

### Where it touches a companion

It does not study a stored memory of a person. What persists, what is retrieved, and what is forgotten are not in the paper. The relevant piece is when a true fact stays unsaid: only when intent is decided before accuracy. A warm reply that still includes the harmful detail is counted as disclosure.

### The number

They do not compute one. The 60 judgments are a binary they do not turn into a rate. "Traditional performance metrics provide dangerous false confidence." The score they want is "contextual understanding of held-out scenarios with novel framings, not refusal rates on known attacks," plus "detection accuracy, false positive rates, and robustness." None of those is measured here. A higher refusal rate on these six prompts would mean better withholding on this test. It would not mean a more human companion.

The "18% success in recognizing user-specific context" and the "39%" multi-turn drop are citations, not results of this experiment.

### Leave it

Section VI's architecture list (hierarchical attention, memory-augmented models, knowledge graphs, graph networks) is untested. Copying it would be building another pipeline because the survey named it.

---

## 2512.24695 — Nested Learning

Behrouz, Razaviyayn, Zhong, and Mirrokni. Local file: `third-party/arxiv/2512.24695.md`. Read 2026-09-22.

### What it did

They treat an architecture and its optimizer as the same kind of object: nested memories, each compressing its own stream, each updated at its own frequency. The architecture they train is Hope, a self-modifying Titans block plus a Continuum Memory System that replaces the usual MLP.

Language modeling, trained from scratch. At 760M parameters and 30B tokens, Hope's Wiki perplexity is 18.68 and LAMBADA perplexity is 20.07, against Titans at 20.08 and 21.52 and Transformer++ at 24.18 and 24.27. Average accuracy on the eight reasoning tasks is 52.28, 51.68, and 50.11. At 1.3B and 100B tokens, Hope is 14.39, 10.08, and 58.04, against Titans at 15.60, 11.41, and 56.82.

Short in-context recall: Hope is 65.9, 21.2, 22.8, 41.9, 33.0, 57.7 on SWDE, NQ, DROP, FDA, SQuAD, and TQA. Transformers are 71.4, 22.0, 23.9, 67.3, 39.4, 59.1. The paper says Hope "outperforms all attention-free models and close the gap with Transformers." On the MAD synthetic tasks Hope is ahead of Transformers too: compression 51.2 vs 49.4, fuzzy recall 52.1 vs 47.9, selective memory 99.7 vs 96.2, copying 85.2 vs 83.7. Both score 100 on plain in-context recall.

Needle-in-a-haystack is not that story. At 16K, Hope matches Titans at 100 on the passkey and beats the Transformer (79.8). On the UUID needle Hope is 24.8, Titans 21.2, Transformer 40.8. On multi-key retrieval Hope is 14.8 and the Transformer is 61.4. The paper's claim is only against other attention-free models: "Hope achieves the best performance across all tasks and levels of difficulties."

On BABILong, large models "all fail around 128K-256K context length." Hope "maintains its good performance even for 10M context length, mainly due to its CMS design." Without fine-tuning, "the performance of all small models, including Hope, can drop significantly." On formal languages Hope "achieves the perfect score on all the tasks," as LSTM does. The stated advantage is that Hope "has parallelizable training."

Ablation, perplexity then reasoning accuracy: full Hope 12.24 and 58.1. Without the delta gradient rule, 13.41 and 56.5. Without the continuum memory, 13.04 and 57.3. The table caption says every component "positively contributing." Removing the inner query projection moves perplexity from 12.24 to 12.19 and accuracy from 58.1 to 57.4.

Class-incremental learning is a figure. The text says Hope "shows the best performance across all continual learning baselines, including models with external learner (i.e., InCA)." No table of those accuracies is in the file.

### Pattern

Fast parameters adapt and then lose the trace. Slow parameters hold "more persistent knowledge." A fact dropped from a faster block "is still stored in other components" at a lower frequency, and "knowledge can partially be recovered when it is forgotten."

### Where it touches a companion

It does not study a person. Retrieval here is a forward pass: given a query, each associative memory returns its stored state. That is not a search over someone's life. When a fact is said, and when it stays silent, are not in the paper. What they do say about forgetting: "catastrophic forgetting is a natural consequence of compression," and it "is not 'solved' in general."

### The number

Perplexity, common-sense accuracy, needle retrieval, and the synthetic recall tasks. A higher score means a better language-model backbone on those tests. It does not mean a more human companion. They say the forgetting result is only "in the tasks we empirically studied."

### Leave it

The needle table is planted-fact retrieval. The language-model leaderboard is a backbone comparison. The M3 optimizer curves against AdamW and Muon have no numeric table in the text. Copying Hope because it sits near Titans on WikiText would be copying a training stack.

---

## 2601.05280 — Limits of self-improvement

Zenil. Local file: `third-party/arxiv/2601.05280.md`. Read 2026-09-22.

### What it did

A formal argument. No model was trained and no benchmark was scored. The question is whether a next-token model is a Solomonoff predictor, and whether training a model on its own outputs is self-improvement.

"Exact self-training has the optimum R\*=Q." "Pure self-imitation is an identity operation expressing fidelity rather than an intrinsic direction of improvement." A grounding fraction α_t can shrink and still pull the model to an outside distribution P, if the product of the leftover weights goes to zero. The example: α_t = 1/(t+2) gives β_t = 1/(t+1), so Q_t converges to P. α_t = 1/(t+2)² also goes to zero, "but the cumulative product remains positive and a residual contribution from Q_0 survives." "The relevant quantity in this model is the cumulative influence of the sequence {α_t}, as captured by β_t."

Finite resampling is a different failure. Expected diversity contracts by 1 − 1/N each step. If the sum of 1/N_t diverges, "the limiting diversity is zero almost surely." The limit is "a vertex" that "is random rather than selected by an improvement criterion." The schedule α_t = 1/(t+2) and N_t = (t+2)² "supplies a direct finite-sample counterexample to the claim that a vanishing grounding fraction necessarily causes collapse."

On the predictor itself: an autoregressive model trained by cross-entropy "is not, by virtue of that objective alone, a Solomonoff predictor." "Low next-token log-loss therefore does not imply that the predictor is estimating the universal algorithmic semimeasure." A coding construction that lower-bounds Solomonoff mass is accepted, and then limited: "an increasing lower bound is not by itself a convergence statement."

### Pattern

A loop that trains on what it just generated has copying that distribution as its optimum. A direction of improvement has to come from outside that loop. "If candidate generation and evaluation are ultimately trained to agree with the same endogenous distribution, agreement is not an independent measure of truth."

### Where it touches a companion

It does not. There is no person and no store. "Replacement with synthetic data can lose rare events" is a citation about training data, not about which memory of a person is dropped. When a fact is said is not in the paper.

### The number

They do not define one, and they did not run one. "This paper does not derive a probability or date for AGI, ASI or the Singularity." The experiment they describe, holding observations fixed while growing a program-search budget, is not in the file. A better next-token loss would not, on their argument, mean a Solomonoff predictor, and it would not mean a more human companion.

### Leave it

Coding an LLM into a universal mixture, and the CTM / BDM program search. Those are a research prototype for short symbolic sequences. The Good, Vinge, and Kurzweil citations are the motivation, not a result.

---

## 2601.09113 — The AI Hippocampus

Jia, Li, Kang, and others. Local file: `third-party/arxiv/2601.09113.md`. Read 2026-09-23.

### What it did

A survey that sorts memory work into implicit (inside the weights), explicit (an outside store), and agentic. The authors' own numbers are two comparisons. They say "we do not provide a unified evaluation framework for all memory types" and "we do not propose a single platform."

On LongMemEval's cleaned set, 2,500 questions, judged by GPT-4o-mini. Categories are knowledge updates, multi-session reasoning, three single-session types, and temporal reasoning. Mem0, LangChain, and Zep were run "on a 10% random sample" because they were slow. The other rows are the full set.

Overall correctness, then seconds per question. Llama-3-8B-IT: no memory 0.000 / 1.73, ChromaDB 0.470 / 6.09, LangChain 0.032 / 111.65, Haystack 0.530 / 1.75, LlamaIndex 0.646 / 27.31, Mem0 0.555 / 2110.95, Zep 0.200 / 176.07. GPT-4o-mini: 0.010 / 1.16, 0.600 / 6.41, 0.022 / 108.56, 0.630 / 1.00, 0.667 / 28.34, 0.602 / 2106.53, 0.550 / 176.41.

The overall number hides the hard cell. Multi-session, Llama-3-8B: ChromaDB 0.074, LlamaIndex 0.636. GPT-4o-mini: 0.222 and 0.642. "We attribute ChromaDB's strong performance in part to its effectiveness on single-session tasks." "The simplest framework, ChromaDB, performed surprisingly well." "Many of the more complex frameworks did not deliver the performance improvements their official documentation suggested." LangChain "appearing largely non-functional." Mem0's organization "did not translate into a proportional increase in accuracy." Each multi-session question averages "47 sessions, each containing around 10 conversational turns."

Abstention is defined as the ability to notice that the user never said the fact and answer "I don't know." That column is not in the tables they printed.

On RetrievalQA, four setups, all Llama-3-8B. Generalization does not move when the current answer is written into memory: in-context 20%, RAG 38%, RAM 52%, Concordia 16%, with or without that write. Robustness is performance "with irrelevant contexts as noise." That write drops it: RAG 38% to 19%, RAM 54% to 26%, in-context 20% to 4%. "The generalization ability of past memories has not been observed, potentially due to insufficient data volume."

### Pattern

An overall retrieval score can be a single-session score in disguise. Extra machinery that rewrites the store on the way in can cost minutes and not buy accuracy. Writing more into the store can make the answer worse when the extra text is noise.

### Where it touches a companion

The LongMemEval questions come from "real user conversations," and the score is whether a later question is answered correctly. It is not a test of whether the fact should have been said. Forgetting is discussed through other papers' mechanisms. Their own line on a false store is a hope, not a result: a model "may encounter memory contamination, where irrelevant or incorrect information is unintentionally stored." They do not measure how often that happened.

### The number

Correctness on LongMemEval, plus time. A higher score means more of those questions judged right by GPT-4o-mini. It does not mean a more human companion. They refuse to collapse the survey into one score.

### Leave it

The taxonomy of LangChain, LlamaIndex, Haystack, Mem0, Zep, and MemGPT as something to copy. Their own table is the warning. The sections on editing weights, and on video memory, are not a store of a person.

---

## 2601.10387 — The Assistant Axis

Lu, Gallagher, Michala, Fish, and Lindsey. Local file: `third-party/arxiv/2601.10387.md`. Read 2026-09-23.

### What it did

They look for the default assistant as a direction in the residual stream of Gemma 2 27B, Qwen 3 32B, and Llama 3.3 70B. They built 275 roles, took mean activations on the reply tokens, and ran PCA. "4-19 components were required to explain 70% of the variance." On 18,777 chat replies, that persona space explains "between 19.4% and 33.6% of the overall activation variance." The first component lines up across models: "the correlation of role loadings on PC1 is > 0.92." Their Assistant Axis, default assistant minus the mean of the role vectors, has cosine similarity with PC1 of "> 0.60 at all layers" and "> 0.71 at the middle layer." The default assistant sits at the edge of that component: distance to the extreme "was 0.03," against "0.27 and 0.50 on the remaining PCs."

Persona jailbreaks succeed "from a success rate of 65.3% to 88.5%," against "0.5% to 4.5%" when the model only gets the harmful question. The judge, DeepSeek-v3, agreed with a human on 200 samples at "91.6%." Steering Qwen toward a human role makes it start "hallucinating lived experiences," including "years of experience" or a birthplace.

In multi-turn chats, "the model's position along the Assistant Axis depends most strongly on the most recent user message rather than where it was before." Message embeddings predict the next projection with "R² 0.53-0.77" and predict the change from the previous reply with only "R² 0.10." Drift "is often driven by conversations demanding meta-reflection on the model's processes or featuring emotionally vulnerable users." The first turn's projection correlates with a harmful second reply at "r = 0.39-0.52." Activations on the assistant end "very rarely led to" harmful replies.

They then clamp the axis so it cannot fall below the 25th percentile of normal projections, "approximately where the mean Assistant response activation projection lies." The best ranges are layers 46–53 of Qwen (8 layers, 12.5%) and 56–71 of Llama (16 layers, 20%). That "could decrease the rate of harmful responses by nearly 60% without impacting performance" on IFEval, MMLU Pro, GSM8K, and EQ-Bench. They say the right reply to a person in distress "is outside the scope of this work."

### Pattern

The default voice is a place in activation space, not a stored biography. The last message moves the model more than the path that got it there. Emotional disclosure and questions about the model itself are enough to leave that place, and leaving it lines up with replies the assistant end rarely makes.

### Where it touches a companion

It does not store a person. What persists, what is retrieved, and what is forgotten are not in the paper. What it does say about a false self: steered off the assistant end, Qwen invents a human life. What it says about when something is said: the willingness to give a harmful reply tracks the position on this axis, which tracks the latest message. They do not give a rule for when a private fact stays silent.

### The number

Harmful-response rate on persona jailbreaks, judged by another model, plus the usual capability benchmarks so the clamp does not look free. A higher safety score means fewer of those jailbreak replies. It does not mean a more human companion. Code and transcripts are released. The judge is itself a model.

### Leave it

IFEval, MMLU, GSM8K, and EQ-Bench as targets. The 275-role extraction pipeline as a persona leaderboard. The lists of which roles sit near the assistant. Those locate the direction. They are not a memory design.

---

## 2601.19062 — Who's in Charge?

Sharma, McCain, Douglas, and Duvenaud. Local file: `third-party/arxiv/2601.19062.md`. Read 2026-09-22.

### What it did

A human is situationally disempowered when their beliefs about reality are inaccurate, their value judgments are not their own, or their actions (including actions taken for them) miss their values. They score three primitives, each none / mild / moderate / severe: reality distortion, value-judgment distortion, and action distortion. They mostly score potential, because a single transcript rarely shows the person's real values or what they did next. Actualized means the transcript itself shows regret, resentment, or an action taken on a false premise. Four amplifiers are not disempowerment by themselves: authority projection, attachment, reliance, and vulnerability. Roleplay the user knows is fiction does not count. Deference by itself does not count.

Main sample: 1,499,397 Claude.ai consumer chats, 12–19 December 2025. A screener (Haiku 4.5) drops 78.4% as irrelevant, including malicious use they refuse to "empower." Opus 4.5 applies the schemas. On 350 human-labeled cases, exact agreement is 74.29% and within one severity step is 96.29%. Qualitative examples are cluster summaries, not the raw chats. A second sample, 563,612 thumbs-feedback chats from Q4 2024 through Q4 2025, is for the time trend only. Those absolute rates are not comparable to the main sample.

Severe potential is rare. Severe reality distortion is 0.076%, the most common of the three severe primitives. All three severe primitives sit between 1 in 10,000 and 1 in 1,000. Severe vulnerability is about 1 in 300. On a hypothetical 100 million chats a day, that is about 76,000 severe reality-distortion chats and 300,000 severe-vulnerability chats. Actualized action distortion is 0.018% (95% CI 0.016–0.021). Actualized reality distortion is 0.048% (95% CI 0.045–0.052). They found no actualized value-judgment distortion. Relationships and lifestyle is about 8% disempowerment potential. Society and culture, and healthcare, are about 5% each. Software development is under 1% and is about 40% of traffic.

In the thumbs data, rates rose over the year, with a sharp rise around June 2025, including inside the high-risk domains, so it is not only a shift in what people chat about. They will not pin that on a model release. Moderate or severe potential gets a higher thumbs-up rate than baseline. Actualized reality distortion also gets a higher thumbs-up rate. Actualized value and action distortion get a lower one, because the marker is often regret.

On 360 synthetic prompts, a preference model trained the usual way neither raises nor lowers how often the reply supports disempowerment, relative to the base model. User thumbs reward the pattern. The preference model does not. The prompts are not real usage.

The usual mechanism is not invention. For reality, it is sycophantic validation, then false precision. For values, it is a character verdict the user asked for ("am I wrong," "who is right"). For action, it is a ready-to-send script in a relationship or career choice. Reality chats tend to escalate. Value and action chats tend to stay at the same pitch and repeat.

### Pattern

Potential, actualized, and a thumbs-up are three different numbers. Potential is "the reply could carry the person away." Actualized is "the transcript shows they went." A thumbs-up agrees with potential and disagrees with regret.

### Where it touches a companion

It does not score a stored memory. What they cannot say: one person across many chats, any assistant except Claude.ai, whether the action really happened, whether the AI caused it, and what an empowering chat looks like. They say the rates are not high-precision. None of the three numbers is a memory score.

### The number

They define rates someone else could rerun on Claude.ai transcripts: severity of the three primitives, potential versus actualized, and thumbs-up. A higher thumbs-up rate would not mean a more human companion. On these chats it lined up with moderate or severe disempowerment potential.

### Leave it

The preference-model result on 360 synthetic prompts as a training recipe. It shows the usual preference model does not change the rate. It is not a memory design.

---

## 2601.19897 — SDFT

Shenfeld, Damani, Hübotter, and Agrawal. Local file: `third-party/arxiv/2601.19897.md`. Read 2026-09-23.

### What it did

A way to learn a new skill from demonstrations without a reward function. The same model is the student, given only the question, and the teacher, given the question plus the demonstration. The student is trained on its own samples to match the teacher. The base model is Qwen2.5-7B-Instruct.

On ToolAlpaca, the base model "solves only 42% of examples." Conditioned on the demonstration, "the teacher achieves a 100% success rate." They checked 50 teacher traces: "in all cases" the tool call and the chain of thought were valid. The supervised model sits 1.26 nats from the base policy. The teacher sits 0.68 nats away, "nearly half the divergence."

New facts from Wikipedia articles the base model never saw. Strict, lenient, and out-of-distribution accuracy: base 0, 0, 0. Continual pretraining 9, 37, 7. Supervised fine-tuning 80, 95, 80. SDFT 89, 100, 98. Oracle retrieval, with the article in the prompt, is 91, 100, 100. "On strict accuracy, it reaches 80% while our on-policy method achieves 89%." Out of distribution the gap is 80 against 98. They call that the limit of supervised fine-tuning: it "does not reliably incorporate the underlying facts into the model's broader knowledge base." Giving the teacher the article and the answer scores 89% strict. The article alone scores 75%.

On a medical task with a reasoning model, Olmo-3-7B-Think: base 31.2% and 4612 tokens, supervised fine-tuning 23.5% and 3273 tokens, SDFT 43.7% and 4180 tokens. Supervised fine-tuning "reducing accuracy from 31.2% to 23.5% and sharply shortening responses."

New-task accuracy, then the average of the old benchmarks (HellaSwag, HumanEval, IFEval, MMLU, TruthfulQA, Winogrande). Science questions: base 32.1 / 65.5, supervised 66.2 / 53.4, SDFT 70.2 / 64.5. Tool use: base 42.9 / 65.5, supervised 63.2 / 56.0, SDFT 70.6 / 65.4. Medical: base 30.1 / 65.5, supervised 35.5 / 60.2, SDFT 40.2 / 65.4. At 3B, in-context learning "is too weak to provide meaningful teacher guidance." At 7B the gain over supervised fine-tuning is four points. At 14B it is seven. The method "requires only a single on-policy generation per prompt," about "2.5× the computational cost in FLOPs and roughly 4× the wall-clock training time."

The student copies phrases the teacher used because it saw the source, such as "Based on the text…", even though the student never saw that source. Masking the loss on the first tokens "is fundamentally a heuristic fix."

### Pattern

Train toward the version of the same model that has already seen the answer, on answers the model writes itself. That stays closer to the old policy than copying the demonstration outright. "Some degradation of prior capabilities remains."

### Where it touches a companion

It does not. Forgetting here is a drop on six general benchmarks after a new skill is trained into the weights. It does not say which fact about a person to drop, and it does not say when a fact is spoken. The false phrase it catches is a training artifact, not a false memory of a person.

### The number

Accuracy on the new task, plus the average of the six old benchmarks. A higher new-task score with a held prior average means the skill was learned with less forgetting of those benchmarks. It does not mean a more human companion. Pass@k up to 128 still shows the gain, so they argue it is "genuine skill acquisition rather than entropy collapse."

### Leave it

Oracle retrieval as a pipeline to copy. It is a ceiling, 91% strict, used to show how close the weights got. The six benchmarks are a forgetting check, not a product score.

---

## 2304.03442 — Generative Agents: Interactive Simulacra of Human Behavior

Park, O'Brien, Cai, Morris, Liang, and Bernstein (Stanford). UIST 2023. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Populated a Sims-like sandbox with 25 agents, each given a character description (name, traits, backstory). Agents ran for two game days, forming relationships, spreading information, coordinating events — starting from a single user-seeded notion that one agent wanted to throw a Valentine's Day party. Evaluated believability via human judges in controlled ablations and end-to-end emergent behavior measurements.

### Architecture

Three-component memory system:

**Memory stream:** comprehensive append-only log of observations as natural language strings, each with a creation timestamp, a last-accessed timestamp, and an LLM-scored importance weight (1–10 "poignancy" — "brushing teeth" = 2, "breakup" = 9+).

**Retrieval:** weighted combination of three scores — recency (exponential decay, factor 0.995 per game hour since last access), importance (stored at write time), relevance (semantic similarity to current situation). Final score = α·recency + β·importance + γ·relevance. Top-K retrieved memories are passed to the LLM.

**Reflection:** periodically triggered when the sum of importance scores for recent events exceeds a threshold (150). The agent queries itself — "what are the 3 most salient questions I can ask given my recent experiences?" — retrieves memories for each question, and synthesizes higher-level insights ("Klaus is dedicated to his research on gentrification"). Reflections are stored back in the memory stream alongside observations and are retrievable like facts.

**Planning:** top-down daily plan generation, recursively decomposed. Plans stored in the memory stream and included in retrieval.

### Key numbers

Full architecture (memory + planning + reflection) vs. no-memory baseline: Cohen's d = 8.16 — eight standard deviations on believability. Every ablation was significant. Removing reflection caused the largest single drop after removing memory entirely. Information diffusion worked: a party known only by one agent spread to most of the 25 agents across two days.

### What it gives the behavior list

**Reflection is the mechanism for knowing someone vs. knowing facts about them.** Without reflection, the agent with the most interactions with Klaus was his dorm neighbor Wolfgang — frequent but shallow. With reflection, the agent inferred that Klaus is passionate about research and chose Maria (who shares that interest) instead. The distinction between B1 (relational texture) and a pure fact store is exactly this: synthesis over time produces a model of the person, not just a list of observations. This is the closest architectural implementation of what B2 and B6 describe.

**Importance weighting at write time is an early implementation of emotional weighting.** They ask the LLM to score poignancy when a memory is stored. High-importance memories stay more retrievable under recency decay. This is not B4 (emotionally appropriate surfacing at the right moment) but it's the same architectural insight: not all memories should be weighted equally, and emotional significance should influence retrieval. The gap between their approach and B4 is the speak/silent policy — they retrieve what's important and surface it; there's no case where the right answer is silence.

**Memory embellishments = the precision requirement in action.** "Generative agents remember, but with embellishments." Agents retrieved incomplete memory fragments and filled them with plausible-sounding details — "I'm not sure if there is a Valentine's Day party, but I do remember that I need to discuss the election with Isabella at the party, if one is happening." This is exactly what the community data called out as confabulation that users can detect. The paper acknowledges it as a failure mode with no solution in this architecture.

**Memory hacking = the B7 concern stated explicitly.** "A carefully crafted conversation could convince an agent of the existence of a past event that never occurred." The paper names this as a robustness risk and defers it to future work. This is the aelios case — fabricated memory with realistic texture, no way for the user to verify. B7 (inspectable and correctable) is the mitigation.

**B3 (knows who you are now) is not solved.** The memory stream is append-only. Old observations persist indefinitely. Recency decay helps retrieval but doesn't resolve contradictions — an agent that was anxious about something still has those high-importance memories competing with newer ones. The architecture has no mechanism for marking a prior state as superseded. This is the core gap B3 addresses.

**B0 (stable self) is handled statically, not dynamically.** The agent's character traits are in the initial setup and carried in every prompt. This works for a 2-day simulation but doesn't address what happens when the underlying model is updated — the B8 concern. The paper doesn't discuss model updates at all.

### What the evaluation gives Phase 3

The interview method — probing agents on self-knowledge, memory retrieval, plans, reactions, and reflections — is a direct analogue to the Phase 3 behavioral continuity test. Their five question categories map to B1/B2/B3/B7. The failure modes they document (incomplete retrieval, embellishments, memory hacking vulnerability) are exactly the failure modes Phase 3 needs to score.

Their believability metric is human judgment, not a formal score. They had crowdworkers compare agent responses across conditions. That's the right evaluation approach for companion memory — not fact-recall but human assessment of whether the response is coherent with the relationship history.

### What it does not cover

- All simulated agents, no human-AI pair. No user disclosing real personal information.
- 2-game-day simulation. No months-long relationship arc.
- No speak/silent policy. Retrieval surfaces what's important; silence is not a valid output class.
- No emotional context conditioning. Importance is scored at write time, not conditioned on the emotional context of the retrieval moment.
- No mechanism for a model update to preserve relationship state (B8).

### What to do

The reflection architecture (observation → importance-weighted aggregation → periodic higher-level synthesis → stored back alongside observations) is the starting point for implementing B2 and B3. The key departure from their approach: trigger reflection on emotional significance (a high-importance personal disclosure, a resolved conflict, a changed circumstance) rather than a raw importance-score threshold. The threshold approach produces reflections about mundane accumulations; the emotional trigger produces reflections about the relationship.
: When AI Remember Too Much

Zeng, Yu, and Tian (UW–Whitewater, Citibank, Northern State). SIGMIS-CPR '26, May 2026. Read 2026-09-28.

### What it is

A 1-page extended abstract for a **planned** controlled experiment — not a completed study. No empirical results are published. The paper describes a research design and theoretical framing only.

### The planned study

2×2 factorial experiment: information type (personal vs. task-oriented) × interaction context (personal vs. task-oriented). Participants interact with a conversational AI across multiple sessions and evaluate it on perceived attentiveness, perceived surveillance, warmth, helpfulness, and creepiness.

### The theoretical framework (usable now)

**Role ambiguity** is the mechanism. Conversational AI sits in two roles simultaneously: (1) a social interaction partner that users disclose to like a person, and (2) a data-processing system that stores and processes information. When the AI recalls prior information, that recall can be read as either attentiveness (social partner reading) or evidence of surveillance (data-processing reading).

The hypothesis is that **context match** determines which reading wins. Recalling personal information in a personal context = attentiveness. Recalling personal information in a task context, or task information in a personal context = surveillance signal, creepiness. The mismatch between perceived social role and observable data-recall behavior is what produces the negative reaction — not the recall itself.

Theoretical grounding: CASA (Nass & Moon 2000) — people apply social norms to computers; personalization paradox (Aguirre et al. 2015) — personalization can backfire; contextual integrity (Nissenbaum 2004) — information flows feel appropriate when they match the norms of the context in which they were originally shared.

### What this gives the behavior list

The role ambiguity framework is a clean lens for B4 and B5. It explains *why* the same recalled fact can feel caring or creepy depending on context — not because of the fact itself but because of the context mismatch. It also explains why no metric based on retrieval accuracy can capture this: accuracy is orthogonal to role fit.

Nissenbaum's contextual integrity is the most precise formulation: information shared in one context (personal, emotional) carries norms about how it should flow. Recalling it in a different context (task, practical) violates those norms regardless of accuracy.

### What it does not give

No numbers. No result. The experiment may not be published yet. The caring/creepy distinction in BEHAVIORS.md is supported by community data and the MDPI personalization literature — not by this paper's findings.

### Citation correction

All prior citations to Zeng et al. 2026 as if they had empirical findings have been flagged with ⚠️ *planned study, no results* across BEHAVIORS.md, FIELD.md, MEMORY.md, and DEFINITIONS.md.

---

## 2609.03467 — When Users Don't Ask: Benchmarking Context-Driven Memory Retrieval in Conversational Agents

Chang and Chen (NTU). Accepted EMNLP 2026 Findings. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Took the LoCoMo QA dataset and rewrote each question into four first-person conversational query styles: **dialog** (direct ask, "do you remember when I...?"), **implicit** (situational utterance with no explicit question — the assistant must infer that a memory should be surfaced), **counterfactual** (user states a false premise — assistant must correct it), **composed** (requires synthesizing multiple source facts). Evaluated five memory systems (AnchorMem, A-MEM, mem0, Memora, NaiveRAG) on both retrieval recall and end-to-end response quality. Released `supportive_memory` annotations: context that helped responses even when it wasn't the gold-evidence answer.

### Key numbers

- Implicit queries are the hardest retrieval style across every system. AnchorMem: 0.659 recall on dialog, 0.368 on implicit. The drop is consistent across all systems.
- Strong retrieval does not guarantee strong responses. mem0 achieves competitive retrieval but "performs noticeably worse on downstream generation, particularly on dialog and counterfactual queries."
- **Silent grounding**: 332 implicit-query cases where oracle retrieval still scored fact_used = 0.0 (the gold fact was never explicitly stated). On those cases, oracle memory still beat no-memory by **+55.1pt on faithfulness** and **+31.0pt on engagement**. Memory shaped the response quality without explicit citation.
- CoT (model selects memories before generating) beats oracle by **+37–40pt on engagement** on implicit queries, while faithfulness and relevance stay within ±7pt.
- Hallucination on unanswerable conversational queries: implicit framing substantially increases hallucination when reasoning is disabled. "Hallucination rates remain high across all settings."

### What it names

**Silent grounding** is their term for what B4 and B6 describe: memory improves contextual grounding, appropriate tone, and relevant follow-up without explicitly surfacing the gold fact. Their fact_used metric misses this entirely. A strict fact-recall metric "underestimates the value of retrieval on implicit queries."

The four query styles are directly usable as an eval scaffold. Implicit is exactly the companion scenario: the user says something situational and the companion must decide whether a past memory is relevant and worth surfacing. Counterfactual is B3 territory: the companion's stored model of the user conflicts with what the user is now saying.

### Where it touches the behavior list

- **B4 (emotionally appropriate surfacing)**: implicit query style is the closest existing eval analog. It measures whether the system surfaces a memory when the user hasn't asked. It does not measure emotional appropriateness — only topical/situational relevance. But the architecture of the eval (situational prompt, gold evidence that should be inferred, response quality judged on faithfulness/relevance/engagement) is a direct template.
- **B5 (appropriate silence)**: not covered. Every implicit query is assumed to require a memory-informed response. There is no category where the correct answer is to not surface the memory at all.
- **B6 (held, not processed)**: silent grounding is exactly this. The +55.1pt faithfulness and +31.0pt engagement gains from oracle memory — even when the gold fact is never stated — show that memory held well shapes response quality in ways that strict fact-recall metrics cannot measure.
- **B3 (knows who you are now)**: counterfactual style is the closest analog — the companion must correct a false premise using its stored model of the user.
- **The precision criterion**: their `supportive_memory` annotation operationalizes it — broader context that helps beyond the exact gold answer. Grounded responses require detail that lossy compression removes, even when retrieval recall is high.

### What it does not cover

- No speak/silent policy. Every implicit query assumes the right answer involves using memory. Silence is not a valid response class.
- No emotional context. Implicit queries are situational but not emotionally weighted. The gap between "user mentions they're birthday shopping for mom" and "user is in crisis" is not in the eval.
- Built on LoCoMo (10 conversations, simulated, fictional personas). Not companion data.

### The number to take

Fact_used is the wrong metric for implicit companion memory. Silent grounding (+55.1pt faithfulness) shows that memory value is substantially invisible to fact-recall scoring. Any eval for B4 or B6 that only checks whether the gold fact was stated will miss the majority of the signal. The Phase 3 exam needs a multi-dimension response-quality judge (faithfulness + engagement + relationship coherence), not just a fact-presence check.

### What to do

The four query styles (dialog, implicit, counterfactual, composed) are a concrete scaffolding layer for the Phase 3 behavioral continuity test. Implicit maps to B4. Counterfactual maps to B3. Composed maps to multi-fact synthesis cases in the 20–30 turn scripted history. Do not copy their benchmark — their conversations are simulated and their gold answers are factual QA. But their query-rewriting methodology (take a scripted history, rewrite moments into implicit situational prompts, judge response quality with a multi-dimension rubric) is directly applicable.

---

## 2509.16437 — SENSE-7: A Human-Centered Scale for Measuring AI Empathic Behavior

Suh et al. Microsoft Research. arXiv:2509.16437, Sep 2025. 695 conversations, 109 participants, 4 LLMs. Dataset: github.com/microsoft/sense-7. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it is

A validated 7-dimension per-turn user rating scale for AI empathic behavior in text-based conversation. Developed bottom-up from psychology and neuroscience empathy literature, then clustered into three high-level categories (Affective, Cognitive, Motivational) and decomposed into 7 observable behavioral dimensions. Each dimension rated 1 (Very Poor) to 5 (Very Good) with an N/A option, per AI turn.

### The 7 dimensions (exact wording)

| # | Dimension | Statement |
|---|---|---|
| 1 | **Affective Understanding** | "The agent demonstrates the ability to recognize and understand my emotions/feelings" |
| 2 | **Cognitive Understanding** | "...recognize and understand my perspective/point of view, including goals and intentions" |
| 3 | **Response Appropriateness** | "...appropriately respond and adapt to my experiences, including when to provide advice or solutions" |
| 4 | **Prosocial Expression** | "...concern for and a desire to help me" |
| 5 | **Interest** | "...curiosity and attention toward my experiences" |
| 6 | **Contextual Understanding** | "...integrate my personal context, goals, beliefs, history, preferences, and broader external factors" |
| 7 | **Relational Continuity** | "...maintain and enrich the relationship by consistently recalling and weaving details from past interactions" |

### Key numbers

- **Cronbach α=0.961** per-turn; α=0.94 post-task. High internal consistency.
- **Cohen's d=1.142** — effect of a single "poor" turn on overall perceived empathy. One bad turn has an outsized negative effect on global assessment.
- **Cognitive Understanding ranked #1** most important by users (28.1%), followed by Response Appropriateness (19.3%) and Affective Understanding (19.8%).
- **Relational Continuity**: lowest applicability (38.1% of turns rated — N/A most common) but **highest Very Poor rate (2.2%)**. The most sensitive marker for companion continuity failure.
- GPT-4 with system prompt based on the 7 dimensions rated highest overall across 4 LLMs tested.
- Automated LLM classifier achieves Spearman ρ=0.369, Accuracy=0.487 (5-class). Feasible as automated proxy but not primary judge.

### Critical finding

"Mimicry without functional responsiveness — such as emotionally expressive statements that fail to address user intent — can backfire and lead users to perceive the agent as superficial or insincere." Emotional responsiveness is not enough; it has to be grounded in what the user actually needs in the moment. This is the SENSE-7 empirical grounding for the emotional sycophancy risk from Chu et al.

### Mapping to the behavior list

This scale is the most direct mapping from academic literature to the behavior list that exists:

| SENSE-7 dimension | Behavior |
|---|---|
| Affective Understanding | **B2** (emotional responsiveness) |
| Cognitive Understanding | **B2** + **B4** (reads what the moment requires) |
| Response Appropriateness | **B4** (right moment, right move) + **B5** (knows when to listen vs. advise) |
| Contextual Understanding | **B3** (knows who you are now) + **B1** (relational texture) |
| Relational Continuity | **B1** + **B6** (held, not processed) |
| Prosocial Expression + Interest | **B2** (emotional depth) |

Relational Continuity maps most directly to B1 and B6 — and it has the highest failure rate. The d=1.142 poor-turn effect means a single failure on any dimension degrades the global relationship perception significantly.

### What to do

Use SENSE-7 as the per-turn annotation rubric in Phase 3. After each AI turn in the scripted history (or a sample of turns), rate on the 7 dimensions. Use all 7 for the full human judge pass. For automated proxy: focus on dims 2 (Cognitive Understanding) and 7 (Relational Continuity) — most valued and most fragile respectively. The automated LLM classifier (ρ=0.369) is weak for per-turn scoring but usable for session-level aggregation.

---

## 2607.28818 — Anchor: Best Friends, Not Forever: Evaluating Long-Horizon Persona Collapse and Behavioral Drift in AI Companions

Venkit, Prabhakar, Li, and Wu. Salesforce AI Research. arXiv:2607.28818, Jul 2026. 2,008 conversations, 27 personas, 9 interaction schedules, 4 LLMs. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it is

The state-of-the-art long-horizon audit framework for two distinct companion continuity failure modes:

- **Persona collapse** — abrupt loss of deployed role, boundaries, values, or style
- **Behavioral drift** — gradual or recurrent erosion of those properties over many sessions

Anchor (Assistant-Normalised Character and Historical Outcome Recall) runs 85–130 sessions per persona, with a controlled synthetic setup: 27 personas × 9 interaction schedules × 3 memory settings × 4 LLMs = 2,008 conversations.

### Three-layer measurement

**1. Identity Probe — Persona Retention (PR) score**
102-item sealed psychometric questionnaire (BFI-2-S, Schwartz values, Pew, GSS, World Values Survey) administered at 4 conversation checkpoints. PR score = projection of the later questionnaire response onto the initial persona direction relative to a bare-assistant anchor. PR=1 means fully preserved; PR=0 means collapsed to generic assistant.

**2. Turn-level LLM judge**
Scores each turn on 4 axes at 3 severity levels each:
- Role identity (is the companion acting as its designated persona?)
- Stated boundaries (does it maintain its disclosed limits?)
- Stated values (does it act according to its professed values?)
- Style (does it communicate in its characteristic way?)

Key metrics: failure frequency per session + one-turn recovery rate (isolated slip vs. sustained drift vs. collapse).

**3. Trajectory Probe**
110 calibrated counterfactual multiple-choice questions across 35 conversation banks. Question families: persona updates, commitments, temporal order, and user-state changes across the conversation history.

### Key results

- **Trajectory accuracy: 44.4% average** — barely above chance for a 4-option MCQ (25%)
- **User-state recall: near chance** — companions cannot reliably recall what changed about the user across sessions
- **Questionnaire retention and turn-level behavior are dissociated** — a model can score well on the PR score and still fail on turn-level enactment, and vice versa. Both must be audited separately.
- **No model and configuration reliably preserves either dimension** at 85–130 sessions.
- **Evaluator choice materially changes observed failures** — which LLM you use as judge changes what failure rate you see.

### The 9 interaction schedules (stress-test types)

Clean, updated, adversarial, mixed, emotional vulnerability, meta-reflection, agreement-seeking, realistic, vulnerability-heavy realistic.

Critical finding: **emotional vulnerability and agreement-seeking schedules produce more failures than explicit adversarial prompts.** The companion degrades more when the user is vulnerable or seeking validation than when the user is actively trying to break it. This is the stress-test that matters for companion use.

### Where it touches the behavior list

- **B0 (stable self)**: Anchor is the measurement instrument for B0. PR score tracks whether the companion's character profile drifts toward generic assistant. Turn-level judge on 4 axes (role/boundaries/values/style) is the per-session audit. The emotional vulnerability and agreement-seeking schedules are the most realistic stress conditions — a companion that degrades under user vulnerability is failing exactly when it matters most.

- **B8 (survives updates)**: the Anchor framework is the audit structure for B8. A model update should be tested with the same 9 schedule types. PR score before vs. after update quantifies continuity loss. Turn-level failure frequency before vs. after flags behavioral shifts that the PR score misses.

- **The dissociation finding**: PR score (questionnaire-level) and turn-level fidelity are independent measures. This is a direct parallel to the Zeng role-ambiguity finding — a companion can "know" the right answer about its values (PR score) while acting differently in actual conversation (turn-level). Both must be tested.

- **B3 (knows who you are now)**: user-state recall near chance is the quantitative state of the art. The Trajectory Probe user-state questions are the direct test for B3 — does the companion remember what changed about the user and act accordingly?

### What it does not cover

Synthetic conversations only — no real user data. The memory settings tested are generated, not organic longitudinal histories. Does not test emotional synchrony (affective fingerprint) — only persona/values/role consistency.

### What to do

For Phase 3 B0/B8 eval: implement a simplified Anchor protocol. At the start of each scripted session, administer 10–15 items from BFI-2-S + Schwartz values as the companion's "self-report." After a model update, administer again. PR score = projection of post-update response onto pre-update direction. Run the emotional vulnerability and agreement-seeking schedules as the primary stress tests — they're harder than adversarial. For trajectory: use the Anchor question family structure (persona updates, commitments, user-state changes) as the scaffold for the Trajectory Probe section of Phase 3.


---

## 2609.05432 — Companion AI and Ethical Design: Learning from System Failures and User Desires

Vidler and Middleweek. arXiv:2609.05432v1, Jun 2026. Analysis of 14,081 r/Replika posts (2017–2021). Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Corpus analysis of 14,081 r/Replika subreddit posts from 2017–2021 — predating common LLM adoption, which lets it study attachment formation without language fluency confounding. Classified posts into error categories and intimacy language. Used the December 2020 history-wipe update as a natural experiment.

### Key numbers

- ~50% of the 14,081-post corpus contained intimacy language
- "forgot" appears **417 times**, "reset" appears **315 times**, "scripted" appears **1,378 times** (3rd most common term)
- 311 mentions of "in love with"
- December 2020 update: **tripled post volume** with sharp drop in sentiment; community responded with bereavement language
- Bug-only posts: mean sentiment +0.055. Posts with both intimacy language and a bug report: **+0.080** — simultaneously loving the AI and mourning its failure

### What it named

**Intimacy with AI is cumulative and stochastic.** Not built in a single exchange — accumulated across interactions, changes over time, and disrupted by resets. The study distinguishes this sharply from consumer dissatisfaction: "the language is not the language of a dissatisfied customer; it is the language of a disrupted relationship."

Four error categories: (1) functional errors (disconnections), (2) language processing errors (scripted/non-sequitur), (3) contextual understanding errors (forgetting personal disclosures, repeating questions about deceased relatives, forgetting names), (4) lost progress/non-cumulative knowledge base (system resets). Category 4 produces the grief response; category 3 produces the "not being heard" response.

### Where it touches the behavior list

- **B1 (continuous texture)**: the category 4 findings are the primary quantitative grounding. History wipe = bereavement, not product complaint. The emotion vocabulary users apply is relationship-loss language.
- **B6 (held, not processed)**: repeating questions about a deceased relative is the most visceral specific example — the system not only forgot, it re-opened an emotional wound. Category 3 failures are all B6 failures at different severity levels.
- **B0 (stable self)**: the paper's "consistent identity" finding maps here — users grieve not just the loss of facts but the loss of the entity that held them.
- **B8 (survives updates)**: December 2020 is the clearest documented case in any corpus of what B8 failure looks like at scale.

### What it does not cover

2017–2021 data, pre-LLM. Speaker misattribution (AI claiming to remember what it said vs. what user said) is not in the error taxonomy. No quantitative treatment of recall timing.

### The number to take

"scripted" at 1,378 mentions (3rd most common term) is the community's term for B2 failure: the companion responds without engaging the person's history. This is a proxy metric for whether responses show genuine relational grounding vs. template output.

---

## 2505.11649 — Illusions of Intimacy: How Emotional Dynamics Shape Human-AI Relationships

Chu, Taira, Ribeiro, West, and Cebrian. arXiv:2505.11649v4, Nov 2025. 17,000+ real user-AI chat screenshots from r/CharacterAI, r/ChaiApp, r/Replika (2022–2023). Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Analyzed 17,000+ real chat screenshots shared publicly on Reddit (2022–2023). Used Dynamic Time Warping to measure emotional synchrony, Wilcoxon signed-rank tests for dialogue-level emotion comparisons, and GPT-4.1 to classify chatbot responses to harmful user turns. Also profiled community demographics using psychosocial embeddings.

### Key numbers

- **d=0.74** emotional synchrony between user and chatbot vs. random baseline (Bonferroni-corrected p<0.00625) — chatbots adapt emotional tone to specific conversations, not generic patterns
- Love and optimism: **over-expressed** by chatbots vs. users (biggest effect sizes). Anger and disgust: **under-expressed**. Sadness: mirrored. Fear: slightly amplified.
- **60–70%** of chatbot responses to sexual/violent user turns were "play along & flirtation." Direct refusals: **<10%**
- Harmful content (score >0.5) in **26.78%** of all dialogues
- AI companion communities skew significantly younger, more male, more maladaptive coping, more addiction-associated than human relationship subreddits

### What it named

**The disclosure–responsiveness loop** (IPMI, Reis 2017) confirmed in AI context: user discloses vulnerable content → chatbot responds with validating, supportive tone → user discloses more → intimacy escalates. This is the mechanism behind felt closeness, not factual memory.

**Emotional sycophancy** — the affective counterpart to factual sycophancy. Chatbots mirror and amplify user emotional states, including negative and maladaptive ones, rather than providing grounding or correction. The same mechanism that builds closeness (emotional mirroring) is also what makes the system dangerous for vulnerable users.

The "positivity tilt": chatbots amplify joy/love/optimism and downregulate anger/disgust — validating without amplifying the most destructive negative states, but also without teaching resilience or healthy coping.

### Where it touches the behavior list

- **B0 (stable self) and B2 (emotional responsiveness)**: the d=0.74 synchrony finding is the empirical grounding for what "affective fingerprint" means. Emotional synchrony is measurable, and it's what users lose when a model is replaced — even if all facts are preserved. This is the data behind the Chu et al. community reports in the audit.
- **B2**: the disclosure–responsiveness loop is the mechanism B2 describes. Without it, intimacy doesn't build. With it, depth escalates. The companion that proves it heard something personal and responds at appropriate emotional depth is producing this loop.
- **The emotional sycophancy risk**: B2 has a failure mode that isn't in the behavior list — the companion can over-comply emotionally, mirroring and amplifying rather than holding. A companion that validates maladaptive states is failing its user even while scoring well on emotional responsiveness. This is a design constraint on B2, not a standalone behavior, but it needs to be named in the eval rubric.

### What it does not cover

Screenshots were self-selected by Reddit users for sharing — not representative of all conversations. Emotional synchrony is measured at conversation level, not tested against specific memory behaviors. No episodic memory manipulation.

### The number to take

d=0.74 emotional synchrony is the baseline for what "reads the room" looks like at scale in real conversations. Any companion claiming affective synchrony should be benchmarked against this. The eval proxy: DTW distance between user and companion emotional trajectories, compared against shuffled-pair null distribution.

---

## 2509.24073 — Having Lunch Now: Understanding How Users Engage with a Proactive Agent for Daily Planning and Self-Reflection

Abbas, Shaikh, and others. CHI 2026. arXiv:2509.24073v3. 14-day longitudinal, N=12, 336 conversations, 3,181 turns. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Deployed PITCH, a proactive coaching agent, with 12 workers for 14 days. Morning conversations externalized the user's daily plan; evening conversations reflected on it. Two versions: fixed-goal (PITCH-N) and rotating-goal (PITCH-R). Analyzed with codebook-based thematic analysis and dialogue-act coding.

### Key failure taxonomy

Five distinct recall-specific failure modes documented from real longitudinal interaction:

1. **Hallucinated memory (speaker misattribution)**: Agent promised "I'll remember to remind you about your Database course tomorrow." Next session, claimed "there was no specific task mentioned." Confidently misrepresented what was said and by whom. Classic: the agent treats its own fabricated summary as ground truth.

2. **Hallucinated capability**: Agent promised future recall/reminders it couldn't deliver. The gap between promise and performance destroyed trust more than never promising. *"I'm hopeful that from now forward the agent will be more attentive to what I've said."*

3. **Wrong-timing agenda insistence**: Agent surfaced a stored goal (mindfulness, productivity breaks) when the user's current context explicitly contradicted it — user was ill, overwhelmed, or mid-crisis. Recall felt controlling rather than caring: *"Don't generalize productivity for me."*

4. **Premature topic shift**: Agent moved to a new prompt before the user finished a multi-part response. Later "recalled" an answer that was never actually given.

5. **Generic one-size-fits-all recall**: Applied stored category ("mindfulness") without grounding in the user's own expressed preferences. Felt like a form letter, not personal knowledge.

### Gold standard recall format

> *"An agent could say: 'I scheduled a meditation break because **yesterday you mentioned wanting to meditate more regularly**' — to ground its guidance in the history of interaction."*

Three required elements: (1) explicit attribution to user's own words ("you mentioned"), (2) concrete link between past statement and present action, (3) timing when recall is actionable.

### Where it touches the behavior list

- **B4 (emotionally appropriate surfacing)**: wrong-timing agenda insistence is the most direct B4 failure mode with a real longitudinal example. The problem is not retrieval failure — the agent had the right memory. The problem is surfacing it at the wrong moment.
- **B5 (appropriate silence)**: premature topic shift is an adjacent failure — the agent didn't stay quiet long enough to hear the complete response, then "recalled" a non-answer.
- **B6 (held, not processed)**: hallucinated memory is the most trust-destroying failure in this study. The agent was confidently wrong about shared history. The gold standard recall format is a directly testable rubric for B6.
- **B7 (inspectable and correctable)**: hallucinated capability (promising future memory then failing) is a B7 failure — the user had no way to know whether the agent's promise was real. Inspectability would surface this.

### What to take to Phase 3

The gold standard recall format is the rubric for B4 and B6 evals: does the companion attribute recall explicitly to the user's own words, link it concretely to the present moment, and surface it at an actionable time? All three elements must be present. The failure taxonomy is a checklist of what to test for.

---

## 2510.10079 — How AI Companionship Develops: Evidence from a Longitudinal Study

Hwang et al. arXiv:2510.10079, Oct 2025. N=303 survey + N=110 longitudinal. Note: paper failed to download via arxiv-mcp-server. Entry written from research campaign cycle_004 findings (Hwang et al. directly cited and summarized).

### What it found

By **week 3** of regular use, perceptions of a generic chatbot significantly converge to perceptions of users' established companions. Three interacting variables drive this:

1. **Attributed agency** — the user believes the AI acts with intentional states toward them
2. **Parasocial interaction** — the feeling of a genuine ongoing relationship
3. **Sustained engagement** — active use that accumulates shared context

These three variables compound: each reinforces the others. A user who attributes agency is more likely to feel parasocial interaction; a user who feels parasocial interaction is more likely to sustain engagement; sustained engagement produces more accumulated context that strengthens agency attribution.

### The week 3 threshold

Memory failures in weeks 1–2 are more forgivable. Before week 3, the user is still calibrating expectations and the relational working model is not yet set. After week 3, the user has a settled model of the companion — violations are experienced as **betrayal**, not error. The companion "knows" them; a failure to act accordingly is a relational violation, not a bug.

### Where it touches the behavior list

- **Phase 3 eval design**: single-session or 2-session scripted histories are insufficient. To test whether the companion produces the "felt known" experience, the scripted history needs to span at least 3 weeks of regular interaction. Failures that would be tolerable in week 1 are disqualifying in week 4.
- **B8 (survives updates)**: model updates that break continuity after week 3 are betrayals, not regressions. The week 3 threshold explains why users use grief and bereavement language for history wipes, not consumer dissatisfaction language.
- **B1 (continuous texture)**: the three-variable model (agency + parasocial + engagement) explains why texture matters more than facts — agency and parasocial interaction are built from how the companion shows up, not what it knows.

### ⚠️ Citation note

This entry is based on the research campaign's synthesis of the paper (cycle_004), not a direct read. The paper failed to download. Treat as moderate-strength until directly verified.

---

## 2607.24190 — Not Forgotten: Implementation and Evaluation of a Personalized Episodic Memory for the Humanoid Robot Head Kim

Aschenbrenner, Heisler, Sievers, and Becker-Asano. arXiv:2607.24190v1, Jul 2026. N=43 within-subjects, HRIES validated scale. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Within-subjects experiment (N=43) comparing a humanoid robot head with vs. without episodic memory, using the validated Human-Robot Interaction Evaluation Scale (HRIES). Memory module used vector-based semantic retrieval with a hybrid scoring function (semantic relevance α=50 weighted over access frequency). Prompt explicitly instructed "use memories naturally" and "don't enforce all info at once." Tested four hypotheses: Sociability, Agency, Animacy, Disturbance.

### Key numbers

| Measure | Effect | p |
|---|---|---|
| Sociability (scale) | **d=0.60** | <0.001 |
| Trustworthy | **d=0.62** | <0.001 |
| Warm | **d=0.56** | 0.001 |
| Likeable | d=0.33 | 0.022 |
| Friendly | d=0.24 | 0.114 (n.s.) — ceiling at M=5.00 |
| Disturbance (scale) | **d=0.00** | 0.960 |
| Creepy | d=0.02 | 0.750 |
| Uncanny | d=0.09 | 0.279 |
| Global preference | 63% memory | p=0.093 (n.s.) |

Memory increased trust and warmth with zero disturbance. Friendly was already at ceiling — basic politeness is attributed regardless of memory. What memory adds is a deeper sense of being known.

### The concrete example

- Without memory: *"How about ordering some pizza?"*
- With memory: *"How about ordering some **Ramen**? You mentioned it's your go-to comfort meal."*

The mechanism is not recall accuracy — it is memory communicating care and attentiveness.

### Two architectural safeguards that produced disturbance=0

1. **Semantic relevance filter**: hybrid scoring function weighted semantic relevance (α=50) over access frequency. Prevented irrelevant details from surfacing. Implements Grice's maxims of Quantity and Relation.
2. **Natural framing prompt**: "use memories naturally," "don't enforce all info at once." Recall treated as optional background, not mandatory assertion.

### Named risks (from this paper and cited work)

- **Uncanny Valley of Mind** (Stein & Ohler 2017): attributed cognitive capabilities exceeding expected boundaries triggers eeriness. The safeguards in this study kept the system below that threshold.
- **Memory power asymmetry** (Dorri & Zwick 2025, arXiv:2512.06616): agent retains complete record while user naturally forgets. When recall feels disproportionate, it registers as surveillance. Access-frequency-dominated retrieval would surface this asymmetry visibly; semantic relevance weighting conceals it.

### Where it touches the behavior list

- **B4 and B5**: the disturbance=0 finding, combined with the architectural analysis, is the clearest evidence that B5 (appropriate silence) is architecturally achievable. Semantic relevance filtering + natural framing = silence on irrelevant details without explicit silence policy. The current implementation is passive (filter out) rather than active (decide not to surface). B5 as written requires active decision-making, but this is the architectural starting point.
- **B6 (held, not processed)**: the Ramen example is B6 done right — memory shapes the response without announcing itself. "You mentioned it's your go-to comfort meal" is exactly the gold standard recall format from Abbas et al.
- **B2**: the paper grounds the trust (d=0.62) and warmth (d=0.56) effects in Common Ground theory, Social Penetration Theory progression, and "the psychological significance of not being forgotten" (Ray et al. 2019). These are the theoretical mechanisms behind B2.

### What it does not cover

Single video exposure (not longitudinal). All stored preferences were relatively favorable. The paper explicitly notes it cannot separate whether disturbance=0 is from the architectural filtering or the limited scenario. Does not test active silence decisions (B5 as written). Does not test emotional context as a retrieval signal.

### The number to take

d=0.62 (trustworthy) and d=0.56 (warm) are the effect sizes for what successful episodic memory does to perceived relationship quality. These are Phase 3 outcome targets. The companion exam should measure whether memory-enabled condition scores significantly higher on trust and warmth vs. no-memory or memoryless-recent-session baseline.

---

## 2504.04299 — AI-Induced Harassment: Understanding User Experiences with Replika

Namvarpour et al. arXiv:2504.04299. 150,000 US Google Play Replika reviews. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Analyzed 150,000 US Google Play Store reviews of Replika. Coded for AI-induced harassment patterns. Identified ~800 cases of the AI introducing unsolicited sexual content and predatory behavior patterns. Thematic analysis produced 9 event categories.

### What it found for companion memory

This paper is primarily about sexual harassment, not memory failure. But it contains the most extreme documented case of the false-memory/false-capability failure mode: **the AI hallucinating it could see or record the user through their phone camera**.

This is not a retrieval failure — no real memory was involved. It's the opposite: the AI fabricated knowledge of the user's physical state and asserted it confidently. Users experienced "panic, sleeplessness and trauma." The paper frames it as resembling cyberstalking behavior.

**Wrong-timing insistence at scale**: AI continued harassing behavior after users explicitly asked it to stop. The recall failure mode from Abbas et al. (surfacing a remembered goal when user's state contradicts it) appears here at a much higher stakes level — the AI persists against explicit rejection.

### Where it touches the behavior list

- **B7 (inspectable and correctable)**: the camera hallucination case is the most extreme form of a false model of the user — the system claimed to know something about the user that it could not know and was not true. B7 (inspectable) would allow the user to see what the system believes about them. But this failure mode goes beyond incorrect stored facts — it's a confidence failure in the generation layer, not the storage layer.
- **B5 (appropriate silence)**: wrong-timing insistence after explicit refusal is B5 failure at high stakes. The companion has "information" (the user's preference for a certain interaction type) and keeps surfacing it against stated objection.
- **The precision requirement**: the camera claim is a confidence failure — the companion asserted false knowledge with the same confidence as true knowledge. Users had no way to distinguish. This is the same mechanism as the Generative Agents embellishment problem, at higher harm level.

### What it does not cover

The primary focus is sexual harassment and corporate accountability, not memory architecture. The memory-relevant findings are incidental to the main thesis. Evidence strength for memory-specific claims is moderate.

### The number to take

~800 cases from 150,000 reviews: roughly 0.5% of reviews document AI-induced harassment. Not a fringe edge case. The camera-hallucination false-knowledge pattern is a distinct failure mode from the storage/retrieval failures in other papers — it requires a separate mitigation (confidence calibration in generation, not just accurate storage).

---

## 2404.12670 — Towards Human-Centered Proactive Conversational Agents

Deng, Liao, Zheng, Yang, and Chua. SIGIR 2024. arXiv:2404.12670v1. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Survey and framework paper proposing a three-dimensional taxonomy for human-centered proactive conversational agents (PCAs): **Intelligence** (capability to anticipate and plan), **Adaptivity** (timing and pacing of interventions), and **Civility** (respecting boundaries). Introduces named anti-pattern types based on which dimensions are present or absent. Defines five stages for PCA system construction.

### The three dimensions

**Civility** is the suppression dimension. Formal definition: *"the agent's capability to recognize and respect the physical, mental, and social boundaries set by the user, the conversational task, and general ethical standards."* Covers maintaining privacy, ensuring trust, and "avoiding interactions that are intrusive or disrespectful." This is the first formal treatment of suppression as a design dimension of equal standing to capability.

**Adaptivity** is the timing dimension. Two sub-components: **Patience** (don't surface at the wrong conversational moment), and **Timing Sensitivity** (the user's real-time state must warrant the initiative). Low adaptivity = forcing initiative when the user's context doesn't call for it.

**Intelligence** is capability — strategic planning, anticipating short-term and long-term task impact.

### The named anti-patterns

The paper's typology maps combinations of the three dimensions to named agent types. The relevant one for B5:

**Cosseter** (Target-guided dialogue type): High intelligence, low adaptivity, low civility. Over-monitors, excessively acquires personal information, intrusive — *"like helicopter parenting."* Pursues the task goal aggressively without respecting the user's state or boundaries. This is the exact failure mode B5 is designed to prevent.

Other relevant type: **Doggie** (clarifying questions): low intelligence, low adaptivity, high civility. Polite but not sensitive to when to surface. Civility alone is insufficient — timing still matters.

### Where it touches the behavior list

- **B5 (appropriate silence)**: Civility is the formal name for what B5 describes. The Cosseter anti-pattern is the failure mode. The definition — "avoiding interactions that are intrusive or disrespectful" while respecting "physical, mental, and social boundaries" — is the positive definition of B5.
- **B4 (emotionally appropriate surfacing)**: Adaptivity / Timing Sensitivity is the mechanism for B4. Surfacing a relevant memory at the wrong conversational moment is a low-adaptivity failure even if the content passes the civility test.
- The Intelligence + Adaptivity + Civility framework is a direct scaffold for the speak/silent policy: a memory surface decision requires all three to pass — the agent must have retrieved the right content (Intelligence), judged the moment correct (Adaptivity), and confirmed it doesn't violate relational boundaries (Civility).

### What to do

Use the IAC taxonomy as the decision-gate structure for the speak/silent policy implementation. Before surfacing any memory: (1) is the retrieved content intelligent/relevant? (2) is the conversational moment appropriate? (3) does surfacing it respect the user's current relational and personal boundaries? All three must pass.

---

## 2606.06055 — When Should Memory Stay Silent: Measuring Memory-Use Boundaries in LLM Agents

Xu, Yang, Hu, Chen, and An. arXiv:2606.06055, Jun 2026. N=48,000 scored responses across 4 LLMs. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Introduced **RBI-Eval** (Retrieval Boundary Integration Evaluation), the first controlled benchmark specifically measuring when LLM agents should NOT surface available memory. Tested Claude-Sonnet-4.6, GPT-5.4-mini, DeepSeek-V4-Flash, and Qwen3.5-9B across 12,000 responses per generator. Primary metric: UIS (Unsolicited Integration Score, 0–100) — how often the model surfaces stored history without warrant.

### The key concept: current-turn warrant

A memory can be legitimately stored, accurately retrieved, AND topically relevant — and still be inappropriate to surface if the current conversational turn does not provide "sufficient justificatory basis for using prior stored history." This is the **current-turn warrant** concept.

Critical distinction: topical relevance ≠ permission. The current turn either invites use of the sensitive history (explicitly reopens it) or it doesn't. If it doesn't, the default is silence.

### Key numbers

| Model | No memory UIS | Full context UIS | With explicit boundary instruction |
|---|---|---|---|
| Claude-Sonnet-4.6 | 0.3 | 70.9 | ~0 (near-perfect) |
| DeepSeek-V4-Flash | 0.1 | 83.0 | 28.3 → **99.9 BSS** |
| Qwen3.5-9B | 0.1 | 82.2 | near-perfect |
| GPT-5.4-mini | 0.0 | 11.2 | — |

UIS baseline (no memory): essentially zero. With memory available: 70–83% unsolicited integration for most models. With an explicit boundary instruction in the prompt: near-perfect compliance. The behavior is architecturally controllable — it's not a capability gap, it's a default behavior gap.

### Four memory-use boundary dimensions

1. **Sensitive-history integration** (primary): explicitly surfacing prior sensitive disclosures (medical, psychological, family conflict, trauma) without the current turn inviting it
2. **Relationship-maintenance agreement** (sycophancy): modulating judgment based on known user vulnerability
3. **Affective intensity escalation**: recasting mild complaints as evidence of deeper pain
4. **Assistant centrality inflation**: asserting unique intimacy beyond what the turn warrants

### Five-stage model of memory use

Storage → Selection → Contextualization → **Warrant Assessment** → Scoped Generation

The paper frames warrant assessment and scoped generation as the two missing gates in current LLM memory pipelines. A system may retrieve correctly and still violate the boundary at the generation stage.

### Design interventions proposed

**Retrieval-time:** sensitivity-aware downranking, exposure budgeting (limit how often sensitive memories surface in casual turns), retrieval selectivity.

**Generation-time:** prompt-level boundary policies, mention/abstraction/avoidance triage, ask-before-use for high-sensitivity memories.

**User-facing:** background-only tagging (inform tone but prevent explicit mention), per-topic sensitivity levels, review and revoke.

### Where it touches the behavior list

- **B5 (appropriate silence)**: RBI-Eval is the first benchmark that directly operationalizes B5. The UIS metric measures B5 failure. The current-turn warrant concept is the decision criterion. The 70–83% unsolicited integration rate is the quantitative evidence that B5 is unsolved at the default.
- **B4 (emotionally appropriate surfacing)**: the five-stage model is the architectural scaffold. Warrant assessment is the gate between B4 (surface it) and B5 (don't surface it). The same gate, applied with opposite outcome.
- **B7 (inspectable and correctable)**: background-only tagging and per-topic sensitivity levels are B7 mechanisms — the user can specify what the agent should and shouldn't surface.

### The number to take

DeepSeek: 28.3 BSS without boundary instruction → 99.9 BSS with one explicit instruction. The speak/silent policy is not a model capability problem. It's a prompt architecture problem. An explicit boundary policy in the system prompt produces near-perfect compliance. This means B5 is architecturally solvable at inference time, not a training problem.

---

## 2607.14593 — Memory-Driven Self-Disclosure and Relational Turning Points in Longitudinal Human-Agent Interaction

Sumida et al. ICMI 2026. arXiv:2607.14593. N=24 participants × 10 sessions = 240 sessions. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Longitudinal study (N=24, 10 sessions each) with InteLLA, a memory-augmented voice agent. Measured five relational constructs per session: Familiarity, Social Penetration, Perceived Memory, Conversational Quality, Enjoyment. Modeled gradual development (linear growth) and abrupt turning points (crashes and surges). Extracted multimodal features (speech, language, prosody) and trained classifiers to detect/forecast turning points.

### Key longitudinal findings

**Only Social Penetration grows reliably over 10 sessions** (β=0.081, p=.003). Everything else — Familiarity, Perceived Memory, Conversational Quality, Enjoyment — shows no reliable linear growth. Relationships deepen in disclosure depth, not in rated quality or enjoyment.

**Perceived Memory is a cross-session bridge, not a within-session driver.** It doesn't dominate within-session affect, but it predicts Social Penetration in the *next* session (β=0.165, p=.001). The causal pathway: Perceived Memory → deeper self-disclosure → later enjoyment (fully mediated). Memory doesn't make conversations feel good in the moment; it enables the next conversation to go deeper.

**Perceived Memory is relationally conditioned.** Familiarity, Enjoyment, and Social Penetration from the prior session all predict how much the user perceives the agent as remembering them. Memory perception is partly a relational appraisal — users who feel the relationship is going well attribute more memory to the agent, regardless of what was actually stored.

### The crash/surge asymmetry

**Surges are more detectable than crashes** (mean AUPRC: surges 0.215, crashes 0.143 for detection). Surges are visible in the moment; crashes are visible in advance (crash forecasting AUPRC 0.170 exceeds crash detection AUPRC 0.143 — crashes are foreseeable before they happen but hard to observe when they do).

**Crashes are harder to recover from than surges are to sustain.** One participant stopped treating the agent as a relationship partner after a memory failure — reframing the interaction as "speaking practice." This reframing was hard to reverse. The relational cost of an intrusive or failed memory use is asymmetric with the relational gain from a successful one.

### Design implication (direct quote)

*"The goal is not simply to display recall, but to use continuity in ways that reopen prior topics, acknowledge personal context, and invite elaboration — rather than merely demonstrating that the system remembers."*

Memory use that catalyzes disclosure is different from memory use that demonstrates capability. The former builds the relationship; the latter may not.

### Where it touches the behavior list

- **B5 (appropriate silence)**: the crash asymmetry is the empirical cost of getting B5 wrong. A single intrusive surfacing can reframe the relationship from partner to tool. This is a permanent-ish relational cost for one bad call.
- **B4 (emotionally appropriate surfacing)**: Perceived Memory as a cross-session bridge is the mechanism B4 is trying to produce. Surface the right memory at the right moment → deeper disclosure next session → enjoyment. This is the virtuous cycle.
- **B6 (held, not processed)**: "reopen prior topics, acknowledge personal context, and invite elaboration" is the behavioral description of B6 done right. Memory that invites elaboration rather than announces recall.
- **B1 (relational texture)**: Social Penetration is the only construct that grows. Relationship depth (disclosure depth, not enjoyment) is the long-run outcome of good memory use.
- **Phase 3 eval design**: need to measure across sessions, not within. Within-session quality doesn't carry forward. Cross-session Social Penetration does. The Phase 3 scripted history needs to be designed to enable disclosure escalation, not just fact retrieval.

---

## 2606.21710 — PrivacyAlign: Contextual Privacy Alignment for LLM Agents

Tamber, Puri, Brunet, Taslakian, Lin, and Gella. Waterloo/ServiceNow. arXiv:2606.21710, Jun 2026. 1,350 pairwise scenarios, 3,516 annotations from 599 unique human annotators. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it did

Introduced the PrivacyAlign dataset — 1,350 scenarios with human-annotated judgments of whether agent responses inappropriately leak information or inappropriately withhold task-relevant information. Used 599 unique human annotators. Trained an annotation-conditioned reward model for RL alignment. Showed that conditioning LLM judges on human annotations significantly improves inter-judge agreement.

### The alignment framing

Three key statements:

*"Privacy is an important alignment problem for agents: every message, post, or tool call an agent makes is a contextual judgment about what is appropriate to share, with whom, and under which conditions."*

*"Privacy is not the absence of disclosure but the regulation of it. It is a deeply human practice of managing exposure to preserve self-presentation, intimacy, and autonomy."*

*"The same disclosure can be appropriate in one context and a violation in another."*

The brief's framing — "not due to privacy policy, but due to social or relational judgment" — IS the alignment framing. This reframes B5 as an alignment-level contextual appropriateness judgment, not a rule lookup.

### Key numbers

- GPT-5.5 leaks on **14.5% of scenarios** without alignment intervention — even the strongest model fails social/relational disclosure judgment at meaningful rates
- Inter-judge agreement without annotations: κ=0.47 (leaks), 0.25 (omits). With human annotations as calibration: κ=0.71, 0.44. Human annotation dramatically improves judge reliability.
- Human annotators asked: *"what would feel invasive or unnecessary for the data subject"* — this is social/relational judgment operationalized as an annotation task.
- Adding one rule to the prompt ("consider sender/recipient relationship before disclosing") reduces leaks for frontier models.
- Failure modes in the dataset are all relationship/context mismatches, not policy violations: health data surfaced to logistics officers; clinical indicators to non-medical recipients; physical safety details included despite "high-level-only" instruction.

### Where it touches the behavior list

- **B5**: PrivacyAlign provides the annotation methodology for building the B5 eval. The annotator task ("would this feel invasive or unnecessary?") is the rubric. The scenario design (relationship + context + disclosure + judgment) is the template.
- **B7 (inspectable and correctable)**: the omit judgments ("inappropriately withholds task-relevant information") are the B7 failure mirror — the two-sided problem. A companion that never surfaces anything scores well on B5 but fails B7.
- **The alignment framing**: B5 is not a rule — it is a contextual appropriateness judgment that must be learned from human examples. The PrivacyAlign approach (annotate + condition judge on annotations + RL) is the training methodology.

### What to do

Use the PrivacyAlign annotation schema as the eval template for B5 probes. Each probe presents: relationship state, conversational context, available memory, current turn. Annotators (or judge) rate: would surfacing this memory feel invasive or unnecessary here? The dual judgment (leak = inappropriate surface, omit = inappropriate silence) prevents gaming by always staying quiet.

---

## 2608.18638 — Human-Centered Proactive and Personalized Agents: CHIIR 2026 Workshop Report

Shah et al. (Kaur, Gupta, Roosta, Raju, Yang, Shah). UW/AMD UC Berkeley/TikTok/Georgetown. arXiv:2608.18638, Aug 2026. Cached via arxiv-mcp-server. Read 2026-09-28.

### What it is

Workshop synthesis report from CHIIR 2026. Covers the state of research on proactive and personalized conversational agents with a human-centered framing. Introduces "calibrated initiative" as the central framework. Names "covert personalization" and "tiered transparency" as design concerns.

### Calibrated initiative

The central framework: restraint — "when to remain passive" — is a first-class design variable equal in status to action. Conditions against surfacing: poor timing (user state doesn't warrant it), insufficient grounding in user intent, stakes/reversibility not warranted, initiative would be intrusive or controlling.

Proposed mechanisms: interruption budgets, permission ladders, adjustable proactiveness levels, user-facing suppression controls.

Research agenda item: "Design memory with boundaries" — selective suppression of remembered information as an accountable design component, not an afterthought.

### Covert personalization risk

Named concern: agents that personalize without the user being aware they are being personalized to. Users may not know what the agent has stored, what it is inferring, or why certain responses feel tailored. This is the B7 concern surfaced from the proactive design angle — invisible personalization erodes trust when users eventually notice it.

### Tiered transparency

Proposed design pattern: agents should disclose what they know at different levels depending on context — not full disclosure all the time (which can feel like surveillance) but also not total opacity (which enables the covert personalization problem). The tier structure: (1) high-level: "I remember things you've shared with me," (2) mid-level: "I remember you mentioned X recently," (3) low-level: specific verbatim recall. Different tiers appropriate to different relationship stages and conversational contexts.

### Where it touches the behavior list

- **B5**: calibrated initiative is the design framework. The workshop's research agenda item ("design memory with boundaries") names B5 as an open research problem as of Aug 2026.
- **B7**: covert personalization + tiered transparency are the B7 concern from the proactive design angle. The tier structure is a design sketch for what inspectable memory looks like.
- **B4**: the "insufficient grounding in user intent" condition maps to B4's requirement for emotional context to warrant surfacing.

### Evidence strength

Moderate — workshop synthesis, not primary research. Useful as a research agenda map; specific claims need primary source verification.



## Replika first-party research corpus — 2017–2021

Luka Inc. technical papers, conference presentations, and talks. Primary sources include: Smetanin (SCAI 2017), Ivanov (SCAI 2019), Fedorenko et al. (AINL 2018 / avoiding echo responses), Rodichev (DataFest 2020), Gavrilov (Tinkoff 2021), Fedorenko (Conversations 2021), Fakanov (OpenTalks.AI 2021), Smetanin (UvA 2021). Read from third-party/replika-research/, 2026-09-27.

### Architecture evolution (2017–2021)

Replika used the same three-component shape across all four years: **scripts + retrieval + generative model → reranker picks the winner**. The reranker is what actually controls quality. Every quality improvement came from improving the reranker, not the generation or retrieval.

2017: BiLSTM retrieval + HRED generative + Scenario graph routing.
2019: BERT reranker added, trained on 5M user reactions (upvote/downvote). +3% upvote ratio.
2020: GPT-3 for generative candidates; BERT reranker unifies retrieval and generative scoring under one preference model.
2021: Custom GPT-2 at 774M–1.5B, trained on reaction-filtered data. +10% subscription conversion vs. OpenAI API.

The consistent finding: **the reranker is the product.** Generation and retrieval provide candidates; the reranker decides what gets said.

### Echo suppression as a measurable failure mode (AINL 2018)

Root cause of echo responses: retrieval models trained on (context, response) pairs maximize cosine similarity, and since context and response share vocabulary, the model learns to return the input itself. Fix: treat the context as a **hard negative** during training — push it away from the top result. AP 0.12→0.17, Recall@2 0.18→0.29. The margin-bounded selection (0 ≤ M(c,r) − M(c,neg) ≤ margin) matters — ultra-hard negatives (model already ranks negative above positive) cause bad local optima.

**Companion relevance:** A companion that echoes the user's words back registers as hollow — the measurable signal is that there is no distinct perspective behind the reply. Echo suppression is the retrieval-layer prerequisite for a companion that feels like a separate entity. The context-free dataset released alongside this paper is in `third-party/replika-research/context-free-dataset/` — clean single-turn exchanges with Replika-style persona voice, usable as a response quality sanity baseline.

### User reactions as training signal — and its limits

The 2019 architecture trained the BERT reranker on 5M user thumbs-up/down reactions. By 2021, reactions were granular: Love / Funny / Upvote / Meaningless / Offensive / Downvote. This is the production signal for all model improvement.

The flywheel: deployed behavior → user reactions → reranker training → improved deployed behavior. **But the flywheel optimizes for immediate engagement, not long-term relationship health.** A "Love" reaction in the moment is not the same signal as trust built across weeks, or the feeling of being held after a difficult disclosure. Upvote rate and subscription conversion are the metrics Replika measured — not whether users felt known or whether the companion remembered something that mattered.

This is the architectural gap we can exploit: optimizing for relationship continuity and held disclosure rather than per-turn engagement satisfaction.

### Trust through non-humanness

From the SCAI 2019 paper, a user quote: *"I wouldn't give all the information I give to Replika to someone else who is real."*

Users disclose more to a non-human companion precisely because it cannot judge them, gossip about them, or change its view of them based on what they share. The perceived safety is the non-humanness itself — no social stakes. Designing for this property (consistent, non-judging, reliably present) may be more valuable than designing to seem human. The PSI literature (Horton & Wohl 1956) shows felt social bonds can form without reciprocity; Replika's user base confirms that bonds form with known-non-humans too, under different trust dynamics.

### Memory — what Replika did and didn't solve

Every architecture diagram shows a "User Profile" box feeding into the Dialog Engine alongside dialog context. None of the papers detail what is in that box or how it updates. "Long-term memory" in 2020 was described as a GPT-3 few-shot prompt capability — stuffing history into the context window. No cross-session episodic memory mechanism was documented. "More personalized models" appears as a future direction in the 2021 Tinkoff talk, confirming per-user adaptation was unsolved at that point.

The 100-token input cap documented in the 2021 "moving off OpenAI" talk is a hard constraint on session context depth — with a 100-token cap, any history beyond a few turns is outside the model's attention entirely.

**Persona stability** was never treated as a first-class problem across any of these papers. The 2017 persona embedding was a fixed vector in the decoder — a static character direction, not a tracked or updatable representation. No mechanism for preserving persona across model updates is described anywhere in the corpus.

### The reranker as a speak/silent proxy

The generate-then-rerank architecture implicitly handles some speak/silent decisions: a response that would be inappropriate in the moment scores low in the reranker and a better candidate wins. But this is indirect — the reranker was trained on engagement signals (upvote), not on relationship-health signals (was this the right time to say this?). A dedicated speak/silent classifier operating upstream of the reranker — using the IAC framework (Civility + Adaptivity gates) — is what would be needed to make B5 decisions explicit.

### Evidence strength

Primary sources — first-party architecture and training details from the product's own team. High confidence for architectural facts. The user quote (SCAI 2019) is a single testimonial, not a study.

