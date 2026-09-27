# Contributing to ContinuityBench

Thank you for your interest in contributing! ContinuityBench is a research benchmark, and we welcome contributions that improve its rigor, coverage, and usability.

## How to Contribute

### New Stressor Sequences

The most valuable contribution is new stressor designs. Each stressor should:

1. **Target a specific drift dimension** (or explicit combination)
2. **Follow the three-phase structure**: Establish → Stress → Probe
3. **Be naturalistic** — the conversation should feel like a real interaction, not a test
4. **Include baseline markers** — what persona, goal, abstraction level, and style should the agent maintain?
5. **Be self-contained** — the stressor should work without external context

Submit stressors as additions to the relevant `.jsonl` file, following the existing format.

### Baseline Results

If you have API access to models we haven't tested, we welcome baseline results:

1. Run `python run_eval.py --model <your-model> --stressors all`
2. Submit the resulting JSON to `baselines/`
3. Include the exact model version, date, and any relevant configuration

### Scoring Improvements

We're interested in alternative scoring methods:
- Embedding-based style distance metrics
- Classifier-based drift detection
- Human annotation studies for judge calibration

### Bug Fixes and Code Quality

Standard open source contribution workflow:
1. Fork the repo
2. Create a feature branch
3. Submit a PR with clear description

## Code of Conduct

Be kind, be rigorous, be helpful. This is a research project — we value intellectual honesty and constructive criticism.
