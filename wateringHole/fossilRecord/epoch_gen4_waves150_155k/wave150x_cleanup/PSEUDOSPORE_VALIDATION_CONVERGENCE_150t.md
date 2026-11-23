# pseudoSpore Validation Convergence — Wave 150t

**Date**: Jul 21, 2026 | **From**: lithoSpore/pseudoSpore team on ironGate
**To**: All science spring teams (groundSpring, airSpring, healthSpring, neuralSpring, wetSpring, ludoSpring)

---

## Pipeline Status

The pseudoSpore promotion pipeline is **complete and tested**. All tooling is
shipped, integration-tested (end-to-end lifecycle test), and ready for spring
team consumption.

### lithoSpore Dimensional Scorecard

| Metric | Value |
|--------|-------|
| Tests | 242 |
| Clippy warnings | 0 |
| Production unwrap() | 0 |
| Unsafe blocks | 0 |
| Files >800L | 0 |
| TODO/FIXME/HACK | 0 |
| CLI subcommands | 28 |

### Registry Status

| Spore | Spring | Version | Status | Modules |
|-------|--------|---------|--------|---------|
| hotSpring-CompChem-GuideStone | hotSpring | 1.6.1 | **COMPLETE** | 7/8 |
| groundSpring-LTEE-Measurement | groundSpring | 1.0.0 | PENDING | awaiting validation |
| airSpring-Agricultural-Meteorology | airSpring | 1.0.0 | PENDING | awaiting validation |
| healthSpring-Clinical-PKPD | healthSpring | 1.0.0 | PENDING | awaiting validation |
| neuralSpring-ML-Surrogates | neuralSpring | 1.0.0 | PENDING | awaiting validation |
| wetSpring-Life-Science-Analytics | wetSpring | 1.0.0 | PENDING | awaiting validation |
| ludoSpring-Game-Science | ludoSpring | 1.0.0 | PENDING | awaiting validation |

---

## What Spring Teams Need To Do

### Step 1: Verify your scope.toml

Each spring should have a `scope.toml` at its root declaring modules.
These were generated in Wave 150d. Verify the module list matches your
current validation capabilities.

### Step 2: Run your validators

Execute your spring's test suite or validation pipeline. Collect results
into a JSON file matching the validation data stream schema:

```json
[
  {
    "name": "module_name",
    "status": "PASS",
    "checks_total": 10,
    "checks_passed": 10,
    "checks": [
      {
        "name": "check_name",
        "expected": 5.57,
        "observed": 5.52,
        "tolerance": 0.1,
        "unit": "kJ/mol",
        "status": "PASS"
      }
    ]
  }
]
```

The `name` field **must match** the module names declared in your scope.toml.

### Step 3: Populate and promote

```bash
# Generate validation.json skeleton (if not already present)
litho init-validation /path/to/pseudospore

# Populate with your results
litho populate-validation /path/to/pseudospore --results results.json

# Or inline for quick updates
litho populate-validation /path/to/pseudospore --module module_a=PASS --module module_b=PASS

# Verify
litho audit --path /path/to/pseudospore --verbose

# Promote when all modules pass
litho promote-spore /path/to/pseudospore --artifact-root /path/to/lithoSpore

# Check overall status
litho spore-status --artifact-root /path/to/lithoSpore
```

---

## Module Counts Per Spring

| Spring | Modules Declared | Notes |
|--------|-----------------|-------|
| groundSpring | 8 | sensor_noise, observation_gap, error_propagation, inverse_problems, anderson_localization, population_dynamics, calibration_datasets, signal_processing |
| airSpring | 6 | et0_reference, et0_methods, soil_physics, water_balance, atlas_pipeline, full_suite |
| healthSpring | 6 | pbpk_compartments, pd_response, drug_interaction, microbiome_metabolism, population_pk, symbiont_pkpd |
| neuralSpring | 6 | ml_surrogates, scholarly_reproduction, warm_dense_matter, biophysical_ai, reservoir_computing, isomorphic_patterns |
| wetSpring | 7 | metagenomics_16s, variant_calling, analytical_chemistry, mathematical_biology, drug_repurposing, hmm_basecalling, anderson_physics |
| ludoSpring | 6 | hci_motor_laws, goms_modeling, procedural_generation, game_design_frameworks, player_modeling, rpgpt_planes |

---

## Standards Reference

- **Validation Data Stream Standard**: `lithoSpore/specs/VALIDATION_DATA_STREAM.md`
- **pseudoSpore Format**: `lithoSpore/specs/PSEUDOSPORE_STANDARD.md`
- **Scope Contract**: `[[modules]]` entries in scope.toml must match validation.json module names
- **Promotion gate**: All declared modules must have status `PASS` for `promote-spore` to succeed

---

## Timeline

This handoff establishes the convergence contract. Spring teams can begin
producing validation results at their own pace. The pipeline is ready now.

**lithoSpore team action**: None — pipeline complete. Available to assist
spring teams with tooling questions.

**Spring team action**: Run validators, produce results JSON, populate
validation.json, promote when ready.

**Overwatch action**: Track promotion progress via `litho spore-status`.
