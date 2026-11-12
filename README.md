# ConceptLab

Inspect the concepts and implication rules of a small supplied object-attribute
table. ConceptLab retains every closure, lattice operation, pseudo-intent
decision and NextClosure attempt. Separate modes enumerate unknown-cell
completions or reveal counterexamples from a complete simulated expert table.

Python bitsets and browser JavaScript sets compute the reports separately.
No model, API, package runtime dependency or private data.

[Live inspector](https://midya8.github.io/conceptlab/) · [Method, sources and exact conventions](METHOD.md)

## Choose a mode

| Question | Mode |
|---|---|
| Which attribute sets are closed, and which implications hold in this table? | [Complete binary context](https://midya8.github.io/conceptlab/) |
| What can change when explicit unknown cells are filled in? | [Unknown-cell completions](https://midya8.github.io/conceptlab/partial.html) |
| Which observed rules survive counterexamples from a supplied expert table? | [Attribute exploration](https://midya8.github.io/conceptlab/exploration.html) |

The binary mode treats missing incidence as false. The completion mode uses
explicit null cells. Exploration uses a complete simulated expert table; it
does not turn a sample into external domain truth.

## Inspect a complete context

- Every attribute subset's supporting objects, double-derivation closure, support counts and all counterexamples to each missing attribute.
- Every object subset's common attributes and closure, including empty subsets and degenerate contexts.
- All formal concepts, exact cover relations and every pair's meet/join. A join's extent can be larger than the raw union.
- Every pseudo-intent candidate, prior pseudo-intent subset and blocker. Pseudo-intents need not be minimal nonclosed sets.
- The established Duquenne-Guigues canonical basis, a full forward derivation for each attribute subset and a basis-minus-rule countermodel for every rule.
- Ganter's NextClosure closed-intent sequence, every accepted/rejected pivot and the exact earlier-coordinate disagreement.
- Editable implication queries with all supporting, satisfying and counterexample objects. An empty antecedent extent gives classical validity but **null conditional confidence**, not 100% evidence.

## Run

Python 3.10+:

```sh
git clone https://github.com/midya8/conceptlab.git
cd conceptlab
python -m venv .venv
. .venv/bin/activate
python -m pip install .
conceptlab examples/demo.json -o audit.json
python -m conceptlab examples/demo.json
python -m unittest discover -s tests -v
PYTHONPATH=. python tools/build_audits.py
```

The browser runs locally after loading static assets. Serve the directory rather than opening `file://`:

```sh
python -m http.server 8000 --directory docs
```

Node 22+ and a Chrome/Chromium binary run the engine and actual-browser tests.
The separate wheel check also needs `uv`; it builds and installs into a temporary
environment, then runs outside the checkout:

```sh
npm test
# CHROME_BIN=/path/to/chrome npm test
sh tools/wheel_smoke.sh
```

## Input

```json
{"attributes": 3, "objects": [[0, 1], [1], [2], []]}
```

Attribute count is 0..6. There are 0..8 objects, each an array of unique attribute indices. Object identity is its row index, so identical rows remain different objects. Mask bit `i` denotes attribute/object `i`. A missing incidence is false, not unknown. Input labels are deliberately numeric; all examples are original synthetic contexts.

## Controls and verification

The retained binary controls distinguish vacuous validity from supporting evidence, count duplicate rows without inventing concepts, retain contranominal closure systems, and expose strict join/pseudo-intent/derivation failures of simpler assumptions.

Tests compare full independent native/JavaScript reports on all 689 binary contexts with 0..3 attributes and 0..3 objects, plus 100 seeded larger contexts. Separate set references, exhaustive basis-model enumeration, Galois adjunction, closure laws, concept-order meet/join and lectic sorting check the native engine. Actual Chrome tests inspect all retained controls, tables, cards, selectors, full records, export, stale-output clearing and 320/390/1280 containment. These counts describe tested coverage, not a speed benchmark or general-domain validation.

## Bounds and attribution

This implements established formal concept analysis, not a new solver. Exhaustive powersets and pairwise concept operations are intentional at six attributes/eight objects. It is not fuzzy FCA, noisy-rule mining, missing-data inference or a predictive system. The basis theorem concerns minimum **implication count**, not minimum literal count. Rules hold only in the supplied table; adding an object can invalidate them. No causal claim.

The method attributes seven inspected research, teaching and software sources, explains the degenerate-context convention and records the precise original implementation boundary. No external FCA code, datasets, examples, benchmarks or optimized algorithms were copied. No affiliation with Concept Explorer, conexp-clj or fcaR.

## Unknown-cell completions and joint goals

[Live completion inspector](https://midya8.github.io/conceptlab/partial.html) | [Exact semantics, limits and prior sources](PARTIAL.md)

Unknown is not false. Enumerate every bounded binary completion of a 0/1/null context, classify every implication as certain/contingent/impossible, and inspect all completion-indexed object witnesses. Exact integer confidence endpoints retain all ties and separately preserve undefined zero-support completions. Goals share one completion: individually possible goals may be jointly impossible. All inclusion-minimal impossible goal sets retain all one-goal-deletion completion certificates.

```sh
python -m conceptlab --partial examples/partial.json
conceptlab --partial examples/partial.json -o /tmp/completions.json
PYTHONPATH=. python tools/build_partial.py
```

The partial schema allows four attributes, four matrix rows, six unknown cells and four implication goals. Its controls check completion-indexed witnesses, confidence endpoints, zero-support cases and minimal joint-goal conflicts. [PARTIAL.md](PARTIAL.md) retains the individual coverage counts, independent exhaustive references, installed reproduction and parser differences. These are finite knowledge-representation audits, not probabilities, predictions, missing-data estimates or a scalable mining claim.

## Attribute exploration: a table is not an expert

The [exact-expert inspector](https://midya8.github.io/conceptlab/exploration.html) distinguishes implications fitted to observed rows from implications checked against an explicitly supplied complete expert table. Reveal actual counterexamples, retry the same premise, inspect accepted knowledge and every lectic pivot, then audit closure equality for every attribute subset. This is a bounded simulated expert, not human interaction or external domain truth.

Independent Python set/model-intersection verification checks exhaustive lectic successors and the canonical basis through a separate pseudo-intent characterization. Synthetic controls include repeated refutation, vacuity, implication chains, duplicate identities and sufficient-but-not-exhaustive observations. The [protocol, limits, reproduction and prior-work credits](EXPLORATION.md) state exactly what is checked.

```sh
python -m conceptlab --exploration examples/exploration.json -o report.json
python -m conceptlab --verify-exploration report.json
```
