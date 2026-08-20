# DAO Governance Case Study — Calibrated Simulation with Real ENS Data

> **Question.** Can an LLM-based governance simulation, calibrated with real
> on-chain participation/concentration metrics, produce testable claims about
> DAO mechanism design — and what happens to those claims under counterfactuals?

**Toolchain.** [OnChainGov](https://github.com/NoahIsArider/OnChainGov) (empirical
metrics) → [MatchaFlow DAO Governance Mode](README.md#dao-governance-mode)
(simulation with Proposer / Governor / Member LLM agents).

---

## 1. TL;DR

- Real ENS DAO data (Snapshot, 90 days): **124 voters, 6 proposals, 392 votes —
  but vp-weighted effective voters ≈ 8.9** (HHI 0.112, Gini 0.897, top-1 address
  controls 28% of voting power). A large DAO is *nominally* participatory and
  *effectively* concentrated.
- Calibrated simulation (baseline): the Governor designs sqrt-weighting +
  a 20% delegation cap in response to the measured concentration; monitored
  concentration stays low and execution quality climbs 85 → 88 → 90; the
  Proposer **accepts in cycle 3**.
- **Counterfactual 1 (low participation):** with a 40-voter / 6.7-votes-per-proposal
  scenario, the same mechanism stack fails — never reaches quorum, Proposer
  **rejects after 3 cycles** and prescribes participation incentives.
  Participation, not mechanism design, is the binding constraint.
- **Counterfactual 2 (no calibration):** without empirical metrics the Governor
  falls back to a generic template (5% cap); the simulation passes, but the
  design has no anchor to the DAO's actual concentration problem.

→ Empirical calibration changes both *what* the agents design and *whether*
the design is accepted. The simulation makes the participation-concentration
trade-off explicit and testable.

## 2. Data

Collected from Snapshot GraphQL (`hub.snapshot.org`) via OnChainGov
(`onchaingov collect snapshot --space ens.eth --since 2026-05-20`), 398 events.

| metric | ENS (baseline) | ENS low-participation (counterfactual) |
|---|---|---|
| proposals (90 d) | 6 | 6 |
| votes | 392 | 40 |
| voters | 124 | 40 |
| avg votes / proposal | 65.3 | 6.7 |
| voting intensity | 3.16 | 1.0 |
| **HHI (vp-weighted)** | **0.112** | **0.156** |
| **Gini (vp-weighted)** | **0.897** | **0.845** |
| top-1 share | 28.3% | 20.3% |
| top-10% share | 83.7% | 73.6% |
| **effective voters (1/HHI)** | **8.9** | **6.4** |

The counterfactual subset keeps the 40 least-active voters and proposals with
≥ 5 votes in that subset — a "demobilized ENS" with the same structure but a
third of the participation.

## 3. Method

Three scenarios, each a full MatchaFlow DAO run (proposal → discussion →
design → execution-monitoring loop → review; max 3 cycles: 2 review-only + 1
acceptance; same proposal topic, same LLM backend `Qwen/Qwen3.8-27B`):

| scenario | calibration | question |
|---|---|---|
| **S1 baseline** | ENS metrics (high participation, medium concentration) | what does a calibrated Governor design? |
| **S2 low-participation CF** | ENS-lowpart metrics (medium participation, medium-high concentration) | does the mechanism survive weak participation? |
| **S3 no-calibration CF** | none (`--no-calibration`, default medium/medium) | what does the uncalibrated Governor design? |

Calibration enters the simulation as a prompt-injected empirical context
(participation/concentration levels + raw numbers); it does not hard-code
mechanisms — agents reason about them.

## 4. Results

### 4.1 Monitoring trajectories (Governor-reported)

| scenario | cycle | participation | concentration | execution quality |
|---|---|---|---|---|
| S1 baseline | 1 | high | low | 85.0 |
| S1 | 2 | high | low | 88.0 |
| S1 | 3 | high | low | **90.0** |
| S2 low-part | 1 | low | high | 82.0 |
| S2 | 2 | low | medium | 85.0 |
| S2 | 3 | low | high | 88.0 |
| S3 no-calib | 1 | medium | medium | 82.0 |
| S3 | 2 | medium | medium | 86.0 |
| S3 | 3 | medium | medium | **88.0** |

### 4.2 Outcome

| scenario | acceptance | cycle | key design choices | Governor's own verdict |
|---|---|---|---|---|
| S1 | ✅ accepted | 3 | sqrt/quadratic weighting, **20% delegation cap**, delegation disclosure, on-chain audit trail | "concentration stays low; quality 85→90; quorum met, top-1 under threshold" |
| S2 | ❌ rejected | 3 (max) | same family + quorum rule (15 independent addresses), top-10% share review, related-address proof | "execution is auditable but never reaches quorum — not a valid decision basis" |
| S3 | ✅ accepted | 3 | **5% delegation cap**, sqrt weighting, disclosure (generic template) | "direction correct; participation sample still small, metrics incomplete" |

## 5. Counterfactual analysis

**C1 — Calibration changes design.** S1 vs S3: with real metrics the Governor
targets the measured concentration problem (20% cap tuned to effective-voter
math); without them it emits a generic 5% cap and medium assumptions. Same
prompt template, different empirical context → different mechanism parameters.

**C2 — Participation is the binding constraint.** S2 holds the mechanism stack
roughly constant and weakens participation by a factor of ~10. Quality still
improves (82 → 88), but the simulation never forms a valid decision basis and
the Proposer rejects — with a concrete prescription: keep anti-concentration
parameters, add targeted participation incentives, and gate expansion on
participation-rate / quorum / vote-count thresholds. The mechanism cannot
manufacture legitimacy; it can only preserve it.

**C3 — Iteration is robust.** Across all scenarios execution quality rises
monotonically (82–90), and rejection feedback triggers concrete parameter
updates — the review-improve loop works even when the outcome is negative.
The failure mode in S2 is *informative*, not broken.

## 6. Limitations

- The simulation is LLM-generated narrative + structured monitoring; metrics are
  agent-reported, not computed from a real execution layer. They should be read
  as *reasoning artifacts*, not measurements.
- Single LLM backend, single proposal topic, 3-cycle horizon. Generalization
  across models / proposals / cycle counts is untested.
- The low-participation counterfactual is a voter-subset of ENS, not a separate
  DAO; it isolates the participation margin but shares ENS's vote distribution.

## 7. Reproduce

```bash
# 1. Collect real data (OnChainGov)
onchaingov collect snapshot --space ens.eth --since 2026-05-20 --out data/raw
onchaingov indicators --data-dir data/raw --out data/indicators
python scripts/prep_ens_calibration.py          # metrics + counterfactual parquet

# 2. Simulate (MatchaFlow)
export LLM_BASE_URL=... LLM_API_KEY=... LLM_MODEL=...
python3 dao/dao_main.py --proposal-idea "..." \
  --calibration-path <ens parquet> --max-cycles 3 --project-code CS_ENS_BASELINE
python3 dao/dao_main.py --proposal-idea "..." \
  --calibration-path <ens lowpart parquet> --max-cycles 3 --project-code CS_ENS_LOWPART
python3 dao/dao_main.py --proposal-idea "..." \
  --no-calibration --max-cycles 3 --project-code CS_NO_CALIB
```

Full deliverables (proposal books, design docs, per-cycle action/monitoring
records, retrospective, acceptance opinions, raw JSON) are under
`dao/simulation/CS_*/deliverables/`.
