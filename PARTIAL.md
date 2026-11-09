# ConceptLab incomplete-context completions

## Scope and prior work

This extension is an original bounded enumerator and witness inspector for established incomplete-context semantics. A missing binary incidence is not silently converted to false. The full binary inspector and canonical-basis implementation remain separate and unchanged except for navigation. This extension computes completed tables, attribute closures, implication and joint-goal truth sets. It does not compute an incomplete-context canonical basis, partial concept lattice, exploration oracle, imputation estimator or fuzzy/graded possibility distribution.

The core completion interpretation is established prior work, not a new algorithm. See the sources below and the complete-context sources in [METHOD.md](METHOD.md). No external implementation, examples or dataset were copied. All retained contexts, schemas, tests, witness views and finite enumeration code are original.

## Input and all completions

Input has exactly `attributes`, `objects`, `goals`. Here `objects` is a **matrix**, unlike the complete-context inspector's attribute-index lists. Each of at most four objects has exactly m entries, with m in 0..4. Each entry is the integer 0 (known absent), integer 1 (known present) or null (unknown). Booleans are rejected. At most six cells may be unknown. At most four goals each contain exactly `premise` and `conclusion`, both arrays of distinct valid attribute indices. Duplicate goals are allowed and keep their positions.

Unknown cells are numbered in row-major order. Completion ID c assigns unknown cell i the value of bit i of c, while preserving every known entry and row identity. With u unknown cells there are exactly 2^u completions, including one completion when u=0. No compatibility constraint between unknown cells is assumed beyond the fixed known entries. The audit enumerates every completion, not a sampled subset.

A completion stores each object's attribute mask and every attribute subset's supporting object IDs and double-derivation closure. Empty support has the full attribute set as its closure. This is the same disclosed degenerate-universe set convention as the complete-context inspector, including zero objects and zero attributes. Duplicate rows remain distinct objects.

## Implication truth sets

For every ordered pair of attribute subsets P,Q, an implication P -> Q is valid in a completed context iff every object possessing P also possesses Q. Every completed table's full counterexample-object list is retained. Supporting and satisfying object lists are reconstructible from the retained completion and are displayed directly by the browser.

- Certain: valid in **every** compatible completion.
- Possible: valid in **at least one** compatible completion.
- Impossible: valid in **no** compatible completion.
- Contingent: possible but not certain.

The exported `status` takes exactly certain, contingent or impossible. A certain implication is also possible. The full valid and invalid completion-ID lists are exported, not just a favorable witness or a count. Completion counts do **not** define a probability distribution. A fraction of validating completions is not a calibrated probability, model confidence or population generalization.

For overlapping P and Q, attributes in Q intersect P follow tautologically. In particular, P -> P is valid in every completion, including a one-unknown-cell table. Directly treating possibly possessed premise attributes and certainly possessed conclusion attributes as independent can lose that tautology. This implementation uses the ordinary implication formula **within each single shared completion**, then quantifies over completions. It does not substitute a cross-extreme extent shortcut for that definition. The overlapping-premise control makes this scope explicit; it is not a claim to reproduce every formula or convention in the papers below.

Checking implication validity in only the all-zero and all-one fill-ins also does not suffice. In a single row `[null,null]`, a0 -> a1 holds in completions 0 (`00`) and 3 (`11`), but fails in completion 1 (`10`). This original control retains every intermediate completion and object witness. The shortcut being contrasted here is **separate implication evaluation in the two endpoints**, not the papers' cross-context extent characterizations.

## Exact support and confidence bounds

The premise support-count minimum and maximum are over all completions. A completed table's conditional row confidence has numerator equal to the number of premise-supporting objects also satisfying Q, and denominator equal to the number supporting P. Zero denominators are undefined, not 100%, even when the implication is vacuously valid.

Confidence extrema are taken only over completions with nonzero premise support. Integer cross-products compare fractions without floating-point rounding. All completion IDs attaining each endpoint are retained. The representative endpoint numerator/denominator comes from the lowest-ID attaining completion and is intentionally not reduced, preserving its observed row counts. Equivalent fractions from other completions can have different raw numerator/denominator pairs; their IDs are still included. If every completion has zero premise support, both endpoints are null. Every zero-support completion is retained separately, even when other completions have defined confidence.

These are descriptive bounds on row ratios within the supplied finite table. No missingness mechanism, prior, likelihood, posterior or predictive interval is specified.

## Joint goals and minimal impossible sets

Goals all refer to **one shared completion**. For every goal subset, the audit intersects the member goals' valid-completion sets. The subset is possible iff this intersection is nonempty, and certain iff it equals the entire completion set. Empty goal subsets are certain. Duplicate goals keep their input positions and do not create different worlds.

Individual possibility need not imply joint possibility. In the row `[null,0]`, the goal empty -> a0 requires completion 1, while a0 -> a1 requires completion 0. Each goal is possible; together they have no compatible completion. This is a quantifier-order distinction, not statistical dependence or a causal effect.

All inclusion-minimal impossible goal subsets are retained. For each one, deleting any member goal leaves a possible subset; every satisfying completion for that deletion is an explicit witness. Since impossibility is monotone under adding goals, testing all one-member deletions is enough for inclusion minimality. Inclusion minimal does not mean globally smallest cardinality. No goal is silently dropped, no maximal consistent subset is selected, and there is no optimization score.

## Interfaces and reproducibility

Run `python -m conceptlab --partial examples/partial.json`, or the installed `conceptlab --partial` console command. The existing UTF-8 byte bound, strict duplicate-key/nonfinite parser and validate-before-atomic-output-replacement apply to both modes. Invalid partial input preserves an existing output path.

The browser uses JSON.parse and a 65,536-character limit. As documented for the base inspector, native 1.0 integer-only schema fields are rejected while browser integral JavaScript numbers are accepted; native duplicate keys are rejected while JSON.parse retains the last. These parser differences are not hidden. Browser edits immediately clear and hide the old audit and disable export. The export is the complete report, independent of selectors, not a selected-query history.

The partial tests add four native core tests and one CLI test without replacing any original tests. Independent complete-matrix truth tables filter compatible worlds for all 107 ternary contexts with both dimensions 0..2; 60 seeded larger contexts add full support, counterexample, Fraction-based endpoint and joint-goal checks. Every completion's attribute closures are also checked against the separate complete-context core. JavaScript compares all full reports for those 107 contexts, another deterministic 60 larger contexts and the 12 retained controls. The two seeded larger sets are not claimed to be identical.

Twelve retained controls cover 86 completions, 438 implication queries, 4,634 query/completion witness rows, 63 goal subsets and seven minimal impossible goal sets. Actual-Chrome tests inspect every retained report, completed matrix, selected closure record, query card, confidence endpoint/tie list, witness row, goal subset, conflict/deletion certificate and export. Every control is layout-checked at 320/390/1280. Counts describe test coverage, not accuracy or performance.

The isolated installed-wheel test retains all 14 original full reports, checks all 12 partial controls, verifies four installed module origins, and runs both console/module interfaces in both modes outside the checkout. CI retains Python 3.10/3.11/3.12/3.13 and original tests, adding partial-control regeneration comparisons. The retained fixture file contains input contexts, not hand-authored expected reports.

## Additional inspected sources

1. Zina Ait-Yakoub, Yassine Djouadi, Didier Dubois and Henri Prade, **From a Possibility Theory View of Formal Concept Analysis to the Possibilistic Handling of Incomplete and Uncertain Contexts**, section 5. Three-valued incidence, preserving known entries, all 2^u completions, lower/upper completions and quantified implication motivation. No disjunctive/graded algorithms, sample family context or paper implementation is reproduced. https://ceur-ws.org/Vol-1703/paper10.pdf
2. Fernando Chacón-Gómez, M. Eugenia Cornejo, Didier Dubois, Jesús Medina and Henri Prade, **Handling incomplete information in formal concept analysis - a possibilistic approach**, published 18 December 2025. Introduction and sections 2-5 as returned by the inspected open page: known-positive/known-negative/unknown distinction, compatible completions, Boolean possibility/necessity and implication characterization. The extension does not implement a graded distribution or claim equivalence with every paper convention; ordinary per-completion implication semantics, including overlap tautologies, are defined above. https://link.springer.com/article/10.1007/s40314-025-03440-3

The Holzer 2004 DOI search result was a lead but its page did not return readable content, so no theorem or implementation detail here relies on that result. The seven directly inspected complete-context sources remain attributed in METHOD.md.
