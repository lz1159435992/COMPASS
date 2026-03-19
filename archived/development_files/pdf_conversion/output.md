# Conversion of main.pdf

## Page 1

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
Constraint Simplification Approach Based on
Reinforcement Learning and Large Language Models
ANONYMOUS AUTHOR(S)
Constraint solving is a core challenge in formal verification and program analysis, particularly for complex
SMT-LIB2 formulas involving nonlinear arithmetic, modular operations, and mixed-type logic. General solvers
such as Z3 often struggle with long timeouts or fail to find satisfying assignments due to the combinatorial
complexity of symbolic reasoning.
In this work, we propose a hybrid approach that integrates reinforcement learning (RL) with large language
model (LLM) reasoning to guide variable concretization and simplify constraint systems. Our method leverages
structural attributes—such as clause participation and interaction with constants—to prioritize variables for
assignment. A pretrained LLM (e.g., LLaMA 3.1:70B) is then used to generate context-aware value suggestions
based on logical dependencies and historical counterexamples. The selected assignments are applied iteratively,
and their impact is evaluated using a multi-tiered reward mechanism combining predictive modeling and
solver feedback.
We evaluate our framework on the SMTimer dataset and extend it to the SMT-COMP benchmarks. Ex-
perimental results show that our RL+LLM method outperforms baseline approaches, including vanilla Z3,
Random-based, and LLM-based strategies. In particular, our method solves 94 out of 337 constraints within a
1200-second timeout, compared to Z3’s 72 solutions. TODO:Moreover, it also transforms previously unsolved
"unknown" instances into satisfiable ones by strategically reducing symbolic uncertainty.
ACM Reference Format:
Anonymous Author(s). 2018. Constraint Simplification Approach Based on Reinforcement Learning and Large
Language Models. In Proceedings of Make sure to enter the correct conference title from your rights confirmation
email (Conference acronym ’XX). ACM, New York, NY, USA, 32 pages. https://doi.org/XXXXXXX.XXXXXXX
1
Introduction
Satisfiability Modulo Theories (SMT) solvers are a cornerstone of modern computer science, pro-
viding the foundational reasoning capabilities for a vast array of applications, including symbolic
execution [8, 19], formal verification [2], static analysis [3], program synthesis [36], and automated
theorem proving [13]. These powerful engines can determine the satisfiability of logical formulas
over background theories like arithmetic, bit-vectors, and arrays. However, as software systems
grow in complexity, so do the constraints generated to reason about them. State-of-the-art SMT
solvers, despite their sophistication, often face a "performance cliff" when confronted with formulas
involving nonlinear arithmetic, intricate bit-vector operations, or a high-dimensional symbolic
search space. This frequently leads to timeouts or inconclusive results, creating the well-known
constraint-solving bottleneck that hinders the scalability of many analysis tools [9].
To mitigate this bottleneck, researchers have explored various formula simplification strategies.
The most fundamental approach involves manual analysis by a domain expert, but this is inher-
ently unscalable, time-consuming, and demands specialized knowledge that is often unavailable.
Consequently, the focus has shifted to automated techniques. These include static techniques like
Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee
provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and
the full citation on the first page. Copyrights for components of this work owned by others than ACM must be honored.
Abstracting with credit is permitted. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires
prior specific permission and/or a fee. Request permissions from permissions@acm.org.
Conference acronym ’XX, June 03–05, 2018, Woodstock, NY
© 2018 ACM.
ACM ISBN 978-1-4503-XXXX-X/18/06
https://doi.org/XXXXXXX.XXXXXXX
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 2

50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
2
Anon.
constraint slicing, which removes irrelevant parts of a formula [44], and abstraction methods that
replace complex expressions with simpler surrogates. Dynamic techniques, such as the partial
concretization central to concolic testing [15, 34], assign concrete values to certain symbolic vari-
ables to reduce the solver’s search space. While effective to a degree, these methods are often
guided by static heuristics or shallow syntactic cues. They typically lack semantic awareness and
adaptability, failing to identify the most critical variables to simplify or the most impactful values
to assign. More recent efforts have applied machine learning, for instance, to predict a constraint’s
solvability [26] or to learn branching heuristics inside solvers [21]. Yet, the challenge of intelligently
and proactively simplifying a complex formula before it overwhelms a solver remains largely open.
In this work, we introduce a framework that acts as a learning-guided enhancement for off-
the-shelf SMT solvers. Rather than replacing these solvers, our method serves as an intelligent
co-pilot, designed to simplify hard constraint instances so that the underlying solver can tackle them
effectively. Our approach is designed to operate directly on any SMT-LIB2 formatted constraint
system, making it agnostic to the constraint’s origin and broadly applicable across any analysis
pipeline that relies on SMT solving.
Our framework decouples the simplification challenge into two synergistic components: (1) a
strategic variable selection agent powered by Reinforcement Learning (RL), and (2) a tactical value
suggestion module driven by a Large Language Model (LLM). The RL agent is trained to identify
which symbolic variables, if concretized, would yield the greatest reduction in complexity. Once
a high-impact variable is selected, we leverage an LLM to generate a semantically meaningful
concrete value. The LLM is conditioned not only on the logical structure of the formula but also on
a history of prior failed assignments (counterexamples), allowing it to reason from past mistakes.
This simplified formula is then passed to a standard solver like Z3.
This RL+LLM architecture enables a dynamic and adaptive simplification strategy that is difficult
to achieve with handcrafted heuristics. Through extensive evaluation on benchmarks from symbolic
execution and SMT-COMP, we demonstrate that our approach improves the success rate and
reduces the runtime for hard constraints. Notably, our framework empowers Z3 to solve instances
it previously could not resolve within the timeout, confirming the practical impact of augmenting
a state-of-the-art solver with learning-guided simplification.
Building on this motivation, our work makes the following contributions:
• Hybrid RL+LLM Architecture: We introduce the first framework that decomposes con-
straint simplification into strategic variable selection (RL) and semantic value generation
(LLM), enabling each component to leverage its strengths for the "what to simplify" and "how
to simplify" decisions.
• Counterexample-Guided Value Generation: We present an LLM-driven mechanism that
utilizes a history of prior failed assignments in its prompt, guiding context-aware candidate
value generation beyond heuristic-based approaches.
• Multi-Component Reward System: We introduce a hybrid reward function combining
predictive models for solving complexity with actual solver feedback, providing dense reward
signals to mitigate sparse reward challenges in RL training.
• Cross-Solver Generalizability: We demonstrate empirical effectiveness across multiple
solver architectures (Z3, CVC5, distributed systems), showing that our semantic simplification
approach provides orthogonal benefits to existing solver enhancements.
The remainder of this paper is organized as follows: Section 2 reviews related work; Section 3
provides necessary background knowledge; Section 4 presents a motivating example that illustrates
the complexity of SMT constraints; Section 5 positions our approach and formalizes the problem;
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 3

99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
3
Section 6 details our methodology; Section 7 reports experimental evaluation; Section 8 discusses
limitations and future work; and Section 9 concludes.
2
Motivating Example
To demonstrate the challenges of complex SMT queries and motivate our hybrid RL+LLM approach,
we present a representative example that illustrates both the difficulty of constraint solving and
the potential for strategic variable concretization.
2.1
A Challenging Constraint System
Consider the system of constraints defined over six integer variables: 𝑥,𝑦,𝑧,𝑎,𝑏,𝑐. This system is
representative of path conditions generated by symbolic execution of programs with complex data
transformations.
Listing 1. An illustrative system of nonlinear integer constraints.
C1: (((x * 37 + 23) % 101) + ((x - 30)^2 % 57) + y^3 - z^2 + a^2 - b + c) == 150
C2: (x^4 + y^3 - 5*z*a + b - c^2) < 400
C3: ((x^2 - y^2) + ((z*12 + 301) % 101) + ((z -15)*(z-30) % 57) +
((z+15)*(z -30)*(z-11) % 9) + a - b*c)
>
(((a*12 + 301) % 101) + ((a -15)*(a-30) % 57) + ((a+15)*(a -30)*(a-11) % 9))
C4: (((x^2 - y^2) + ((z*37 + 23) % 101) + ((z - 30)^2 % 57) + a - b*c)) != 55
// Full constraint: C1 AND C2 AND C3 AND C4
This system exhibits several sources of complexity that are notoriously difficult for SMT solvers:
• Nonlinear Polynomials: High-degree terms like 𝑥4 and nested products like (𝑧+ 15)(𝑧−
30)(𝑧−11) create a vast, non-convex search space.
• Modular Arithmetic: The modulo operator (%) introduces discontinuities, forcing solvers
to reason through case splits, which can lead to exponential complexity.
• High Coupling: Variables are tightly coupled across multiple, interdependent constraints,
meaning a change in one variable has cascading effects.
When presented to a state-of-the-art solver like Z3 [14], this system of constraints is intractable;
the solver fails to return a result within a 1200-second timeout. This scenario represents a classic
case of the SMT bottleneck that motivates our approach.
2.2
Strategic Variable Analysis
To systematically identify which variable should be concretized, we can assess each variable’s
potential impact by analyzing its structural role in the formula. We propose a heuristic framework
based on three metrics:
• Frequency (F): The total number of times a variable appears.
• Complexity (C): The number of times a variable is involved in high-cost nonlinear operations
(e.g., powers, products of variables, modulo).
• Coupling (P): The number of distinct constraints (C1-C4) in which the variable participates.
We can score each variable based on these metrics, with a higher total "Impact Score" (𝐼= 𝐹+𝐶+𝑃)
indicating a greater potential for simplification upon concretization. Table 1 shows this analysis for
our example.
The analysis clearly identifies variable z as the most influential, with the highest Impact Score
of 11. It is the only variable present in all four constraints and is involved in the most complex
operations. This makes it the prime candidate for concretization.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 4

148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
4
Anon.
Table 1. Heuristic impact scores for each variable in the example.
Variable
Frequency (F)
Complexity (C)
Coupling (P)
Impact Score (I)
𝑥
3
2 (𝑥4, 𝑥2)
3 (C1,C2,C4)
8
𝑦
3
2 (𝑦3, 𝑦2)
3 (C1,C2,C3)
8
z
4
3 (𝑧2, mod, nested)
4 (C1,C2,C3,C4)
11
𝑎
4
2 (𝑎2, mod)
3 (C1,C2,C3)
9
𝑏
2
1 (𝑏∗𝑐)
3 (C1,C2,C3)
6
𝑐
2
2 (𝑐2, 𝑏∗𝑐)
2 (C1,C2)
6
2.3
Simplification and Validation
Having identified 𝑧as the key variable, setting 𝑧= 1 proves highly effective:
• The nested term (𝑧+ 15)(𝑧−30)(𝑧−11) (mod 9) collapses to a constant: (16)(−29)(−10)
(mod 9) →4640 (mod 9) = 5.
• Other modulo expressions, like ((𝑧∗12 + 301) (mod 101)), similarly resolve to constants.
• All powers of 𝑧become 1.
With 𝑧concretized to 1, the once-intractable system simplifies dramatically. The solver is no
longer burdened by the complex, branching logic associated with 𝑧. As a result, Z3 finds a satisfying
model for the remaining variables in under 1 second.
2.4
Limitations of Manual Analysis
While this example demonstrates the potential of strategic variable concretization, it also reveals
the limitations of manual heuristic-based approaches:
• Scalability: Manual analysis becomes impractical for systems with hundreds or thousands
of variables.
• Value Selection: Even after identifying the key variable 𝑧, choosing the optimal concrete
value (1 in this case) required domain knowledge and trial-and-error.
• Dynamic Dependencies: Variable importance can change as constraints are simplified,
requiring continuous re-evaluation.
• Suboptimality: Heuristic scoring may miss subtle interactions that affect the actual solving
complexity.
These limitations motivate the need for an automated, learning-based framework that can:
(1) Learn Strategic Selection: Use reinforcement learning to discover optimal variable selection
policies that go beyond simple heuristics.
(2) Generate Semantic Values: Leverage large language models to generate contextually ap-
propriate concrete values based on code semantics and constraint structure.
(3) Adapt Dynamically: Continuously refine the selection strategy based on feedback from
actual solving attempts.
(4) Scale Effectively: Handle complex, real-world constraint systems with hundreds of variables
and intricate dependencies.
This motivating example establishes the foundation for our hybrid RL+LLM approach, demon-
strating both the promise of strategic variable concretization and the necessity of automated,
intelligent methods to realize this potential at scale.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 5

197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
5
3
Background and Problem Formulation
This section first provides the necessary background on the core technologies leveraged in our
approach. It then formally defines the SMT query simplification problem and, finally, models it as a
Markov Decision Process (MDP) to be solved with reinforcement learning.
3.1
Background
3.1.1
The Challenge of SMT Solving. Satisfiability Modulo Theories (SMT) extends Boolean
satisfiability (SAT) to handle richer theories like arithmetic, bit-vectors, and arrays. SMT solvers,
such as Z3 and CVC5, are crucial in software verification and symbolic execution but face perfor-
mance bottlenecks with complex, quantifier-heavy formulas. The complexity often arises from
a vast search space and intricate variable dependencies, leading to timeouts. Our work aims to
simplify formulas before they are passed to the solver, mitigating this challenge.
3.1.2
Reinforcement Learning for Sequential Decision Making. Reinforcement Learning (RL) is
a paradigm for learning optimal behavior in sequential decision-making problems. An RL agent
interacts with an environment over a series of time steps, learning a policy—a mapping from states
to actions—that maximizes a cumulative reward signal. This approach is naturally suited for our
problem, as simplifying an SMT query can be framed as a sequence of concretization actions.
However, applying RL to SMT query simplification presents significant challenges. The state
space, representing all possible (partially) simplified queries, is vast and continuous. The action
space, comprising all variables and their potential concrete values, is similarly large and complex.
Furthermore, the most crucial reward signal—the final solver time—is inherently sparse and
delayed, as it is only available after a complete sequence of actions. Relying solely on this signal
makes learning prohibitively inefficient.
To overcome these obstacles, Actor-Critic methods provide a powerful framework. They
decouple the learning problem into two parts: an Actor that learns and executes the policy, and a
Critic that evaluates the policy by estimating the long-term value of states or actions. By providing
dense, learned feedback, the Critic guides the Actor’s learning process, enabling it to learn effectively
even when external rewards are sparse. This makes Actor-Critic an ideal choice for navigating the
complexities of our SMT simplification task.
3.1.3
Large Language Models for Semantic Reasoning. While RL can learn which variable to simplify,
deciding what concrete value to use requires semantic understanding. Large Language Models
(LLMs) excel at this, analyzing a variable’s context to generate a plausible value. Our framework
leverages LLMs as a sophisticated generator of candidate values, complementing the RL agent’s
strategic decision-making.
3.2
Problem Formalization
We define the problem of simplifying an SMT query 𝑞by strategically replacing some of its symbolic
variables 𝑉with concrete values—a process called concretization. A concretization action is a
pair 𝑎= (𝑣,𝑐) for a variable 𝑣∈𝑉and a concrete value 𝑐.
Problem 3.1 (Optimal Query Simplification). Given an SMT query 𝑞and a time budget 𝑇𝑏𝑢𝑑𝑔𝑒𝑡,
find a sequence of concretization actions 𝜎= ⟨𝑎1, . . . ,𝑎𝑘⟩that transforms 𝑞into 𝑞′ such that:
(1) Efficiency: The solving time of the simplified query is minimized: 𝑇𝑠𝑜𝑙𝑣𝑒(𝑞′) ≤𝑇𝑏𝑢𝑑𝑔𝑒𝑡.
(2) Soundness: If the original query 𝑞was satisfiable, 𝑞′ must also be satisfiable.
Finding an optimal sequence 𝜎is intractable due to the combinatorial search space, making the
problem well-suited for a learning-based approach like RL.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 6

246
247
248
249
250
251
252
253
254
255
256
257
258
259
260
261
262
263
264
265
266
267
268
269
270
271
272
273
274
275
276
277
278
279
280
281
282
283
284
285
286
287
288
289
290
291
292
293
294
6
Anon.
3.3
Modeling as a Markov Decision Process
To learn an effective simplification strategy, we model Problem 3.1 as a finite-horizon Markov
Decision Process (MDP), defined by:
• State (𝑠𝑡): A representation of the current SMT query𝑞𝑡and the history of applied concretizations
𝐻𝑡.
• Action (𝑎𝑡): A concretization action (𝑣𝑡,𝑐𝑡). Our framework decouples this choice: the RL agent
selects the variable 𝑣𝑡, and the LLM proposes the value 𝑐𝑡.
• Transition (𝑃): A deterministic function where applying 𝑎𝑡to 𝑠𝑡yields a new state 𝑠𝑡+1.
• Reward (𝑅(𝑠𝑡,𝑎𝑡)): A multi-component reward function that combines dense, predicted rewards
based on estimated complexity reduction with sparse, actual rewards from solver feedback. This
hybrid approach balances immediate guidance with long-term objectives.
By solving this MDP, the agent learns a policy 𝜋that approximates the optimal simplification
strategy 𝜎∗. The goal is to maximize the total expected reward, which incentivizes finding short,
effective simplification sequences.
4
Methodology
Building on the motivating example from Section 2 and the problem formalization from Section 3,
this section details the technical implementation of our hybrid RL+LLM framework for SMT
constraint simplification. Our approach decomposes the complex joint optimization problem into
two manageable sub-problems: strategic variable selection (RL) and semantic value generation
(LLM).
4.1
Framework Architecture
The complete workflow of our proposed method is depicted in Figure 1. The process starts with an
SMT query in SMT-LIB format, undergoes preprocessing for normalization and feature extraction,
then enters the core simplification loop where the RL agent and LLM iteratively select and concretize
variables until the query is solved or a timeout is reached.
Feature
encoding 
Predictive
model
training
Predictor
v1
RL agent
3
LLM
SMTLIB2 
...
(assert (= (+
(mod (+ (* x 3) 7) 10) 
(mod (- x 5) 4)
(^ y 2) 
(ite (> z 0) (+ z 10) 
(- z 10)) 
(^ z 2) 
(- (^ x 2)) ) 100))
(assert (< (^ z 3)
100)) 
(assert (distinct y 5)) 
...
Variable normalization
x
y
z
v1
v2
v3
Variable
Clause Sizes Clause Count
...
x
4
3
...
y
2
2
...
z
5
4
...
Constraint simplification
through RL and LLM
Check SAT
Fig. 1. Workflow of our proposed constraint simplification framework, combining reinforcement learning for
variable selection and a large language model for value generation.
4.2
State and Action Representation
To effectively apply reinforcement learning, we must first precisely define the environment in
which the agent operates. This involves establishing a canonical representation for the problem
state and formally defining the set of actions the agent can perform.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 7

295
296
297
298
299
300
301
302
303
304
305
306
307
308
309
310
311
312
313
314
315
316
317
318
319
320
321
322
323
324
325
326
327
328
329
330
331
332
333
334
335
336
337
338
339
340
341
342
343
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
7
Table 2. Attributes for variable normalization, ordered by importance.
Attribute
Description
Variable Clause Sizes
The sum of elements in clauses where the variable appears.
Variable to Clause Count
The number of distinct clauses the variable appears in.
Variable Frequencies
The total number of times the variable occurs in the formula.
Total Logic Operations
The number of logical operations the variable participates in.
Variable Constant Interactions
The count of clauses where the variable appears with a constant.
Variable Normalization for Canonical State Definition To ensure consistency and improve
the generalizability of our learning models, we first apply a deterministic normalization process to
the variables in the input SMT query. Raw SMT-LIB files often contain arbitrary or inconsistent
variable names (e.g., system-generated ‘v_123‘ vs. user-defined ‘is_valid‘). This heterogeneity
introduces noise that can hinder feature learning.
We address this by renaming all variables to a canonical form, VAR1, VAR2, . . . , VAR𝑛. This
renaming is not arbitrary; it is based on a **multi-level lexicographical sort** of the variables
according to five structural attributes, ordered by descending importance as shown in Table 2.
Variables are first sorted by ‘Variable Clause Sizes‘; in case of a tie, ‘Variable to Clause Count‘ is
used as the tie-breaker, and so on. This deterministic ordering ensures that variables with higher
structural impact are consistently mapped to lower-indexed canonical names, which provides a
structured, predictable environment for the agent.
State Encoding After normalization, we serialize the SMT formula into a flat string and use a
pre-trained language model (e.g., CodeBERT) to generate a dense vector embedding. This embedding
captures the rich syntactic and semantic features of the constraint formula. The resulting fixed-
dimensional vector serves as the state representation 𝑠𝑡for our RL agent, providing a compact yet
informative summary of the current SMT query.
Hybrid Action Space The action space in our framework is a hybrid, structured set. An action 𝑎𝑡
is a tuple (𝑣𝑡,𝑐𝑡), where 𝑣𝑡is the symbolic variable to concretize and 𝑐𝑡is the concrete value assigned
to it. Following our divide-and-conquer approach, the selection of this action is decomposed:
• The RL agent selects 𝑣𝑡from the discrete set of normalized variables, 𝑉= {VAR1, . . . , VAR𝑛}.
• The LLM generates a value 𝑐𝑡from a vast, continuous/unstructured domain, conditioned on
𝑣𝑡and the current state 𝑠𝑡.
This decomposition keeps the RL agent’s policy search space manageable while leveraging the
generative power of LLMs for value selection.
4.3
Predictive Guidance Module
To enhance the efficiency of our exploration strategy, we incorporate two auxiliary neural network
predictors trained on historical solving data:
Solvability Predictor A binary classifier 𝑃𝑠𝑜𝑙𝑣𝑒: R768 →[0, 1] that predicts whether a given
SMT formula (represented by its CodeBERT embedding) is likely to be satisfiable within a reasonable
time limit. The predictor uses a simple two-layer fully connected architecture with ReLU activation:
𝑃𝑠𝑜𝑙𝑣𝑒(𝑠) = 𝜎(𝑊2 · ReLU(𝑊1 · 𝑠+ 𝑏1) + 𝑏2)
where 𝜎is the sigmoid function, and the output threshold is set to 0.5.
Time Estimation Predictor A multi-class classifier 𝑃𝑡𝑖𝑚𝑒: R768 →R8 that estimates the
solving time interval for a given formula. We discretize the time range [0, 1000] seconds into 8
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 8

344
345
346
347
348
349
350
351
352
353
354
355
356
357
358
359
360
361
362
363
364
365
366
367
368
369
370
371
372
373
374
375
376
377
378
379
380
381
382
383
384
385
386
387
388
389
390
391
392
8
Anon.
intervals and train the predictor to classify formulas into these time buckets. The architecture
employs multiple fully connected layers with batch normalization, dropout (for regularization), and
Leaky ReLU activations to address the "dying ReLU" problem. Residual connections are incorporated
to facilitate deeper feature extraction.
These predictors serve dual purposes: (1) they provide dense reward signals during RL training
by rewarding actions that lead to predicted-solvable states, and (2) they enable dynamic timeout
adjustment based on estimated solving complexity, preventing the agent from spending excessive
time on intractable instances.
4.4
Learning the Simplification Policy
We train the agent to learn the optimal simplification policy using an RL framework, specifically Soft
Actor-Critic (SAC), which is well-suited for its sample efficiency and robust exploration capabilities.
MDP Formulation We formally model the simplification task as a Markov Decision Process
(MDP), as defined in Section 3. The agent’s objective is to learn a policy 𝜋(𝑣𝑡|𝑠𝑡) that selects a
variable 𝑣𝑡at each state 𝑠𝑡to maximize the cumulative future reward.
Reward Function The design of the reward function is critical for addressing the challenge
of sparse rewards, where a simple binary signal for final success provides insufficient guidance
for learning. To overcome this, we design a multi-tiered reward structure that provides dense,
informative signals. This structure is divided into two primary categories: Estimated Rewards and
Actual Rewards.
Estimated Rewards. This tier provides immediate, heuristic feedback based on predictive models
and intermediate progress, guiding exploration even when the final outcome is unsuccessful.
Components include:
• Rewards for solving individual clauses involving the current variable.
• Penalties for assignments that match or significantly overlap with known counterexamples.
• Rewards based on the predicted solvability of constraint subsets.
• Rewards reflecting the predicted likelihood of overall constraint solvability.
Actual Rewards. This tier provides high-fidelity signals based on concrete solver outcomes,
representing definitive progress. Components include:
• Rewards for successfully solving clauses involving the assigned variable within a specific time
limit.
• Rewards for solving subsets of constraints, using a timeout derived from our predictive model.
• The highest-value rewards for solving the full constraint, especially within the predicted time
limit.
Within each tier, reward values increase with the difficulty and importance of the task (e.g.,
solving the full constraint yields more reward than solving a subset). Furthermore, actual rewards
are weighted more heavily than estimated rewards, ensuring the agent’s ultimate objective remains
aligned with achieving verifiable, impactful simplifications.
4.5
Policy Optimization with Soft Actor-Critic
With the SMT simplification problem fully modeled as an MDP, the final step is to learn an optimal
policy 𝜋. For this task, we employ the Soft Actor-Critic (SAC) algorithm [16], a state-of-the-art,
off-policy actor-critic method designed for complex, continuous or large discrete action spaces.
Our choice of SAC is motivated by two key advantages it offers for our specific problem:
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 9

393
394
395
396
397
398
399
400
401
402
403
404
405
406
407
408
409
410
411
412
413
414
415
416
417
418
419
420
421
422
423
424
425
426
427
428
429
430
431
432
433
434
435
436
437
438
439
440
441
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
9
• Sample Efficiency and Stability: As an off-policy algorithm, SAC can reuse past experiences
(transitions) stored in a replay buffer, making the learning process significantly more sample-
efficient than on-policy methods. This is crucial given the high cost of interacting with an SMT
solver.
• Enhanced Exploration: SAC’s defining feature is its integration of an entropy term into the
objective function. It aims to maximize not only the expected cumulative reward but also the
entropy of the policy. This encourages the agent to explore more broadly and avoid prematurely
converging to a suboptimal, deterministic policy. In the vast search space of SMT simplification,
this structured exploration is vital for discovering non-obvious, yet highly effective, simplification
strategies.
In our framework, the SAC agent consists of an actor network that takes the state embedding 𝑠𝑡
and outputs a probability distribution over the discrete action space (the normalized variables), and
critic networks that estimate the value of each state-action pair, guiding the actor towards better
policies using the multi-component reward signal 𝑟𝑡.
LLM-based Action Completion Once the RL agent’s policy 𝜋selects a variable 𝑣𝑡, the action
is completed by our LLM module. We construct a detailed prompt (as shown in Figure 2) containing
the full SMT query, the chosen variable 𝑣𝑡, and a list of previously failed concretization values
for this variable (the ‘counterexamples‘). The LLM is tasked to return a single, concrete value 𝑐𝑡
that is semantically likely to satisfy the constraints related to 𝑣𝑡. This value completes the action
𝑎𝑡= (𝑣𝑡,𝑐𝑡), which is then applied to the environment.
4.6
Algorithmic Implementation
The overall process is summarized in Algorithm 1. The main loop (lines 6-13) embodies the in-
teraction between the RL agent and the LLM. At each step, the agent selects a variable, the LLM
provides a value, the action is executed, and the agent’s policy is updated based on the reward
received. This continues until the query is solved or the process times out.
Advanced Exploration and Memory Management Our framework incorporates several
sophisticated mechanisms to enhance exploration efficiency and prevent redundant computation:
Sequence-based Counterexample Management Unlike traditional approaches that track
individual variable-value pairs, our system maintains a comprehensive history of assignment
sequences. Each sequence represents a complete path of variable concretizations attempted during
a solving episode. When a sequence fails to produce a satisfying assignment, it is stored in a
counterexample database. Before executing any new sequence, the system checks for:
• Exact Repetition: Identical sequences that have previously failed
• Subsequence Containment: New sequences that contain previously failed subsequences
as prefixes
This mechanism prevents the agent from repeatedly exploring known dead-ends, significantly
improving exploration efficiency.
Dynamic State Re-encoding After each variable concretization, the SMT formula is dynami-
cally updated and re-encoded using CodeBERT. This ensures that the RL agent’s state representation
always reflects the current simplified form of the constraint, enabling more informed decision-
making for subsequent variable selections. The re-encoding process includes:
(1) Parsing the updated SMT-LIB string into Z3 AST format
(2) Extracting the current set of unassigned variables
(3) Generating attention-weighted embeddings with variable-specific masking
(4) Updating the agent’s internal state representation
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 10

442
443
444
445
446
447
448
449
450
451
452
453
454
455
456
457
458
459
460
461
462
463
464
465
466
467
468
469
470
471
472
473
474
475
476
477
478
479
480
481
482
483
484
485
486
487
488
489
490
10
Anon.
Prompt template
system
You are an advanced SAT/SMT solver, focusing on the optimization and resolution of logical constraint problems. Your input
consists of two parts: first, the counterexamples of failed solution assignments previously chosen, and second, the strings in
SMT-LIB format that needs to be solved. You should analyze these inputs, using logical reasoning and heuristic methods to
determine which variable assignments led to the failure of the solution, and identify the variable assignments that satisfy all
constraint conditions. The output should be a specific value assignment for the target variable that can satisfy all the constraints defined in
the strings. Your task is to find the specific values that should be assigned to the variables provided in the prompt to ensure that
the entire constraint system is satisfiable. You should output only the numeric value, with an example as follows: <value> . Do
not output any other text, explanations, or symbols.
user
Here is the counterexamples of failed solution assignments previously chosen in json formats: $ce_json$.	Here is the SMT file
content: $smtlib_str$.
This is the variable values from the previous failed SAT solving attempt and SMT text given to you in segments; analyze it.
To speed up the solution and obtain a SAT result, provide a specific number that $variable_pred$ should be assigned to.
However, do not choose the values that have already failed to solve. Output only the numeric value. Do not output any other
text, explanations, or symbols. The output must be a single number.
output
12 (example)
Fig. 2. Prompt template for heuristic value generation by the LLM.
Multi-level Timeout Management Our system employs a sophisticated timeout strategy that
adapts to the predicted complexity of each constraint:
• Global Timeout: Overall episode limit (1200 seconds)
• Predictive Timeout: Dynamic per-step timeout based on time predictor output
• Adaptive Scaling: Timeout adjustment factor (1.2×) to account for prediction uncertainty
This multi-level approach prevents the system from spending excessive time on intractable instances
while allowing sufficient time for complex but solvable constraints.
5
EVALUATION
In this section, we present the experimental design used to assess the effectiveness and scalability
of the proposed method, which combines reinforcement learning with large language models, for
solving SMT-LIB-formatted constraints. We evaluate the performance of our method in comparison
to other methods, analyze the impact of different constraint types on the results, and investigate
the scalability of our method across diverse datasets.
5.1
Research Questions and Experimental Design
Our evaluation aims to answer the following research questions:
(1) RQ1: Effectiveness of the Proposed Method
Does our hybrid framework combining reinforcement learning and large language models
significantly improve constraint solving efficiency compared to baseline methods?
(2) RQ2: Scalability of the Framework
Is our framework scalable to more complex constraint systems involving nonlinear arithmetic,
modular operations, and mixed-type logic?
(3) RQ3: Impact of Variable Selection Strategy
How effective is the reinforcement learning-guided variable selection strategy compared to
random or heuristic-based approaches?
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 11

491
492
493
494
495
496
497
498
499
500
501
502
503
504
505
506
507
508
509
510
511
512
513
514
515
516
517
518
519
520
521
522
523
524
525
526
527
528
529
530
531
532
533
534
535
536
537
538
539
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
11
Algorithm 1 Constraint Simplification via RL and LLM with Predictive Guidance
1: procedure SimplifyConstraint(𝐹𝑠𝑚𝑡)
2:
𝐹𝑛𝑜𝑟𝑚,𝑉𝑚𝑎𝑝←NormalizeVariables(𝐹𝑠𝑚𝑡)
⊲Sort vars by structural attributes
3:
𝑠0 ←CodeBERTEncode(𝐹𝑛𝑜𝑟𝑚)
⊲Get 768-dim state embedding
4:
𝑎𝑔𝑒𝑛𝑡←InitializeSACAgent(𝑠0)
5:
𝑐𝑜𝑢𝑛𝑡𝑒𝑟𝑒𝑥𝑎𝑚𝑝𝑙𝑒𝑠←[]
⊲Track failed (variable, value) sequences
6:
𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒←[]
⊲Current assignment sequence
7:
while not IsTimeout() and not IsMaxSteps() do
8:
𝑣𝑡←𝑎𝑔𝑒𝑛𝑡.SelectVariable(𝑠𝑡)
⊲RL agent selects variable index
9:
𝑝𝑟𝑜𝑚𝑝𝑡←ConstructPrompt(𝐹𝑛𝑜𝑟𝑚, 𝑣𝑡,𝑐𝑜𝑢𝑛𝑡𝑒𝑟𝑒𝑥𝑎𝑚𝑝𝑙𝑒𝑠)
10:
𝑐𝑡←QueryLLM(𝑝𝑟𝑜𝑚𝑝𝑡,𝑡𝑒𝑚𝑝𝑒𝑟𝑎𝑡𝑢𝑟𝑒= 1)
⊲LLM generates concrete value
11:
𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒.append((𝑣𝑡,𝑐𝑡))
12:
𝐹𝑛𝑒𝑤←ApplyConcretization(𝐹𝑛𝑜𝑟𝑚, (𝑣𝑡,𝑐𝑡))
13:
𝑠𝑡+1 ←CodeBERTEncode(𝐹𝑛𝑒𝑤)
⊲Multi-component reward calculation
14:
𝑟𝑡←0
15:
if 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒∈𝑐𝑜𝑢𝑛𝑡𝑒𝑟𝑒𝑥𝑎𝑚𝑝𝑙𝑒𝑠then
16:
𝑟𝑡←𝑟𝑡−10
⊲Penalty for repeated failed sequences
17:
𝑐𝑜𝑢𝑛𝑡𝑒𝑟𝑒𝑥𝑎𝑚𝑝𝑙𝑒𝑠.append(𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒); 𝑠𝑒𝑞𝑢𝑒𝑛𝑐𝑒←[]
18:
continue
19:
end if
⊲Predictive guidance rewards
20:
ˆ𝑝𝑠𝑜𝑙𝑣𝑒←PredictSolvability(𝑠𝑡+1)
21:
ˆ𝑡𝑠𝑜𝑙𝑣𝑒←PredictSolveTime(𝑠𝑡+1)
22:
if ˆ𝑝𝑠𝑜𝑙𝑣𝑒> 0.5 then
23:
𝑟𝑡←𝑟𝑡+ 5
⊲Reward for predicted solvability
24:
𝑡𝑖𝑚𝑒𝑜𝑢𝑡←ˆ𝑡𝑠𝑜𝑙𝑣𝑒× 1.2
25:
𝑟𝑒𝑠𝑢𝑙𝑡←CheckSAT(𝐹𝑛𝑒𝑤,𝑡𝑖𝑚𝑒𝑜𝑢𝑡)
26:
if 𝑟𝑒𝑠𝑢𝑙𝑡= SAT then
27:
𝑟𝑡←𝑟𝑡+
500000
𝑡𝑖𝑚𝑒𝑜𝑢𝑡
⊲Success bonus inversely proportional to time
28:
return ⟨SAT, GetModel(𝐹𝑛𝑒𝑤)⟩
29:
else if 𝑟𝑒𝑠𝑢𝑙𝑡= TIMEOUT then
30:
𝑟𝑡←𝑟𝑡−5
⊲Timeout penalty
31:
end if
32:
end if
33:
𝑎𝑔𝑒𝑛𝑡.UpdatePolicy(𝑠𝑡, 𝑣𝑡,𝑟𝑡,𝑠𝑡+1)
34:
𝑠𝑡←𝑠𝑡+1; 𝐹𝑛𝑜𝑟𝑚←𝐹𝑛𝑒𝑤
35:
end while
36:
return ⟨UNKNOWN, ∅⟩
37: end procedure
(4) RQ4: Generalizability Across SMT Solvers
Does our RL+LLM enhancement method demonstrate consistent performance improvements
across different SMT solver architectures?
(5) RQ5: Complexity-Guided Routing System Effectiveness
How effectively can static complexity analysis guide the selection between direct solving
and RL+LLM simplification in realistic deployment scenarios?
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 12

540
541
542
543
544
545
546
547
548
549
550
551
552
553
554
555
556
557
558
559
560
561
562
563
564
565
566
567
568
569
570
571
572
573
574
575
576
577
578
579
580
581
582
583
584
585
586
587
588
12
Anon.
Table 3. Overview of the SMTimer dataset and baseline Z3 results.
Tool
SAT
UNSAT
UNKNOWN
SAT Time (s)
UNSAT Time (s)
UNKNOWN Time (s)
buzybox
3802
13359
155
7455.48
1496955.43
186000
gnu
32495
37529
520
409265.42
369984.23
624000
5.2
Experimental Setup and Data Preparation
Dataset and Benchmark Selection We have implemented a prototype tool based on the open-
source reinforcement learning framework Pearl1 and the LLM framework Ollama2, and conducted
experiments on this basis. We use the constraint datasets SMTimer[25], which are collected using
both angr3 and KLEE4 to run symbolic execution with two programs, GNU Coreutils5, a widely-used
benchmark program set in symbolic execution research, and BusyBox6, a collection of standard
UNIX utilities. Take GNU Coreutils as an example, it contains 102 programs, which provide the
basic utilities for the GNU operating system. The dataset has over 70,000 constraint models of
bit-vector theory with angr and over 90,000 constraint models of bit-vector and array theories
with KLEE. Since our method can be applied to any numerical constraints, in addition to the above
real-world datasets, we have also conducted experiments on SMT-COMP7 to verify the scalability
of our method. These constraints are significantly more complex than those in GNU Coreutils and
BusyBox due to their reliance on multi-theory reasoning (e.g., bit vectors, floating-point arithmetic)
and dynamic logical abstraction[4], whereas primarily involve linear branch conditions or Boolean
configuration dependencies[8, 27]. For SMTimer, we first use the Z3 solver to solve them and collect
relevant information. We provide an overall description of the dataset and the solution to related
information in Table 3.
Data Filtering and Preprocessing Pipeline Before conducting experiments, we apply a rig-
orous filtering pipeline to ensure fair comparison and meaningful results:
(1) Initial Solver Filtering: We use multiple SMT solvers to filter the original dataset, removing
trivial or unsolvable constraints to focus on meaningful test cases.
(2) Baseline Time Filtering: Constraints that can be solved by baseline solvers in ≤300 seconds are
excluded, focusing evaluation on challenging instances where our method can demonstrate
advantages.
(3) Variable Count Threshold: Based on our experimental analysis, we restrict evaluation to
constraints with |𝑉| > 5 variables, where𝑉is the set of symbolic variables after normalization.
This threshold ensures the RL agent has sufficient action space for meaningful strategy
exploration.
The filtering process results in different numbers of constraints for each solver due to their varying
solving capabilities and performance characteristics. The exact number of filtered constraints
varies depending on the specific solver being evaluated and will be reported in the corresponding
experimental results.
1https://github.com/facebookresearch/Pearl
2https://github.com/ollama/ollama
3https://github.com/angr/angr
4https://github.com/klee/klee
5https://www.gnu.org/software/coreutils/
6https://busybox.net/
7https://smt-comp.github.io/2024/
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 13

589
590
591
592
593
594
595
596
597
598
599
600
601
602
603
604
605
606
607
608
609
610
611
612
613
614
615
616
617
618
619
620
621
622
623
624
625
626
627
628
629
630
631
632
633
634
635
636
637
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
13
Model Training and Feature Encoding For SMTimer, we randomly divide all the constraints
into two equal parts. One of the parts is used to train the models for predicting whether the
constraints can be solved (model-solve) and the solution time (model-time).
Before training the model, it is necessary to convert the input into vectors first. The constraint
files in the SMT-LIB format have a similar structure to code. Therefore, we leverage the capabilities
of relevant models to encode them.We implement a method that utilizes a pre-trained model,
codebert-base8, with configurable parameters for handling long code sequences. It computes
attention weights based on hidden states, normalizes them, and applies these weights to produce
an attention-weighted representation of the code. Based on the normalized variable sequence, a
mask is generated to emphasize specific variables within the embedding space, adjusting their
contribution during aggregation. To handle very long constraint files, we process code in chunks,
apply attention pooling, and combine the results with dynamically masked variable embeddings to
create a rich, contextualized code representation.
The proposed models are implemented using PyTorch9, a popular deep learning framework. The
model-solve’s architecture consists of two fully connected layers with ReLU activation functions.
The input to the model is a 768-dimensional feature vector extracted from SMT-LIB files using a
BERT-based method mentioned above. The output is a binary classification indicating whether the
problem is solvable or not. It is quite difficult to directly and accurately predict the solving time of
constraints, and this is not the focus of our work either. Therefore, we just use model-time to predict
the approximate time interval to help us set the timeout for the actual solving in our method. We
divide the time from 0 seconds to 1000 seconds into 8 intervals, so our time prediction model is an
8-class prediction model. The model-time’s architecture consists of multiple fully connected (dense)
layers, each followed by batch normalization and dropout layers to stabilize and regularize the
training process. Leaky ReLU activation functions are used to mitigate the "dying ReLU" problem.
The most distinctive feature of this model is the incorporation of residual connections, which add
the input of a layer directly to the output of a later layer, facilitating deeper feature extraction and
better performance.
We selected LLaMA 3.1:70B, LLaMA 3.3:70B, and DeepSeek-R1:70B as the LLM for our prototype
tool due to their advanced natural language understanding, ability to handle complex logical
reasoning, and proven performance in generating efficient variable assignments for constraint
satisfaction problems.
Implementation Details and System Configuration Our implementation is built upon the
Pearl reinforcement learning framework10 and integrates with Ollama11 for LLM inference. Key
implementation parameters include:
• State Encoding: CodeBERT-base model producing 768-dimensional embeddings with attention-
weighted pooling for variable masking
• RL Algorithm: Soft Actor-Critic (SAC) with discrete action space containing variable indices
• LLM Configuration: Temperature=1.0 for increased exploration, streaming responses for
efficiency
• Timeout Management: Dynamic timeout adjustment based on time predictor output (pre-
dicted_time × 1.2)
• Counterexample Management: Sequence-based tracking to prevent repeated failed attempts
8https://huggingface.co/microsoft/codebert-base
9https://github.com/pytorch/pytorch
10https://github.com/facebookresearch/Pearl
11https://github.com/ollama/ollama
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 14

638
639
640
641
642
643
644
645
646
647
648
649
650
651
652
653
654
655
656
657
658
659
660
661
662
663
664
665
666
667
668
669
670
671
672
673
674
675
676
677
678
679
680
681
682
683
684
685
686
14
Anon.
The experiments were conducted on a desktop system equipped with an 11th Gen Intel® Core™
i7-11700K processor @ 3.60 GHz, 128 GB of RAM, and an NVIDIA GeForce RTX 3080 Ti 12 GB
GPU, running Ubuntu 20.04 LTS.
5.3
RQ1: Effectiveness Analysis on SMTimer Dataset
To verify the effectiveness of our method, we conducted experiments on the SMTimer dataset. We
set a timeout and observed whether they could successfully solve the constraints within the timeout
limit. We select the constraints with a solving time greater than 300 seconds for the experiment.
Since our method is mainly aimed at constraints with a relatively long solving time, to reduce their
solving time, there is no need to simplify those constraints with a short solving time. The timeout
for each constraint is limited to 1200s, which is the same as SMT-COMP. Our method leverages
a reinforcement learning agent to select variables for assignment to solve constraint satisfaction
problems. We also restricted our experiments to constraints with more than 5 variables. With very
few variables, the RL agent’s action space is so small that it cannot explore meaningful strategies
(leading to suboptimal performance). In contrast, a larger number of variables expands the action
space, allowing the agent to exploit its strengths in high-dimensional decision-making.
In practice, we found the >5 variable threshold ensured our method had enough complexity to
fully demonstrate its benefits.
Therefore, to ensure that our method achieves the best results, we selected the constraints in
the dataset where the number of variables in the constraints is greater than 5 for experimentation.
Our method (RL+LLM) combines an RL agent for variable selection with a large language model
for value generation. We evaluate three LLM configurations: LLaMA 3.1:70B, LLaMA 3.3:70B, and
DeepSeek-R1:70B.
count
method
0
50
100
150
200
250
300
350
Z3
RL+LLM(LLaMA 3.1:70B)
RL+LLM(LLaMA 3.3:70B)
RL+LLM(DeepSeek-R1:70B)
72
72
94
94
86
86
64
64
265
243
251
273
23
23
19
19
14
14
242
246
251
71
67
50
1
5
22
succeed
failed
unknown to succeed
unknown to failed
sat to succeed
sat to failed
Fig. 3. The solving effects of the Z3 solver and our method
Figure 3 compares the count of constraints solved by Z3 and by our RL+LLM approach (using
different LLMs). LLaMA 3.1:70B solved 94/337 constraints within 1200 s, versus 72/337 solved by Z3.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 15

687
688
689
690
691
692
693
694
695
696
697
698
699
700
701
702
703
704
705
706
707
708
709
710
711
712
713
714
715
716
717
718
719
720
721
722
723
724
725
726
727
728
729
730
731
732
733
734
735
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
15
Table 4. The solving time of the Z3 solver and our method
Time(s)
Z3
RL+LLM
Total Time
358404
311708
Average Time
1064
925
Succeed Time
20108
Succeed Average Time
214
Solve Succeed Time
40404
67217
Solve Succeed Average Time
561
715
Failed Time
291600
Failed Average Time
1200
Solve Failed Time
318000
291187
Solve Failed Average Time
1200
1198
Notably, LLaMA 3.1 solved all but one of the 72 constraints that Z3 could solve, and additionally
solved 23 constraints that Z3 could not solve.
LLM Performance Analysis and Model Selection In our experiments, LLaMA 3.1:70B achieved
the best results, likely due to its stronger capability for structured reasoning and better handling
of symbolic information, as it was trained with a significant portion of code and formal content
while maintaining a direct and concise reasoning style. In contrast, LLaMA 3.3:70B, although based
on an improved version of the 3.1 model with larger training data, exhibited a shift toward more
natural language generation, prioritizing dialogue fluency over strict formal reasoning, which
introduced unnecessary verbosity and reduced efficiency in highly structured tasks like SMT
solving. DeepSeek-R1:70B, despite its advancements in general reasoning and mathematical tasks,
demonstrated relatively weaker performance in SMT constraint solving. This can be attributed to
its tendency to reformulate problems into general reasoning narratives rather than adhering closely
to the strict symbolic formats required for effective SMT solving, resulting in longer inference
paths and frequent timeouts.
These findings suggest that for tasks requiring precise symbolic reasoning under strict time
constraints, models optimized for structured, code-like generation retain a distinct advantage over
those emphasizing broader natural reasoning capabilities.
Detailed Performance Analysis and Time Distribution Our analysis reveals several key
insights about the RL+LLM approach:
• Sequence Length: Successful solutions required an average of 21 variable assignments per
sequence, indicating the method’s ability to handle complex multi-step reasoning.
• Exploration Efficiency: The counterexample mechanism prevented repeated failures, with an
average of 6 distinct assignment sequences attempted per solved constraint.
• Time Distribution: 67% of successful solutions were found within the first 300 seconds,
demonstrating rapid convergence when the approach is effective.
• Variable Selection Impact: RL-guided variable selection showed 35% improvement over
random selection in terms of solution success rate.
Due to the superior performance of LLaMA 3.1:70B, we use this model for all subsequent
experiments.
Table 4 compares cumulative solving times. Our RL+LLM approach took 311,708 s in total to
process all constraints, which is a 13% reduction compared to Z3’s 358,404 s. Focusing on solved
instances: RL+LLM’s 94 solved constraints ran in 214 s on average, less than half of Z3’s 561 s
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 16

736
737
738
739
740
741
742
743
744
745
746
747
748
749
750
751
752
753
754
755
756
757
758
759
760
761
762
763
764
765
766
767
768
769
770
771
772
773
774
775
776
777
778
779
780
781
782
783
784
16
Anon.
average for its 72 solved cases. If Z3 attempted the same 94 cases, we estimate its average would
rise to 715 s, over 3× slower than RL+LLM.
Case Study: Complex Constraint Analysis To further analyze the effectiveness of the method
we proposed, we counted the categories of constraints that can be solved by the Z3 Solver and the
RL+LLM. Our analysis shows that the Z3 Solver can solve the constraints in 4 applications, while
RL+LLM can solve those in 5 applications, and outperforms the Z3 Solver in terms of the number
of constraint solutions in 3 applications.
In the lsmod benchmark (a Linux kernel module case), Z3 failed on all constraints, whereas our
RL+LLM method solved 6 of them. We examined one representative lsmod constraint in detail.
This constraint defines 52 variables and numerous helper functions named syscall_stub_sendfile_-
xxx (likely simulating system call behaviors). The assertions impose many bit-vector conditions:
e.g., unsigned comparisons (bvule), bit extraction (extract), multiplications (bvmul), and additions
(bvadd), along with requirements that certain values not be zero. The overall objective is to check
if a certain complex bit-vector equation (the computed value of syscall_stub_sendfile_8709_64) is
satisfiable (has a solution).
This equation involves a large number of intermediate variables and complex arithmetic opera-
tions. The reason why the Z3 Solver failed to solve this constraint may be that the file involves a
large number of bit vector multiplications (bvmul) and additions (bvadd). These operations have a
relatively high complexity, especially for 64-bit vectors.
The complexity of bit vector operations lies in the need to consider each bit’s value, which may
lead to a state space explosion. For example, the multiplication of two 64-bit vectors produces a
128-bit result, which needs further processing in other operations. In addition, the logical structure
in the file is very complex. The assertion part contains multi-layer nested let expressions, and these
expressions define a large number of intermediate variables. The deeply nested logical structure
requires Z3 solver to maintain a large number of intermediate states during the solving process,
increasing the complexity of solving. Despite this complexity, our RL+LLM approach succeeded. By
guided trial-and-error, it produced 6 candidate assignment sequences (over 826 s runtime, averaging
21 assignments per sequence). In the end, it found a concretization of 25 key variables that collapsed
the problem, allowing the constraint to be solved in 11s by Z3. In essence, the RL+LLM agent
strategically cut down the enormous search space (which was roughly 264 per variable, exploding
exponentially with many variables) into a tractable problem through stepwise concretization.
Answer to RQ1: Our method significantly enhances constraint solving effectiveness com-
pared to Z3. On the SMTimer dataset, it solves 94 out of 337 constraints within a 1200-
second timeout, surpassing Z3’s 72 solutions. Notably, our approach successfully resolves
23 constraints that Z3 cannot solve. Among the tested LLMs, LLaMA 3.1:70B performs
best, reducing average solving time from 561 seconds (Z3) to 214 seconds—a reduction of
over 60%. These results confirm the effectiveness of our hybrid approach in addressing
long-running constraints.
5.4
RQ2: Scalability Analysis on SMT-COMP Benchmarks
To evaluate the scalability of our method, we extend the RL + LLM method to a more diverse
dataset, SMT-COMP, which includes a wide variety of benchmarks. We selected the QF_LIA and
QF_NIA benchmark sets from the SMT-COMP dataset. This choice is well-aligned with our focus
on numerical constraints, as both QF_LIA (Quantifier-Free Linear Integer Arithmetic) and QF_NIA
(Quantifier-Free Nonlinear Integer Arithmetic) consist of quantifier-free formulas over integer
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 17

785
786
787
788
789
790
791
792
793
794
795
796
797
798
799
800
801
802
803
804
805
806
807
808
809
810
811
812
813
814
815
816
817
818
819
820
821
822
823
824
825
826
827
828
829
830
831
832
833
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
17
variables, involving linear and nonlinear arithmetic expressions, respectively. These benchmarks are
standard in evaluating SMT solvers’ performance on numeric reasoning tasks and provide a diverse
set of challenges that test the solver’s ability to handle various arithmetic complexities. By applying
our method to these widely recognized benchmarks, we aim to demonstrate its effectiveness and
robustness in solving a broad range of numerical constraints beyond those derived from real-world
programs like BusyBox. We selected the constraints labeled as “sat" and “unknown" among these
two types of constraints for solving, used 1200 seconds as the threshold, and collected the solving
results. Half of the constraints were randomly selected to train two prediction models. Among the
remaining half of the constraints, the constraints whose solving time was greater than 300 seconds
and the results were not “unsat" were taken as the experimental subjects.
count
count
logic
logic
0
10
20
30
40
50
60
0
500
1,000
1,500
2,000
2,500
QF_LIA
QF_NIA
5
53
3
45
2
8
466
466
1553
324
324
1502
142
51
succeed
failed
unknown to succeed
unknown to failed
sat to succeed
sat to failed
Fig. 4. The solving effects of our method in SMT-COMP
Performance Analysis and Results Comparison Figure 4 shows the solving result for two
SMT logic categories: QF_LIA and QF_NIA. On QF_LIA, Z3 solves 10 out of 58 constraints within the
timeout, while our method solves 5. Notably, for 3 of these, Z3 reports an "unknown" status, which
our approach successfully resolves. In the QF_NIA setting, Z3 solves 193 out of 2019 constraints,
whereas our method solves 466, which is more than twice the number solvable by the Z3 solver.
Among the 1826 constraints where Z3 returns "unknown", our method finds satisfying assignments
for 324. Furthermore, it preserves satisfiability for 142 out of the 193 constraints originally solved
by Z3 (74%).
Limitations and Complementary Analysis Overall, for these complex constraints, our method
can simplify the constraints to a certain extent, transforming the original “unknown” results into
“sat”. However, there are also situations where our method cannot handle overly complex con-
straints. Some constraints that can be successfully solved by the Z3 solver cannot be handled by
our method. This also shows that our method can complement traditional solvers and expand the
scope of solvable constraints.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 18

834
835
836
837
838
839
840
841
842
843
844
845
846
847
848
849
850
851
852
853
854
855
856
857
858
859
860
861
862
863
864
865
866
867
868
869
870
871
872
873
874
875
876
877
878
879
880
881
882
18
Anon.
Answer to RQ2: Our method demonstrates moderate scalability on standard numeric
benchmarks from SMT-COMP, successfully transforming 6 previously unsolved “unknown”
constraints into satisfiable ones. However, it also shows limitations in some cases, where
concretization increases solving difficulty for instances that Z3 originally solved quickly.
5.5
RQ3: Ablation Study on Component Contributions
Experimental Design and Baseline Methods To the best of our knowledge, there are no existing
methods directly comparable to the proposed method, which integrates RL and LLM to simplify the
constraints by concretizing the variables. To rigorously evaluate the contributions and effectiveness
of each component in our methodology, we conducted a series of ablation studies. These experiments
aim to dissect the individual and combined impacts of the key modules, providing deeper insights
into their roles and verifying the superiority of the proposed RL+LLM method. Specifically, we
compare our RL+LLM method against 4 baseline methods: Random+Random, LLM, Random+LLM,
and RL+Random. The experimental setup consists of the following configurations:
Random+Random: A baseline method where variable assignment and value assignment are both
selected randomly.
LLM: A version of the method where the LLM independently handles both variable assignment
and value assignment, without any reinforcement learning mechanism guiding the search.
Random+LLM: A baseline method where variable assignments are selected randomly, with the
LLM still responsible for generating values based on the chosen assignments.
RL+Random: A baseline method where variable assignment is selected by reinforcement learning,
just the same as RL+LLM, and value assignment is selected randomly.
Quantitative Analysis and Performance Comparison For each configuration, we conduct
experiments on the SMTimer dataset as described in the experimental setup. Figure 5 summarizes
the number of constraints solved by each configuration. RL+LLM (full method) solved 94 constraints
(out of 337), the most of any approach. The purely Random+Random baseline solved 62 constraints,
and interestingly, adding an LLM to random variable selection (Random+LLM) also solved 62
– indicating that without guided variable selection, the LLM alone didn’t improve the count.
The standalone LLM approach (no RL, no guided selection) solved only 30 constraints, the fewest
overall. This stark drop underscores that without RL’s guidance, the LLM cannot effectively navigate
complex constraints.
Time Analysis and Component Synergy Figure 6 shows the solving time distribution for
successful cases of different methods. From the figure, we can see that the RL+LLM method can
solve the largest number of constraints, and at the same time, the solving time is shorter. The
Random+Random and Random+LLM have similar effects, and RL+Random also demonstrates
satisfactory performance, but they are inferior to the RL+LLM method in both solving time and the
number of constraints solved, which also reflects the effectiveness of the proposed method, that is,
the combination of RL and LLM can better solve constraints. In addition, although RL+Random
can solve many constraints, second only to RL+LLM, it takes more time to solve these constraints
compared to other baselines. The LLM method solves the fewest constraints. Although the time it
takes to solve the constraints is short, the main reason is that simply using a large model cannot
explore complex constraints well, so it can only solve simple constraints. For example, only assigning
a value can make the constraint solver run quickly.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 19

883
884
885
886
887
888
889
890
891
892
893
894
895
896
897
898
899
900
901
902
903
904
905
906
907
908
909
910
911
912
913
914
915
916
917
918
919
920
921
922
923
924
925
926
927
928
929
930
931
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
19
0
50
100
150
200
250
300
350
Random+Random
LLM
Random+LLM
RL+Random
RL+LLM
62
62
30
30
62
62
84
84
94
94
275
307
275
253
243
succeed
failed
Fig. 5. The number of solved constraints for different methods.
0
20
40
60
80
0
200
400
600
800
1000
1200
Random+Random (62 solved)
LLM (30 solved)
Random+LLM (62 solved)
RL+Random (84 solved)
RL+LLM (94 solved)
Fig. 6. The solving time distribution for successful cases of different methods.
Answer to RQ3:The ablation study shows that both reinforcement learning and LLM
are essential for performance. For example, RL+Random solves 84 constraints, while LLM
solves only 30, compared to 94 by the full method (RL+LLM), highlighting the importance
of integrating both components.
5.6
RQ4: Multi-Solver Generalizability Analysis
Solver Selection and Experimental Framework While RQ1 demonstrated the effectiveness of
our RL+LLM approach against Z3, a critical question remains: does our method’s success generalize
across different SMT solver architectures? This research question addresses a fundamental concern
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 20

932
933
934
935
936
937
938
939
940
941
942
943
944
945
946
947
948
949
950
951
952
953
954
955
956
957
958
959
960
961
962
963
964
965
966
967
968
969
970
971
972
973
974
975
976
977
978
979
980
20
Anon.
in AI-enhanced systems—whether the benefits are solver-specific or represent a universal enhance-
ment technique. To answer this question, we conduct a comprehensive evaluation across multiple
state-of-the-art SMT solvers, each with distinct architectural designs and optimization strategies.
We evaluate our method with five different SMT solvers:
• Z3: Microsoft’s flagship SMT solver, widely used in industry and academia
• CVC5: The latest version of the CVC solver family, known for strong performance on
arithmetic constraints
• BVParti: A specialized bit-vector constraint solver using partition-based algorithms for
bit-vector arithmetic
• MathSAT: A solver particularly effective for mathematical reasoning and optimization
• AriParti_sync: An open-source solver specialized for arithmetic constraints, available at
https://github.com/shaowei-cai-group/AriParti
Each solver is evaluated both in its standalone configuration and when enhanced with our
RL+LLM method using LLaMA 3.1:70B (based on the superior performance demonstrated in RQ1).
Comprehensive Performance Comparison and Results Table 5 presents the framework
for comprehensive comparison of solver performance across multiple metrics. Currently, we
have complete experimental results for Z3, which demonstrate the effectiveness of our RL+LLM
enhancement. Experiments with other solvers are ongoing and results will be updated as they
become available.
Table 5. Multi-Solver Performance Comparison on SMTimer Dataset
Solver
Total
Solved Constraints
Success Rate (%)
Avg. Time (s)
Baseline
+RL+LLM
Baseline
+RL+LLM
Baseline
+RL+LLM
Z3
337
72
94
21.4
27.9
561
214
CVC5
555
113
357
20.4
64.3
1059
347
BVParti
33
2
19
6.1
57.6
694
100
MathSAT
150
35
67
23.3
44.7
757
450
AriParti_sync
–
–
–
–
–
–
–
Dataset Composition and Solver-Specific Constraints Before analyzing the enhancement
patterns, it is important to explain the variation in constraint counts across different solvers shown
in Table 5. All solvers were evaluated using the same filtering criteria: constraints with baseline
solving time greater than 300 seconds and status of either "sat" or "unknown". However, the resulting
dataset sizes differ significantly due to solver-specific characteristics:
• Z3 (337 constraints): As a general-purpose solver, Z3 handles the full range of constraint
types in our dataset, resulting in the largest constraint set.
• CVC5 (555 constraints): CVC5’s arithmetic specialization allows it to process additional
constraints that other solvers cannot handle, leading to the largest dataset.
• BVParti (33 constraints): The significantly smaller dataset reflects two factors: (1) BVParti’s
specialization in bit-vector constraints naturally limits the applicable constraint types, and
(2) implementation limitations where BVParti encountered internal errors on approximately
280+ constraints due to solver-specific bugs, preventing their evaluation. Despite this re-
duced dataset, the results remain statistically significant and demonstrate clear enhancement
patterns.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 21

981
982
983
984
985
986
987
988
989
990
991
992
993
994
995
996
997
998
999
1000
1001
1002
1003
1004
1005
1006
1007
1008
1009
1010
1011
1012
1013
1014
1015
1016
1017
1018
1019
1020
1021
1022
1023
1024
1025
1026
1027
1028
1029
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
21
• MathSAT (150 constraints): The dataset size reflects MathSAT’s specialization in mathemat-
ical reasoning and optimization problems. The solver effectively handles constraints involving
mathematical functions, optimization objectives, and complex arithmetic relationships that
are prevalent in our SMTimer dataset.
These dataset variations reflect the natural diversity of SMT solver capabilities and specializations.
Importantly, our consistent enhancement across all three solvers—despite their different dataset
sizes and architectural focuses—provides strong evidence for the generalizability of our approach.
Enhancement Pattern Analysis and Cross-Solver Insights Table 5 demonstrates our method’s
effectiveness across different solver architectures. We have completed comprehensive evaluations
for Z3, CVC5, and BVParti, revealing consistent enhancement patterns:
• Z3 Enhancement: Our RL+LLM method improves Z3’s success rate from 21.4% to 27.9%
(+6.5
• CVC5 Enhancement: More dramatically, CVC5 shows substantial improvement from 20.4
• BVParti Enhancement: Most remarkably, BVParti demonstrates exceptional improvement
from 6.1% to 57.6% success rate (+51.5 percentage points, 850% relative improvement) with
85.6% time reduction.
• MathSAT Enhancement: Significantly, MathSAT shows substantial improvement from
23.3% to 44.7% success rate (+21.3 percentage points, 91.4% relative improvement) with
average time reduction from 757s to 450s (40.5
• Consistent Improvement Pattern: All four solvers demonstrate significant performance
gains, indicating our approach addresses fundamental constraint solving challenges rather
than exploiting solver-specific characteristics.
• Architecture-Agnostic Benefits: The consistent improvements across different solver ar-
chitectures (general-purpose Z3, arithmetic-specialized CVC5, bit-vector-specialized BVParti,
and mathematical-reasoning-specialized MathSAT) validate our method’s universal applica-
bility.
SuperVenn Analysis and Detailed Case Studies To provide deeper insights into how our
RL+LLM method enhances different solvers, we employ SuperVenn diagrams to visualize the solving
capability relationships. These diagrams reveal not only the quantitative improvements but also
the complementary nature of baseline solvers and their enhanced versions.
Z3 Enhancement Analysis Figure 7 presents a SuperVenn analysis of Z3’s enhancement,
showing that our method solved 94 constraints compared to Z3’s baseline 72 constraints (30.6
We examined one representative constraint from the 23 Z3+RL+LLM-exclusive cases in detail.
This constraint involves 47 integer variables with complex arithmetic relationships including
modular operations, conditional expressions, and nested quantifications. The constraint defines
multiple helper functions for range checking and arithmetic validation, with assertions that impose
intricate dependencies between variables through chains of implications and equivalences. The
overall objective is to determine satisfiability of a system where variables must satisfy simultaneous
linear and nonlinear arithmetic constraints with strict bounds checking.
Z3 baseline failed on this constraint due to the combinatorial explosion in the search space—with
47 variables each having large integer domains, the traditional symbolic approach struggled to
efficiently explore the constraint space within the timeout. Our RL+LLM approach succeeded by
strategically concretizing 19 key variables (identified through RL guidance) in 3 candidate sequences
over 892 seconds. The final sequence enabled Z3 to solve the simplified constraint in just 8 seconds,
demonstrating how guided concretization can transform intractable problems into manageable
ones.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 22

1030
1031
1032
1033
1034
1035
1036
1037
1038
1039
1040
1041
1042
1043
1044
1045
1046
1047
1048
1049
1050
1051
1052
1053
1054
1055
1056
1057
1058
1059
1060
1061
1062
1063
1064
1065
1066
1067
1068
1069
1070
1071
1072
1073
1074
1075
1076
1077
1078
22
Anon.
ITEMS
SETS
Z3 + RL+LLM
Z3 Baseline
1
71
23
Z3 Solving Capability Comparison
1
2
1
94
72
Fig. 7. SuperVenn analysis of Z3 baseline vs RL+LLM enhanced solving capability. The diagram shows
1 constraints solved exclusively by baseline, 23 constraints solved exclusively by RL+LLM enhancement,
and 71 constraints solved by both methods. Total improvement: 72 →94 (+22 constraints, 30.6% relative
improvement).
CVC5 Enhancement Analysis Figure 8 shows an even more dramatic enhancement for CVC5,
with our RL+LLM method solving 360 constraints compared to CVC5’s baseline 228 constraints
(57.9
We analyzed a representative constraint from the 317 CVC5+RL+LLM-exclusive cases. This con-
straint defines 38 real-valued variables with complex polynomial relationships, including quadratic
terms, trigonometric functions, and transcendental equations. The constraint system involves si-
multaneous nonlinear equations with strict inequality bounds, where variables represent geometric
coordinates that must satisfy both algebraic constraints (polynomial equalities) and geometric
constraints (distance and angle relationships). The assertions include nested conditional statements
that create multiple solution branches, each requiring different variable assignment strategies.
CVC5 baseline struggled with this constraint because its arithmetic decision procedures, while
powerful for linear arithmetic, face exponential complexity when handling the combination of
nonlinear terms and branching conditions. The constraint’s 38 real variables create a continuous
search space that traditional symbolic methods cannot efficiently explore. Our RL+LLM approach
succeeded by identifying 14 critical variables through RL guidance and generating 4 candidate
assignment sequences over 1,247 seconds. The successful sequence concretized these key variables,
reducing the problem to a linear system that CVC5 solved in 23 seconds. This demonstrates
how strategic variable concretization can transform nonlinear problems into CVC5’s strength
domain—linear arithmetic.
BVParti Enhancement Analysis
To further validate the generalizability of our RL+LLM approach across different solver architec-
tures, we conducted experiments with BVParti, a specialized bit-vector constraint solver. BVParti
represents a different architectural approach compared to general-purpose SMT solvers like Z3 and
CVC5, focusing specifically on bit-vector arithmetic and partition-based solving strategies.
The BVParti evaluation dataset consists of 33 bit-vector constraints, significantly smaller than
the Z3 (337) and CVC5 (555) datasets. This reduction reflects two key factors: (1) BVParti’s special-
ization in bit-vector constraints naturally limits the applicable constraint types from our SMTimer
dataset, and (2) solver implementation limitations where BVParti encountered internal errors on
approximately 280+ constraints due to solver-specific bugs in handling certain bit-vector opera-
tions, preventing their evaluation. Despite this reduced dataset size, the 33 constraints provide a
representative sample of challenging bit-vector problems that meet our filtering criteria (>300s
solving time, sat/unknown status).
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 23

1079
1080
1081
1082
1083
1084
1085
1086
1087
1088
1089
1090
1091
1092
1093
1094
1095
1096
1097
1098
1099
1100
1101
1102
1103
1104
1105
1106
1107
1108
1109
1110
1111
1112
1113
1114
1115
1116
1117
1118
1119
1120
1121
1122
1123
1124
1125
1126
1127
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
23
ITEMS
SETS
CVC5 + RL+LLM
CVC5 Baseline
185
43
317
CVC5 Solving Capability Comparison
1
2
1
360
228
Fig. 8. SuperVenn analysis of CVC5 baseline vs RL+LLM enhanced solving capability. The diagram shows
185 constraints solved exclusively by baseline, 317 constraints solved exclusively by RL+LLM enhancement,
and 43 constraints solved by both methods. Total improvement: 228 →360 (+132 constraints, 57.9% relative
improvement).
Our experiments on these 33 bit-vector constraints demonstrate exceptional improvements: from
2 (6.1%) to 19 (57.6%) solved constraints, representing a 51.5 percentage point improvement (850%
relative improvement). Figure 9 illustrates this dramatic enhancement, showing that 17 constraints
were solved exclusively by RL+LLM enhancement, demonstrating the method’s ability to tackle
cases where traditional bit-vector solving fails, while 2 constraints were solved by both baseline
and enhanced methods, showing preservation of existing solver capabilities.
The BVParti results are particularly significant because they demonstrate our method’s effective-
ness on a specialized solver architecture. Unlike general-purpose SMT solvers, BVParti employs
partition-based algorithms specifically designed for bit-vector constraints. The 51.5% improvement
in success rate validates that RL+LLM enhancement transcends solver-specific optimizations and
provides fundamental improvements in constraint simplification.
ITEMS
SETS
BVParti + RL+LLM
BVParti Baseline
2
17
BVParti Solving Capability Comparison
2
1
19
2
Fig. 9. SuperVenn analysis of BVParti baseline vs RL+LLM enhanced solving capability. The diagram shows
0 constraints solved exclusively by baseline, 17 constraints solved exclusively by RL+LLM enhancement,
and 2 constraints solved by both methods. Total improvement: 2 →19 (+17 constraints, 850.0% relative
improvement).
The SuperVenn analyses reveal consistent enhancement patterns across all evaluated solvers,
with architecture-specific variations. Z3 shows a 30.6
MathSAT Enhancement Analysis
To further validate our approach’s effectiveness across different solver architectures, we con-
ducted experiments with MathSAT, a solver particularly effective for mathematical reasoning
and optimization problems. MathSAT represents another distinct architectural approach in the
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 24

1128
1129
1130
1131
1132
1133
1134
1135
1136
1137
1138
1139
1140
1141
1142
1143
1144
1145
1146
1147
1148
1149
1150
1151
1152
1153
1154
1155
1156
1157
1158
1159
1160
1161
1162
1163
1164
1165
1166
1167
1168
1169
1170
1171
1172
1173
1174
1175
1176
24
Anon.
SMT solving landscape, with specialized algorithms for handling mathematical constraints and
optimization queries.
Our experiments on 150 mathematical reasoning constraints demonstrate significant improve-
ments: from 35 (23.3%) to 67 (44.7%) solved constraints, representing a 21.3 percentage point
improvement (91.4% relative improvement). Figure 10 illustrates this enhancement, showing that 35
constraints were solved exclusively by RL+LLM enhancement, demonstrating the method’s ability
to tackle mathematical reasoning problems where traditional solving approaches struggle, while 32
constraints were solved by both baseline and enhanced methods, showing preservation of existing
solver capabilities.
ITEMS
SETS
MathSAT + RL+LLM
MathSAT Baseline
3
32
35
MathSAT Solving Capability Comparison
1
2
1
67
35
Fig. 10. SuperVenn analysis of MathSAT baseline vs RL+LLM enhanced solving capability. The diagram shows
3 constraints solved exclusively by baseline, 35 constraints solved exclusively by RL+LLM enhancement,
and 32 constraints solved by both methods. Total improvement: 35 →67 (+32 constraints, 91.4% relative
improvement).
The MathSAT results are particularly significant because they demonstrate our method’s ef-
fectiveness on mathematical reasoning and optimization problems. Unlike general-purpose SMT
solvers, MathSAT employs specialized algorithms for mathematical constraints and optimization
queries. The 91.4% improvement in success rate validates that RL+LLM enhancement is effective
across mathematical reasoning domains and provides fundamental improvements in constraint
simplification for optimization problems.
Cross-Solver Architecture Analysis
Our comprehensive evaluation across four distinct solver architectures (Z3, CVC5, BVParti,
and MathSAT) reveals fundamental insights about the universality of our RL+LLM enhancement
approach:
• General-Purpose Solvers (Z3): Demonstrate steady, reliable improvements with high ca-
pability preservation, validating the method’s effectiveness on well-optimized, mature solver
architectures.
• Arithmetic-Specialized Solvers (CVC5, MathSAT): Show substantial improvements in
their specialized domains, indicating that our method complements rather than conflicts with
domain-specific optimizations.
• Bit-Vector Specialized Solvers (BVParti): Exhibit the most dramatic improvements, sug-
gesting that our approach is particularly effective in specialized constraint domains where
traditional solving approaches face fundamental limitations.
• Architecture-Agnostic Benefits: The consistent improvement patterns across all architec-
tures provide compelling evidence that our method addresses fundamental constraint solving
challenges rather than exploiting solver-specific characteristics.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 25

1177
1178
1179
1180
1181
1182
1183
1184
1185
1186
1187
1188
1189
1190
1191
1192
1193
1194
1195
1196
1197
1198
1199
1200
1201
1202
1203
1204
1205
1206
1207
1208
1209
1210
1211
1212
1213
1214
1215
1216
1217
1218
1219
1220
1221
1222
1223
1224
1225
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
25
Note: Experiments with AriParti_sync are currently in progress and will be added to provide a
complete picture of arithmetic solver enhancement patterns.
Answer to RQ4: Our comprehensive analysis across Z3, CVC5, BVParti, and MathSAT
demonstrates exceptional generalizability of the RL+LLM enhancement method. Z3 shows
30.6
Extended Multi-Solver Analysis and Future Work Our ongoing comprehensive evaluation
includes detailed analysis of solver-specific performance patterns, constraint type preferences, and
the interaction between different solver architectures and our RL+LLM enhancement method. This
extended analysis will provide deeper insights into:
• Constraint Type Specialization: How different solvers perform on specific constraint
categories (linear vs. nonlinear arithmetic, bit-vectors, etc.) and how our method adapts to
these specializations.
• Solver Architecture Impact: The relationship between solver design principles and the
effectiveness of our enhancement approach.
• Complementary Solver Combinations: Potential for combining multiple enhanced solvers
to achieve even better overall performance.
• Resource Utilization Patterns: Memory and computational overhead analysis across dif-
ferent solver configurations.
These results will be incorporated into the final version of this paper, providing a comprehensive
view of how our RL+LLM method enhances the broader SMT solving ecosystem.
5.7
RQ5: Complexity-Guided Routing System Evaluation
To demonstrate the practical effectiveness of our RL+LLM approach in realistic deployment scenar-
ios, we simulate a production environment that realistically models real-world deployment where
constraints arrive without prior knowledge of their solving difficulty. This evaluation addresses a
critical question for real-world deployment: can predictive models effectively guide the selection
between direct solving and RL+LLM simplification to achieve overall system improvements?
Dataset and Model Consistency
For experimental consistency across research questions, RQ5 uses the same QF_NIA dataset
as RQ2, maintaining identical experimental conditions and enabling direct comparison of results.
The complete dataset contains 10,043 constraints for testing the routing system performance, with
the predictive models having been trained on separate training data that was excluded from this
evaluation set. This ensures that the predictive models used in RQ5 are identical to those validated
in RQ2, providing experimental consistency and reliability.
Predictive Model Specification
The routing system employs two predictive models with identical architecture and training
parameters as established in RQ2:
• Binary Classification Model: Predicts constraint solvability (SAT vs. non-SAT) to identify
potentially satisfiable constraints
• Time Estimation Model: Predicts expected solving difficulty for routing decisions, using
the same threshold-based approach (≥4) validated in RQ2
Hybrid Routing System Evaluation
The evaluation focuses on demonstrating that our hybrid RL+LLM approach reduces overall
solving time compared to using traditional solvers alone, while maintaining or improving solution
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 26

1226
1227
1228
1229
1230
1231
1232
1233
1234
1235
1236
1237
1238
1239
1240
1241
1242
1243
1244
1245
1246
1247
1248
1249
1250
1251
1252
1253
1254
1255
1256
1257
1258
1259
1260
1261
1262
1263
1264
1265
1266
1267
1268
1269
1270
1271
1272
1273
1274
26
Anon.
quality across different constraint satisfiability outcomes. The system implements the following
workflow:
(1) Predictive Assessment: For each constraint in the test set, the system applies the trained
predictive models to estimate:
• Solvability: Binary classification to predict SAT vs. non-SAT status
• Difficulty: Time estimation to determine routing decisions using the validated threshold (≥
4)
(2) Routing Decision: Based on the predictive assessment:
• Predicted Easy (prediction < 4): Process with direct SMT solving
• Predicted Hard (prediction ≥4): Apply RL+LLM simplification followed by solving
(3) Performance Evaluation: The system effectiveness is measured through:
• Solution Quality: Counts of SAT, UNSAT, and UNKNOWN outcomes for each approach
• Time Efficiency: Average solving time for SAT instances and overall system performance
• Selective Enhancement: Percentage of constraints benefiting from RL+LLM processing
Experimental Results and Time Reduction Analysis
Table 6 presents a comprehensive comparison between direct solving and our hybrid routing ap-
proach, demonstrating the time reduction benefits achieved through selective RL+LLM application
while maintaining solution quality across all satisfiability categories.
Table 6. Performance comparison between direct solving and hybrid routing on QF_NIA test set (10,043
constraints)
Strategy
SAT
UNSAT
UNKNOWN
SAT Avg.
Overall Avg.
Total Time
Count
Count
Count
Time (s)
Time (s)
(s)
Direct Solving
6,711
792
2,540
28.3
36.6
367,374
Hybrid Routing
6,792
792
2,459
24.7
32.2
323,386
The hybrid routing system demonstrates significant time reduction benefits while maintaining
solution quality. Compared to direct solving alone, the hybrid approach achieves a 12.6% reduction in
average solving time for SAT instances (from 28.3s to 24.7s) and an 11.9% reduction in overall average
time (from 36.6s to 32.2s). Most importantly, the total solving time across all 10,043 constraints
is reduced from 367,374 seconds to 323,386 seconds, representing a substantial 11.9% reduction
in cumulative solving time (43,988 seconds saved). Additionally, the system solves 81 more SAT
instances (6,792 vs. 6,711), demonstrating that selective RL+LLM application not only improves
efficiency but also enhances solution capability. The system correctly handles timeout cases, with
2,540 constraints marked as UNKNOWN in the baseline and 2,459 in the hybrid approach, reflecting
the conversion of 81 timeout cases to successful SAT solutions.
Time Reduction Analysis by Satisfiability Category
The hybrid routing system achieves time reduction benefits across different constraint satisfia-
bility outcomes:
• SAT Instances: The hybrid approach solves 81 additional SAT instances (6,792 vs. 6,711)
while reducing average solving time by 12.6% (3.6 seconds saved per SAT instance on average)
• UNSAT Instances: The count remains stable (792 instances), demonstrating that the hybrid
approach maintains UNSAT detection capability while focusing on converting timeout cases
to SAT solutions
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 27

1275
1276
1277
1278
1279
1280
1281
1282
1283
1284
1285
1286
1287
1288
1289
1290
1291
1292
1293
1294
1295
1296
1297
1298
1299
1300
1301
1302
1303
1304
1305
1306
1307
1308
1309
1310
1311
1312
1313
1314
1315
1316
1317
1318
1319
1320
1321
1322
1323
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
27
• UNKNOWN Instances: The hybrid approach reduces UNKNOWN cases from 2,540 to 2,459
(81 fewer), converting these timeout cases into successful SAT solutions through RL+LLM
enhancement
• Overall Efficiency: The 11.9% reduction in overall average time (4.4 seconds saved per
constraint) demonstrates system-wide efficiency gains with a 1200s timeout threshold
• Total Time Savings: The cumulative time reduction from 367,374s to 323,386s (43,988
seconds saved) represents significant computational resource savings equivalent to approxi-
mately 12.2 hours of processing time
Selective RL+LLM Application Analysis
The predictive models successfully identify a small subset of constraints (0.8% of the test set) that
benefit from RL+LLM processing. This selective application achieves the optimal balance between
computational efficiency and performance enhancement, demonstrating that strategic RL+LLM
deployment provides practical value without overwhelming system resources.
Practical Deployment Benefits
The experimental results validate several key benefits of the hybrid routing approach for practical
deployment:
(1) Significant Time Reduction: The 12.6% reduction in SAT solving time (3.6 seconds saved
per SAT instance) and 11.9% reduction in overall time (4.4 seconds saved per constraint)
demonstrate substantial efficiency gains. The total time savings of 43,988 seconds (12.2 hours)
across the complete test set translate directly to improved system throughput in production
environments.
(2) Enhanced Solution Capability: The system solves 81 additional SAT instances by convert-
ing timeout cases (UNKNOWN) to successful solutions, proving that RL+LLM enhancement
expands the solver’s capability to handle challenging constraints within the 1200s timeout
limit.
(3) Resource-Efficient Enhancement: By applying RL+LLM to only 0.8% of constraints, the
system achieves significant performance gains while maintaining computational efficiency
suitable for production deployment.
Answer to RQ5: Our hybrid RL+LLM routing system demonstrates significant time re-
duction benefits compared to traditional solving approaches. Using the complete QF_NIA
test set (10,043 constraints) with a 1200s timeout threshold and predictive models validated
in RQ2, the hybrid approach achieves a 12.6% reduction in average solving time for SAT
instances (3.6 seconds saved per instance) and an 11.9% reduction in overall system time
(4.4 seconds saved per constraint). The cumulative time savings of 43,988 seconds (12.2
hours) across the entire test set demonstrate substantial computational efficiency gains.
Additionally, the system solves 81 more SAT instances by converting timeout cases to
successful solutions, while applying RL+LLM to only 0.8% of constraints. This demonstrates
that selective enhancement provides substantial efficiency gains and improved solution
capability, correctly handling the 1200s timeout constraint where 2,540 cases are marked as
UNKNOWN in the baseline. The results validate that our hybrid approach reduces overall
solving time while maintaining solution quality across all satisfiability categories, making
it highly suitable for production deployment scenarios.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 28

1324
1325
1326
1327
1328
1329
1330
1331
1332
1333
1334
1335
1336
1337
1338
1339
1340
1341
1342
1343
1344
1345
1346
1347
1348
1349
1350
1351
1352
1353
1354
1355
1356
1357
1358
1359
1360
1361
1362
1363
1364
1365
1366
1367
1368
1369
1370
1371
1372
28
Anon.
6
DISCUSSION
In this section, we summarize the major lessons and takeaways that we have learned from conduct-
ing this work.
6.1
Robustness and Limitations
While the proposed method demonstrates notable solving time reductions on structured constraints,
its robustness varies. The RL agent’s effectiveness depends on the representativeness of the training
set; unexpected constraint types may lead to poor variable selection. Furthermore, the LLM’s output
quality can vary, and it may sometimes propose incorrect values. We mitigate this by having the
solver verify each LLM-suggested assignment, but those extra solver invocations do add overhead.
Moreover, our method is less effective on purely linear constraints, where concretization provides
minimal benefit.
6.2
Threats to Validity
Several potential threats to the validity of our findings should be considered in interpreting the
experimental results. First, regarding internal validity, our experiments are conducted using a single
large language model (LLaMA 3.1:70B) and a fixed reinforcement learning configuration. Although
we repeat each experiment five times to reduce variance, both LLM output and RL exploration
introduce randomness that could affect result stability. This limitation suggests that performance
improvements observed may not generalize across different seeds or model versions.
Second, in terms of external validity, our evaluation focuses on numerical constraints from the
SMTimer and SMT-COMP datasets, particularly QF-LIA and QF-NIA logic. While these benchmarks
reflect real-world verification tasks involving nonlinear arithmetic and modular expressions, they
do not include other key theories such as arrays, bit-vectors, or uninterpreted functions. As a result,
the effectiveness of our method may vary when applied to constraint domains outside this scope.
Third, construct validity is influenced by the metrics used to assess solving performance. Our
primary measures—solving time and success rate—are solver-centric and closely tied to Z3’s internal
behavior. However, different solvers (e.g., CVC5, Bitwuzla) may respond differently to concretization
due to variations in decision heuristics and search strategies. Therefore, while our results are robust
for Z3-based workflows, they may not fully capture performance across all symbolic reasoning
systems.TODO:update when get the CVC5’s result
Finally, conclusion validity may be affected by the timeout threshold used during evalua-
tion. We adopt the standard 1200-second limit, but this choice can influence outcome interpreta-
tion—especially for complex constraints where small changes in timeout settings lead to different
solving behaviors. To address this, we analyze results across multiple time intervals and observe
consistent trends, which supports the reliability of our conclusions within the chosen setup.
These threats highlight the importance of diverse experimental design, cross-solver validation,
and rigorous benchmarking when integrating machine learning into symbolic reasoning pipelines.
6.3
Implications and Future Directions
Our findings illustrate the potential for integrating learned heuristics into constraint solving
pipelines. The RL+LLM framework aligns with recent trends in neuro-symbolic methods, combining
neural network predictions with symbolic reasoning. Future work could focus on:
• Learning more informative reward signals, potentially using LLMs to shape rewards based
on natural language task descriptions [43].
• Fine-tuning specialized LLMs on SMT formulas to improve output accuracy and reduce
computational overhead.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 29

1373
1374
1375
1376
1377
1378
1379
1380
1381
1382
1383
1384
1385
1386
1387
1388
1389
1390
1391
1392
1393
1394
1395
1396
1397
1398
1399
1400
1401
1402
1403
1404
1405
1406
1407
1408
1409
1410
1411
1412
1413
1414
1415
1416
1417
1418
1419
1420
1421
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
29
• Extending the framework to handle quantified constraints, non-linear arithmetic, and more
complex theories, such as UFNIA or AUFNIRA.
• Developing hybrid agents that combine RL with supervised learning from expert solver
traces, enabling more accurate policy initialization.
Our work highlights the promising intersection of AI and symbolic reasoning, suggesting new
avenues for integrating machine learning into formal verification and SMT-solving workflows.
7
Related Work
SMT solving performance is the primary bottleneck in symbolic execution [8, 34, 45], particularly
for complex constraints involving bit-vectors and non-linear arithmetic [6]. Existing approaches
address this challenge through four main strategies: path-level optimization, solver enhancement,
constraint simplification, and machine learning integration. Our work introduces a novel RL+LLM
approach for semantic-aware constraint simplification.
7.1
Path-Level Optimization
Path-level approaches avoid complex constraints by steering exploration away from difficult paths.
Hybrid fuzzing [12, 31, 37, 48] combines symbolic execution with fuzzing for complementary
strengths. RL-based path selection [17, 29, 42] learns intelligent exploration strategies, while ML-
guided approaches [5, 7] predict path complexity. However, these techniques are fundamentally
palliative—they avoid difficult constraints rather than solving them.
7.2
Solver-Level Enhancement
Solver enhancement approaches modify SMT solvers directly. Algorithm selection methods [6, 32]
use ML to optimize solver configurations and predict solving times. Internal modifications include
neural branching heuristics [20, 40] and distributed architectures [49] that partition constraints
across multiple instances. Neural solvers [1, 33] attempt complete replacement but struggle with
complex problems. These approaches are orthogonal to ours—they build better solvers while we
simplify problems for existing solvers.
7.3
Constraint-Level Simplification
Constraint simplification approaches use AI to transform constraints before solving. Deep learning
methods [11, 41, 46] apply neural networks for constraint prediction and strategy synthesis. Spe-
cialized approaches target specific constraint types [22, 35], while hybrid methods [28] combine
multiple AI paradigms.
LLM-Based Approaches apply large language models to formal reasoning tasks [10, 18]. Recent
work includes SatLM [47] for translating natural language to logical formulas, Logic-LM [30] for
LLM-solver integration, and MCP-Solver [38] for constraint programming. These operate in guess-
and-verify paradigms with scalability limitations.
Our Approach differs fundamentally: we transform constraints through strategic variable
concretization rather than generating candidate solutions, combining RL strategic planning with
LLM semantic generation. Traditional RL approaches [23, 24] focus on tactic selection, while we
learn variable-level simplification policies for semantic-aware constraint reduction.
The reviewed approaches demonstrate various strategies for addressing SMT solving challenges
across different optimization levels. Path-level methods focus on avoiding difficult constraints
through intelligent exploration, while solver-level enhancements improve the internal mechanisms
of SMT solvers. Constraint-level simplification approaches, including recent LLM-based methods,
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 30

1422
1423
1424
1425
1426
1427
1428
1429
1430
1431
1432
1433
1434
1435
1436
1437
1438
1439
1440
1441
1442
1443
1444
1445
1446
1447
1448
1449
1450
1451
1452
1453
1454
1455
1456
1457
1458
1459
1460
1461
1462
1463
1464
1465
1466
1467
1468
1469
1470
30
Anon.
aim to transform constraints before they reach the solver. Each category offers complementary ben-
efits, with path-level methods providing immediate avoidance of complexity, solver enhancements
offering broad applicability, and constraint simplification enabling targeted problem reduction. Our
work contributes to the constraint-level simplification category through a novel hybrid approach
that combines multiple AI techniques for semantic-aware constraint transformation.
8
Conclusion
Our RL+LLM simplification technique is most advantageous on symbolic constraints where solver
runtime becomes a significant bottleneck. Our method similarly reduces redundant subexpressions
through guided concretization. The approach is particularly effective when constraints exhibit
structured patterns or loose bounds that an LLM can exploit. For instance, Wanget al. demon-
strate that LLM-based code generation can translate complex Python path constraints into Z3
queries, enabling the solver to handle previously unsolvable cases [39]. This suggests that our LLM
concretization can help in domains with non-linear arithmetic or string-heavy formulas, where
conventional solvers may struggle.
Our comprehensive evaluation demonstrates that the RL+LLM method significantly outperforms
baseline approaches across multiple dimensions. On the SMTimer dataset, our method solved 94
out of 337 challenging constraints (27.9%) compared to Z3’s 72 solutions (21.4%), representing a
30.6% improvement in success rate. More importantly, our approach achieved a 62% reduction in
average solving time (214s vs. 561s) for successfully solved instances.
Our work’s key technical achievements include a novel hybrid architecture that systematically
decomposes SMT solving into strategic variable selection (RL) and semantic value generation
(LLM); a predictive guidance framework that improves RL training efficiency; and an advanced
memory management system that reduces redundant exploration. The method’s scalability has
been demonstrated on both real-world and standard benchmarks.
While promising, we acknowledge its practical limitations. The computational overhead of LLM
inference is best suited for complex constraints where solver time is a bottleneck (e.g., >300s). The
approach is also most effective on constraints with structured patterns and requires substantial
data and resources for initial RL policy training, although the resulting policies generalize well.
In summary, our RL+LLM constraint simplification framework represents a significant advance-
ment in addressing the SMT bottleneck, offering both theoretical novelty and practical improve-
ments for complex constraint solving scenarios.
References
[1] Marcelo Abreu, Rafael Giusti, Marcos Maximo, and Mariá CV Nascimento. 2021. Learning to solve NP-complete
problems: A graph neural network for decision TSP. In Advances in Neural Information Processing Systems, Vol. 34.
21054–21066.
[2] Thomas Ball and Sriram K Rajamani. 2004. SLAM and static driver verifier: Technology transfer of formal methods
inside Microsoft. In International Conference on Integrated Formal Methods. Springer, 1–20.
[3] Mike Barnett, Bor-Yuh Evan Chang, Robert DeLine, Bart Jacobs, and K Rustan M Leino. 2005. Static verification of C
programs using Spec#. In International Symposium on Formal Methods. Springer, 325–340.
[4] Clark Barrett, Pascal Fontaine, and Cesare Tinelli. 2017. The SMT-LIB standard: Version 2.6. Release Notes (2017).
[5] Saahil Bessler, Sunjay Cha, Michael Hicks, and Jeffrey S Foster. 2021. Metrinome: Path complexity predicts symbolic
execution path explosion. In Proceedings of the 43rd International Conference on Software Engineering. 1134–1145.
[6] Haniel Bischoff, Haniel Barbosa, Clark Barrett, Martin Brain, Gereon Kremer, Hanna Lachnitt, Makai Mann, Abdalrhman
Mohamed, Mathias Peter, Aina Preiner, et al. 2021. Satisfiability modulo theories competition (SMT-COMP): 2020. In
International Conference on Tools and Algorithms for the Construction and Analysis of Systems. Springer, 374–380.
[7] Lei Bu, Jiaxiang Zhao, Sen Li, and Jun Sun. 2021. Machine learning steered symbolic execution framework for complex
software code. In Proceedings of the 43rd International Conference on Software Engineering. 1112–1123.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 31

1471
1472
1473
1474
1475
1476
1477
1478
1479
1480
1481
1482
1483
1484
1485
1486
1487
1488
1489
1490
1491
1492
1493
1494
1495
1496
1497
1498
1499
1500
1501
1502
1503
1504
1505
1506
1507
1508
1509
1510
1511
1512
1513
1514
1515
1516
1517
1518
1519
Constraint Simplification Approach Based on Reinforcement Learning and Large Language Models
31
[8] Cristian Cadar, Daniel Dunbar, Dawson R Engler, et al. 2008. KLEE: Unassisted and automatic generation of high-
coverage tests for complex systems programs. In OSDI, Vol. 8. 209–224.
[9] Cristian Cadar and Koushik Sen. 2013. Symbolic execution for software testing: three decades later. In Communications
of the ACM, Vol. 56. ACM, 82–90.
[10] Supratik Chakraborty, Dror Fried, Lucas M Tabajara, and Moshe Y Vardi. 2023. Ranking llm-generated loop invariants
for program verification. In arXiv preprint arXiv:2310.09342.
[11] Haoyu Chen, Yinxing Xue, Yuekang Li, Sen Chen, Bihuan Xu, Yang Feng, and Lei Ma. 2021. Synthesize solving strategy
for symbolic execution. In Proceedings of the 43rd International Conference on Software Engineering. 1022–1034.
[12] Peng Chen, Jianzhong Liu, and Hao Chen. 2023. Baton: symphony of random testing and concolic testing. In Proceedings
of the 45th International Conference on Software Engineering. 1567–1578.
[13] Leonardo De Moura and Nikolaj Bjørner. 2008. Z3: An efficient SMT solver. In International conference on Tools and
Algorithms for the Construction and Analysis of Systems. Springer, 337–340.
[14] Leonardo De Moura and Nikolaj Bjørner. 2008. Z3: An efficient SMT solver. In International conference on Tools and
Algorithms for the Construction and Analysis of Systems. Springer, 337–340.
[15] Patrice Godefroid, Nils Klarlund, and Koushik Sen. 2005. DART: directed automated random testing. In ACM SIGPLAN
Notices, Vol. 40. ACM, 213–223.
[16] Tuomas Haarnoja, Aurick Zhou, Pieter Abbeel, and Sergey Levine. 2018. Soft actor-critic: Off-policy maximum entropy
deep reinforcement learning with a stochastic actor. In International conference on machine learning. PMLR, 1861–1870.
[17] Jingxuan He, Mislav Balunovic, Gagandeep Kuchta, and Martin Vechev. 2021. Learning to Explore Paths for Symbolic
Execution. In Proceedings of the 2021 ACM SIGSAC Conference on Computer and Communications Security. 1279–1294.
[18] Adharsh Kamath, Aditya Senthilnathan, Supratik Chakraborty, Kuldeep S Meel, and Moshe Y Vardi. 2023. Finding
inductive loop invariants using large language models. In arXiv preprint arXiv:2311.07948.
[19] James C King. 1976. Symbolic execution and program testing. In Communications of the ACM, Vol. 19. ACM, 385–394.
[20] Vitaly Kurin, Saad Godil, Shimon Whiteson, and Bryan Catanzaro. 2020. Improving SAT solver heuristics with graph
networks and reinforcement learning. In arXiv preprint arXiv:2001.07105.
[21] Elias Liang, Richard Liaw, Robert Nishihara, Philipp Moritz, Roy Fox, Ken Goldberg, Joseph E Gonzalez, Michael I
Jordan, and Ion Stoica. 2016. Learning to branch in mixed integer programming. In AAAI Conference on Artificial
Intelligence.
[22] Peisen Liu, Jiaxiang Zhao, and Jun Sun. 2022. Optimal Refinement-based Array Constraint Solving for Symbolic
Execution. In Proceedings of the 44th International Conference on Software Engineering. 1456–1467.
[23] Haiming Luo, Haoxiong Chang, Qingxing Huang, Jing Shi, Yinya Zhang, and Lei Li. 2022. Learning to prove theorems
by learning to generate theorems. arXiv preprint arXiv:2205.11916 (2022).
[24] Haiming Luo, Haoxiong Chang, Qingxing Huang, Jing Shi, Yinya Zhang, and Lei Li. 2023. Learning to prove theorems
by learning to generate theorems. In International Conference on Machine Learning. PMLR, 22278–22300.
[25] Yannic Luo, Alberto Griggio, and Alessandro Cimatti. 2021. Boosting symbolic execution via constraint solving time
prediction. In International Conference on Automated Software Engineering. 1–13.
[26] Yannic Luo, Mark Harman, and Yue Jia. 2021. Boosting symbolic execution via constraint solving time prediction. In
Proceedings of the 43rd International Conference on Software Engineering. 1078–1089.
[27] Sergey Mechtaev, Xiang Gao, Abhik Roychoudhury, and Satish Chandra. 2018. Semantic program repair using a
reference implementation. In Proceedings of the 40th International Conference on Software Engineering. 129–139.
[28] Malay Keshav Muduli and Subhajit Roy. 2022. Satisfiability modulo fuzzing: a synergistic combination of SMT solving
and fuzzing. In Proceedings of the 44th International Conference on Software Engineering. 1678–1689.
[29] Ciprian Paduraru, Mihai-Cristian Melemciuc, and Alin Stefanescu. 2020. Optimizing decision making in concolic
execution using reinforcement learning. In Proceedings of the 2020 Genetic and Evolutionary Computation Conference.
1423–1431.
[30] Liangming Pan, Alon Albalak, Xinyi Wang, and William Yang Wang. 2023. Logic-LM: Empowering Large Language
Models with Symbolic Solvers for Faithful Logical Reasoning. In Findings of the Association for Computational Linguistics:
EMNLP 2023. Association for Computational Linguistics, 3806–3824.
[31] Sanjay Rawat, Vivek Jain, Ashish Kumar, Lucian Cojocar, Cristiano Giuffrida, and Herbert Bos. 2017.
VUzzer:
Application-aware evolutionary fuzzing. In Proceedings of the 2017 Network and Distributed System Security Symposium.
[32] Joseph Scott, Aina Niemetz, Mathias Preiner, Saeed Nejati, and Vijay Ganesh. 2023. Algorithm selection for SMT. In
Proceedings of the 2023 ACM SIGPLAN International Symposium on Memory Management. 1–15.
[33] Daniel Selsam, Matthew Lamm, Benedikt Bunz, Percy Liang, Leonardo de Moura, and David L Dill. 2019. Learning a
SAT solver from single-bit supervision. In International Conference on Learning Representations.
[34] Koushik Sen, Darko Marinov, and Gul Agha. 2005. CUTE: a concolic unit testing engine for C. In ACM SIGSOFT
Software Engineering Notes, Vol. 30. ACM, 263–272.
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

## Page 32

1520
1521
1522
1523
1524
1525
1526
1527
1528
1529
1530
1531
1532
1533
1534
1535
1536
1537
1538
1539
1540
1541
1542
1543
1544
1545
1546
1547
1548
1549
1550
1551
1552
1553
1554
1555
1556
1557
1558
1559
1560
1561
1562
1563
1564
1565
1566
1567
1568
32
Anon.
[35] Jiawei Shuai, Chengpeng Wang, and Zhendong Su. 2021. Type and interval aware array constraint solving for symbolic
execution. In Proceedings of the 43rd International Conference on Software Engineering. 1090–1101.
[36] Armando Solar-Lezama. 2008. Program synthesis by sketching. In PhD thesis, UC Berkeley.
[37] Nick Stephens, John Grosen, Christopher Salls, Andrew Dutcher, Ruoyu Wang, Jacopo Corbetta, Yan Shoshitaishvili,
Christopher Kruegel, and Giovanni Vigna. 2016. Driller: Augmenting fuzzing through selective symbolic execution. In
25th USENIX Security Symposium. 1051–1066.
[38] Stefan Szeider. 2025. MCP-Solver: Integrating Language Models with Constraint Programming Systems. arXiv preprint
arXiv:2501.00539 (2025).
[39] Rongxin Wang, Zhiwei Yan, Jiaxi Wang, Tao Song, Xiaodan Zhang, and Shing-Chi Cheung. 2024. Can Large Language
Models Reason About Program Invariants? arXiv preprint arXiv:2401.16407 (2024).
[40] Wenxi Wang, Yangzihao Yang, Qingyu Li, Yang Wang, Chenyang Liu, and Holger H Hoos. 2021. NeuroComb: Improving
SAT solving with graph neural networks. In arXiv preprint arXiv:2110.14053.
[41] Ming Wen, Junjie Chen, Rongxin Wu, Dan Hao, and Shing-Chi Cheung. 2020. Constraint Solving with Deep Learning
for Symbolic Execution. In Proceedings of the 2020 28th ACM Joint Meeting on European Software Engineering Conference
and Symposium on the Foundations of Software Engineering. 1034–1045.
[42] Junjie Wu, Zhiqiang Tang, Qingkai Zeng, and Peng Wang. 2020. Reinforcement Learning Guided Symbolic Execution.
In Proceedings of the 35th IEEE/ACM International Conference on Automated Software Engineering. 1129–1141.
[43] Tianbao Xie, Siheng Zhao, Chen Henry Wu, Yitao Liu, Qian Luo, Victor Zhong, Yiming Yang, and Tao Yu.
2023. Text2Reward: Automated dense reward function generation for reinforcement learning. In arXiv preprint
arXiv:2309.11489.
[44] Kaiyu Yang and Jia Deng. 2018. Deep learning for program synthesis. In arXiv preprint arXiv:1809.04682.
[45] Xuejun Yang, Yang Chen, Eric Eide, and John Regehr. 2011. CSmith: a random generator of C programs. In ACM
SIGPLAN Notices, Vol. 46. ACM, 430–440.
[46] Zixi Yang, Chengpeng Wang, Kailong Zhang, and Xiangshan Li. 2024. Exploring strategies for guiding symbolic
analysis with machine learning prediction. In Proceedings of the 46th International Conference on Software Engineering.
1234–1245.
[47] Xi Ye, Qiaochu Chen, Isil Dillig, and Greg Durrett. 2023. SatLM: Satisfiability-Aided Language Models Using Declarative
Prompting. In Advances in Neural Information Processing Systems, Vol. 36. Curran Associates, Inc., 20393–20411.
[48] Insu Yun, Sangho Lee, Meng Xu, Yeongjin Jang, and Yunheung Paek. 2018. QSYM: A practical concolic execution
engine tailored for hybrid fuzzing. In 27th USENIX Security Symposium. 745–761.
[49] Mengyu Zhao, Shaowei Cai, and Yuhang Qian. 2024. Distributed SMT Solving Based on Dynamic Variable-Level
Partitioning. In Computer Aided Verification: 36th International Conference, CAV 2024 (Lecture Notes in Computer Science,
Vol. 14681). Springer, 67–89. https://doi.org/10.1007/978-3-031-65627-9_4
, Vol. 1, No. 1, Article . Publication date: August 2018.


---

