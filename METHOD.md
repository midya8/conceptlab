# ConceptLab: exact method and limits

## What is original

This is an original bounded exhaustive implementation and inspector of established formal concept analysis (FCA). Python uses integer masks; JavaScript uses explicit sets for derivations, pseudo-intents, inference and NextClosure. The synthetic contexts, explanatory search controls, witness schemas, UI and tests are original. No external FCA implementation, dataset, example, benchmark or optimized solver was copied. Existing software already supports FCA and implication-basis inspection. This project makes all small finite decisions visible; it does not claim invention or superior performance.

## Context and derivation

Input has exactly `attributes` and `objects`. Attributes are integers 0..m-1, with m in 0..6. Objects are 0..n-1, n in 0..8. Each object row contains distinct valid attribute indices. Duplicate rows are allowed and remain separate objects. Rows and incidence lists are canonicalized only by sorting attributes within each row; row identity/order remains intact.

Let G be the objects, M the attributes and I their binary incidence. For A subset G, A' consists of the attributes possessed by every object in A. For B subset M, B' consists of all objects possessing every attribute of B. Both empty antecedents use universal quantification: the common attributes of no objects are M, and the objects possessing no required attributes are G.

B'' is the attribute closure; A'' is the object closure. These maps are extensive, monotone and idempotent. The antitone Galois relation is A subset B' iff B subset A'. All attribute and object subsets are retained, not just closed sets. Missing-attribute witnesses list every object in B' lacking that attribute. Thus absence from B'' has an explicit counterexample, even if other attributes follow.

The Belohlavek text's initial definition assumes nonempty object and attribute universes. ConceptLab explicitly extends the same finite set formulas to zero-sized universes. Other inspected context definitions do not impose that restriction. Degenerate examples are an implementation convention stated here, not an empirical result attributed to the nonempty-only definition. With G empty there is exactly one concept (empty extent, full intent); with M empty there is exactly one concept (full extent, empty intent), including both empty simultaneously.

Masks use bit i for element i. A mask is a set encoding, not an integer score. Numeric mask order and lectic order differ.

## Concepts, order and lattice operations

A concept is a pair (A,B) with A'=B and B'=A. Attribute closed sets enumerate all concepts uniquely. IDs are assigned by ascending numeric intent mask, not by generality. Concept (A,B) is below (C,D) when A subset C, equivalently D subset B. Cover relations retain strict comparable pairs with no intermediate concept.

For two concepts:

- Meet has extent A intersect C and intent (B union D)''.
- Join has extent (A union C)'' and intent B intersect D.

Every ordered concept pair's meet and join IDs are exported. The browser exposes their full extent/intent masks and contrasts the join extent with raw extent union. Native independent tests verify greatest-lower/least-upper order conditions, rather than simply recomputing the same formulas.

The UI uses exact concept and cover tables, not a force-directed drawing. It does not claim a spatial embedding, unique diagram or visual cover test.

## Pseudo-intents and canonical basis

A pseudo-intent P is not closed and satisfies Q'' subset P for every pseudo-intent Q strictly contained in P. Candidates are processed by cardinality and then numeric mask, which places every proper subset before its superset. Every decision retains whether the candidate is closed, every earlier pseudo-intent contained in it, and all of those whose closures are not contained in it. Accepted candidates have no blocker.

For each pseudo-intent P, the basis includes P -> P'' minus P. Subtracting P makes the newly concluded attributes explicit and is equivalent to P -> P''. The established Duquenne-Guigues canonical basis is complete, nonredundant and minimum in number of implications for this closure operator. This is an attributed theorem, not a new optimization result. It is not a claim of minimum total premise/conclusion literal count. The implementation does not enumerate every possible equivalent minimum basis.

One inspected paper writes Q'' as a proper subset of P. For the nonclosed candidate P in this definition, allowing Q''=P cannot add a pseudo-intent: any Q'' is closed, so Q''=P would make P closed. The formulations therefore agree here.

Forward derivation starts at a selected set. At each step, the first canonical rule whose premise is present and whose conclusion adds an attribute fires. The full before/after/added masks and rule ID are retained. It terminates at a fixed point. Every initial attribute subset's terminal result must equal its contextual double derivation, and tests independently enumerate all basis models to show the model sets equal exactly the closed sets.

For each basis rule, a second derivation omits that rule and begins at its premise. Its terminal set respects every remaining rule and violates the omitted conclusion. These basis-minus-rule models are explicit nonredundancy certificates. They do not by themselves prove global minimum cardinality; that is the canonical-basis theorem above.

## NextClosure and full candidates

Ganter's established NextClosure is used only to enumerate closed intents, not to generate the canonical basis. The basis here uses exhaustive recursive pseudo-intent decisions. NextClosure starts at closure(empty). For each current intent, pivots i not already present are tested in descending attribute index. The seed keeps current attributes earlier than i and includes i; its closure is accepted only when it agrees with the current set on every earlier coordinate. Every tested seed, closure, disagreement mask and acceptance is retained, including rejected candidates. Stop at the full attribute set.

Attribute 0 is the first lectic coordinate, even though it is bit 0 in the numeric mask. Independent tests sort closed masks by the tuple of bits in attribute order and compare the entire enumeration. There is no claimed NextClosure speed advantage; the small exhaustive reference remains available.

## Implication queries, support and vacuity

The browser accepts an attribute premise and conclusion through mask selectors. An implication B -> C holds in this context exactly when every object supporting B also supports C. The UI lists all premise objects, all satisfying objects and all counterexamples. `valid` is true exactly when the counterexample list is empty.

Support count of a premise is |B'|; the denominator for support proportion is n. Conditional confidence numerator is |(B union C)'|; denominator is |B'|. Numerator and denominator remain visible integers. Decimal ratios are descriptive browser numbers, not extra exact rational fields in the core report. A zero denominator is displayed as null.

An empty extent makes every conclusion classically valid, but does not give 100% conditional confidence. With no objects the support proportion is also null. Zero-support validity is explicitly flagged. These are rules about this complete supplied table, not causal links, generalized population laws or predictions. No unknown/missing incidence state, fuzzy membership, noisy threshold or holdout is modeled.

Queries are interactive derived views of the exported complete context and closure records. The audit export does not promise to preserve the selector's current premise/conclusion, nor a selected query history. Every query can be reconstructed from the context. The full export is the same native/JavaScript audit, independent of current selectors.

## Original controls and what they distinguish

Fourteen synthetic controls include no objects/no attributes/both empty, a shared attribute from the empty premise, duplicate rows, an unsupported conjunctive antecedent, full rows, a contranominal table, directional implications, one additional counterexample object, and the maximum six-attribute/eight-object context.

Three deterministic tiny-context searches retain strict controls:

- `[[1,2],[0],[]]` at four attributes has a pseudo-intent with a proper nonclosed subset. Minimal nonclosed candidates alone miss part of the canonical basis.
- `[[1],[0],[]]` at four attributes has two concepts whose raw extent union is not closed. A concept join requires closure.
- `[[0,1],[],[]]` at four attributes has a subset whose deterministic canonical-basis derivation takes at least two rule applications.

Searches identify transparent counterexamples, not favorable model performance. The generator, not a hand-authored expected-result file, regenerates retained reports. Duplicate-row and added-object controls show that empirical support and logical theory answer different questions.

## Validation and reproducibility

The Python core accepts ordinary dictionaries with exact keys, integer attribute counts and valid lists. Booleans are rejected as integers. The CLI reads UTF-8 JSON, rejects duplicate keys and nonfinite JSON constants, and limits input to 65,536 bytes. It validates and serializes the full result before atomically replacing a requested output path; invalid input preserves an existing output.

Browser JSON uses `JSON.parse`, limits input to 65,536 JavaScript characters, accepts syntactically numeric integral values (for example 1.0), and takes the last duplicate key. Native JSON parsed as a float (such as 1.0) is rejected for integer-only schema fields. Both reject Boolean schema indices. These parser and byte/character differences are explicit, not a cross-parser byte-equivalence claim. Browser input edits immediately hide/clear prior records and disable export until a fresh valid audit.

Run the commands in README. CI uses Python 3.10, 3.11, 3.12, 3.13; Node 22 and actual Chrome; regeneration byte comparisons; and an installed wheel in a temporary environment outside the checkout. Tests inspect all module origins and run both console and module CLIs.

Native set references check closure and pseudo-intents for all 689 binary contexts with both dimensions 0..3 and 100 seeded larger contexts. Tests enumerate every basis model, all object/attribute Galois pairs, closure laws, lectic order and pairwise lattice order. Independent JavaScript compares full report objects, including all traces, against native output for the same exhaustive contexts and another deterministic 100-context larger sequence. The two larger sequences are not claimed to be identical.

Retained corpus: 14 controls, 194 attribute subsets, 390 object subsets, 69 concepts and 30 canonical rules. Browser tests inspect every displayed record, every ordered lattice operation (635), every rule and all 5,762 premise/conclusion query combinations for the retained controls. They also check invalid/stale clearing, JSON export and all controls at 320/390/1280. These are descriptive verification counts, not accuracy, speed or scalability results.

## Inspected sources and existing work

1. **Baris Sertkaya, Some Computational Problems Related to Pseudo-Intents (2009).** Intro and section 2: implication semantics, pseudo-intent recursion and minimum-cardinality basis. Historical complexity/open-problem statements in this paper are not current claims here. https://lat.inf.tu-dresden.de/research/papers/2009/Sert09.pdf
2. **Konstantin Bazhanov and Sergei Obiedkov, Comparing Performance of Algorithms for Generating the Duquenne-Guigues Basis.** Intro and sections 2-3: derivations, implication models, canonical-basis definition and iterative implication closure. The optimized algorithms, experiments, examples and performance comparisons are not used or reproduced. https://ceur-ws.org/Vol-959/paper3.pdf
3. **Sebastian Rudolph, Formal Concept Analysis II: Closure Systems and Implications, TU Dresden (2014), based on Gerd Stumme's lecture.** Closure-system introduction and NextClosure lectic-order theorem/procedure. Titanic is not implemented. https://iccl.inf.tu-dresden.de/w/images/8/83/FCA2014-03.pdf
4. **Sebastian Rudolph, Formal Concept Analysis, Exercise Sheet 7, Winter 2015/16.** Closure-operator definition and NextClosure exercise. No family example copied. https://iccl.inf.tu-dresden.de/w/images/f/fb/IFCA15-Tutorial07.pdf
5. **fcaR, Working with ImplicationSets, CRAN software documentation.** Introduction, canonical-basis extraction and implication display. Evidence of existing functionality, not a source of implementation or sample data. ConceptLab does not implement its fuzzy FCA features. https://cran.r-project.org/web/packages/fcaR/vignettes/implications.html
6. **Concept Explorer, Documentation.** Intro/main interface, context editing, lattice interpretation/subcontexts and Duquenne-Guigues-basis sections. Established functionality is acknowledged; no affiliation or UI/code reuse. https://conexp.sourceforge.net/users/documentation/
7. **Radim Belohlavek, Introduction to Formal Concept Analysis, Olomouc (2008).** Sections 1.1, 2.1-2.3 and 2.6: binary contexts and formal concepts, extent/reverse-intent order, and Main Theorem 2.35's meet/join formulas. Its nonempty-universe convention differs from the explicitly supported degenerate cases above. https://phoenix.inf.upol.cz/esf/ucebni/formal.pdf
