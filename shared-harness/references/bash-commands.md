# Bash Commands

Default status audit:

```bash
shared-harness
```

Machine-readable status:

```bash
shared-harness --json
```

Sync canonical Codex skill to Claude:

```bash
python3 ~/.codex/skills/shared-harness/scripts/sync_shared_harness.py
```

Validate the bridge:

```bash
python3 ~/.codex/skills/shared-harness/scripts/validate_shared_harness.py
```

Quick Codex skill validation:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/shared-harness
```
