# Attribute exploration: a table is not an expert

ConceptLab 0.3.0 adds an original bounded implementation of published attribute exploration. It simulates a reliable expert using an explicitly supplied complete formal context. It does not consult a person, a language model or an external knowledge source. All statements about validity refer only to that supplied finite table.

## Request and scope

```json
{"context":{"attributes":3,"objects":[[0,1,2],[0],[1]]},"initial_objects":[0]}
```

`context` is exactly the complete-context schema used by ConceptLab, restricted here to 0..5 attributes and at most eight rows. Each row lists unique integer attribute indices. `initial_objects` lists unique row IDs initially visible to the exploration procedure; its input order does not change execution. The generator records the original request and sorts its working row IDs. Duplicate rows are allowed and retain distinct identities. Background knowledge, exceptions, incomplete counterexamples and online expert interaction are not supported. The complete-context and partial-context inspectors are unchanged apart from navigation links.

## Definitions

For attribute set A and observed object IDs H, `observed_closure(A)` is the intersection of all rows in H containing A. The intersection of no supporting rows is the full attribute universe. `domain_closure(A)` uses the entire supplied expert table instead. An implication A -> B is valid in a table iff every supporting row contains B. This includes unsupported premises: vacuous validity is not empirical or external evidence.

Accepted implications form a definite-Horn theory. Its closure of a seed is obtained by simultaneous forward rounds: test all rule premises against the round's starting set, add the conclusions of every applicable indexed rule, and stop after the first zero-addition round. Display rounds retain firing rule IDs, newly added attributes, and before/after masks. Rule conclusions store only attributes outside their premise.

## Protocol

1. Start at empty premise A, initial observations H, and an empty accepted theory L.
2. Compute C, the closure of A in the observed table.
3. If A=C, record a `closed` event without a question. Otherwise ask A -> C\A. It is the strongest conclusion supported by the currently observed rows for that premise.
4. The simulated expert checks every supplied row. If any row contains A but not C, record **all** such counterexample IDs, choose the lowest ID, reveal that row, and retry the **same** A. A rejection never advances the lectic pivot. Each revealed row respects all previously accepted implications.
5. If no counterexample exists, accept A -> C\A and append it to L. This is a decision about the supplied table only.
6. After a closed or accepted event, try absent attributes i in descending order. Form the truncated seed `(A intersect {0,...,i-1}) union {i}` and close it under L. Accept the first candidate whose coordinates before i equal those of A. Retain every attempted pivot, seed, closure, all earlier-coordinate disagreements and every closure round. If none exists, exploration ends.

Attribute order is the request's index order a0,a1,... . The lectic order compares characteristic vectors from a0 upward, with absent before present. This is not increasing integer-mask order. Adding a counterexample shrinks the observed closure and leaves the premise unchanged. Advancing a pivot strictly increases the premise lectically. Thus there are at most `2^m + number_of_expert_rows` events. No claim of minimum questions or minimum observed rows is made.

For the example, observing only g0 first suggests empty -> {a0,a1,a2}. The full expert supplies g1={a0}; the revised question at the same premise is empty -> {a0}. Then g2={a1} refutes it. A fitted implication is a question, not established domain knowledge.

## Final obligations

For every one of the `2^m` premises, export retains:

- closure under the accepted theory, including derivation rounds;
- closure and support IDs in the complete expert table;
- closure and support IDs in the final observed table;
- all expert-row counterexamples for every attribute outside the domain closure.

All three closures must agree. Consequently the accepted theory captures all implications of the supplied table, not only the questions asked. Some expert rows may remain unseen without any loss of implicational completeness. The final accepted implications are the canonical (Duquenne-Guigues/stem) basis of that finite table under the stated no-background protocol. They are not a minimum-object representation or evidence of external truth.

## Independent verifier

`conceptlab/exploration.py` generates bitset traces. `docs/exploration-engine.js` generates the same report in the browser independently; matching generators alone are not proof.

`conceptlab/exploration_verify.py` shares only strict input validation and does **not** call either generator. It reconstructs expected evidence with Python sets. Theory closure is the intersection of all satisfying attribute-set models containing the seed. It separately reconstructs forward display rounds and requires their result to equal that intersection. Exhaustive lectic sorting of every theory-closed subset independently checks each pivot successor. An inclusion-ordered recursive pseudo-intent definition independently checks the final canonical basis. The checker compares the full typed report: keys, field types, order, counterexample choice, every round and all final obligations. It is bounded exhaustive checking, not a theorem prover or security proof.

The CLI uses strict UTF-8 JSON, rejects duplicate JSON keys/nonfinite constants, keeps modes mutually exclusive, and atomically replaces output only after successful generation/checking. Generator input limit: 65,536 UTF-8 bytes. Verification limit: 4 MiB, to accommodate exported evidence. A custom browser JSON edit invalidates visible results and export until rerun.

## Reproduce

```sh
python -m unittest discover -s tests -v
npm test
sh tools/wheel_smoke.sh
python -m conceptlab --exploration examples/exploration.json -o report.json
python -m conceptlab --verify-exploration report.json
# Installed console entry point works identically:
conceptlab --verify-exploration report.json
# Optional external closure comparison, not a runtime dependency:
uv pip install --target /tmp/conceptlab-reference concepts==0.9.2
PYTHONPATH=.:/tmp/conceptlab-reference python tools/check_exploration_concepts.py
```

Native tests enumerate all 6,654 combinations of expert families on 0..3 attributes and every possible initially observed subfamily. A separate seeded set covers five attributes, duplicate rows and varied initial order. Tests compare the accepted basis against the existing complete-context audit and the separate verifier. Every report scalar outside the request is forged in turn across twelve controls, with key deletion/extra-field attacks and generator-isolation checks. CLI tests preserve existing output after invalid input or forged evidence.

The external `concepts` 0.9.2 check compares the support IDs and domain/final-observed/event-observed closures against that package's extent/intension operations. It **does not** validate question scheduling or canonical-base computation. Empty-axis requests are explicitly counted but excluded from that package comparison because its Context requires nonempty axes; internal exhaustive tests retain them. The reference is optional and adds no project dependency.

Actual Chrome tests cover every event, pivot, display round and final premise across all twelve controls at 1280, 390 and 320 widths; actual exports are downloaded, parsed and independently checked by the Python CLI. Polling is limited to Chrome startup and byte-complete download transport. Semantic evidence assertions are not retried.

## Original controls

The twelve synthetic controls cover empty tables and vocabularies, universal attributes, repeated rejection of one premise, observed/domain disagreement, implication chains, fully observed starts, vacuous premises, duplicate identities, a table containing every subset, a five-attribute expert and sufficient-but-not-exhaustive observations. They are teaching fixtures, not empirical benchmarks or evidence about real domains.

## Inspected foundations and credit

The protocol and canonical-basis theory are prior work. No novelty claim is made for FCA, NextClosure or attribute exploration. Source examples and implementation code were not copied. Original code, finite evidence schema, controls, UI and verification work are provided here.

1. Sebastian Rudolph, **Attribute Exploration**, TU Dresden teaching slides: stem-base algorithm, expert question/refinement loop and preservation lemma. Primary algorithm source. https://iccl.inf.tu-dresden.de/w/images/2/21/05_attribute_exploration.pdf
2. Sebastian Rudolph, **Formal Concept Analysis II: Closure Systems and Implications**, slides based on Gerd Stumme's lecture: lectic order and NextClosure coordinate test. https://iccl.inf.tu-dresden.de/w/images/8/83/FCA2014-03.pdf
3. Gerd Stumme, **Attribute Exploration with Background Implications and Exceptions**: exact expert counterexamples and preservation of earlier accepted knowledge. Its background/exception extensions are excluded. https://kobra.uni-kassel.de/server/api/core/bitstreams/2761a6ef-ed18-4d4d-9d3b-895fa9f50b9e/content
4. Bernhard Ganter and Sergei Obiedkov, **Conceptual Exploration**, Springer, 2016. Publisher metadata/overview inspected, not claimed as a full-book proof review. https://link.springer.com/book/10.1007/978-3-662-49291-8
5. Maximilian Felde and Gerd Stumme, **Attribute Exploration with Multiple Contradicting Partial Experts**, 2022: basic complete expert assumptions and boundaries of richer expert models. Those extensions are excluded here. https://export.arxiv.org/pdf/2205.15714v1.pdf
6. **conexp-clj API**, complete-counterexample handler contract and explicit handler correctness responsibility. Used as a protocol comparison, not a dependency or source-code template. https://github.com/tomhanika/conexp-clj/blob/master/doc/API.md
7. **conexp-clj exploration tutorial**, version 2.7.0: accepted implication/counterexample interaction and canonical-base relation. https://github.com/tomhanika/conexp-clj/blob/v2.7.0/doc/Exploration.org
8. Sebastian Bank, **concepts** 0.9.2 package and API docs: optional external extent/intension reference, not an exploration oracle. https://pypi.org/project/concepts/0.9.2/ and https://concepts.readthedocs.io/en/stable/api.html

Inspected November 9, 2026. The result remains an educational finite simulator: no human expert integration, noisy/partial expert repair, background theory, probability, causal claim, external knowledge acquisition, scalability benchmark or production guarantee.
