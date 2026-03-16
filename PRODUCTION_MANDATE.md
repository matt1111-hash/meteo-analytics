# Production Mandate

## Status

This document is a root-level execution mandate for every agent working anywhere under `/home/tibor/PythonProjects`.

Effective immediately, the required target state for every repository is not “mostly working”, “acceptable”, or “good enough”. The only acceptable target is production-ready, reviewable, repeatable, and fully validated delivery.

There is no medium-quality outcome. There is no partial definition of done. There is no “we will clean it up later”.

## Non-Negotiable Goal For Tomorrow

Every actively maintained repository under `/home/tibor/PythonProjects` must be brought to a state where all of the following are true:

- local repository is clean
- remote branch state is clean and pushable
- no hidden worktree debris remains
- test suite is green
- linting is green
- type checking is green where configured
- quality gate is green
- CI/CD is green
- E2E coverage exists where the project type requires it
- production build or runtime startup is validated
- architecture checks are either green or explicitly configured to the real project structure
- no fake green status caused by broken venv activation, missing node modules, missing runtime dependencies, or skipped tools
- where the app is launched from the Linux desktop, the desktop launcher path is real, current, and validated end-to-end

If any one of these is false, the repository is not production-ready.

## What Is Forbidden

The following are forbidden across all repositories:

- weakening tests to get green
- deleting failing tests without an explicit human decision
- changing protected config only to silence gates
- accepting false green output from broken tool detection
- leaving dirty git state and calling the work complete
- shipping with known type errors, lint debt, or collection-time test failures
- shipping with broken local setup while claiming CI will handle it
- shipping with missing frontend dependencies or missing Python runtime packages
- leaving desktop launchers pointing at stale paths, removed entrypoints, or ad-hoc shell one-liners that are not validated
- ignoring file-size, complexity, architecture, or security gates because they are inconvenient
- hiding unfinished work in comments, TODOs, placeholders, or undocumented follow-up promises

## Required End State Per Repository

A repository may be called complete only when all applicable checks below are satisfied.

### Git Integrity

- `git status` is clean
- no unintended untracked files remain
- no broken generated artifacts remain in repo root or project root
- branch state is reviewable and safe to push
- remote can be updated without carrying accidental local garbage

### Python Repositories

- virtual environment is valid and points to the actual active environment
- `venv/bin/activate` or `.venv/bin/activate` does not point at a non-existent path
- runtime dependencies are installed
- dev dependencies are installed
- `pytest` passes
- `ruff check` passes
- `ruff format --check` passes
- `mypy` passes where the repo expects mypy
- `./quality_gate.sh` passes locally
- `./quality_gate.sh --ci` passes where supported
- coverage meets repository threshold
- architecture checks are real, not template-only, when the repository claims Clean Architecture enforcement
- file-size and complexity gates pass without exemptions introduced just to hide problems

### Frontend Repositories

- `node_modules` exists and is valid for the current lockfile
- lint passes
- typecheck passes
- test suite passes
- production build passes
- repo-owned desktop launcher script exists where the app is launched from the desktop
- repo-owned `.desktop` file exists or the Desktop entry points to the repo-owned launcher
- desktop launcher validates dependencies and starts from the repository root
- desktop launcher startup path is validated against the real production preview/build flow
- frontend quality gate passes where present
- E2E tests exist and pass for user-critical flows where the project is user-facing
- bundle warnings are either resolved or formally documented as accepted risk by a human

### API And Full-Stack Repositories

- backend tests pass
- frontend tests pass
- API startup path is validated
- authentication, authorization, and rate limiting are covered where applicable
- E2E tests cover the core user journey end-to-end
- CI pipeline exercises the real critical path, not a reduced substitute

### Desktop-Launched Applications

- the repository owns the launcher logic; launcher behavior must not live only in an unversioned Desktop file
- desktop `.desktop` entries must call a stable script or command owned by the repository
- launcher scripts must set the correct working directory before starting the app
- launcher scripts must fail loudly on missing venv, missing node modules, missing build artifacts, or missing entrypoints
- launcher scripts should support a lightweight validation mode such as `--check` where practical
- repository README must document the desktop launch command when desktop launch is part of the supported workflow

## CI/CD Requirement

For every repository that matters, CI/CD is not optional.

Minimum required CI/CD standard:

- install dependencies in a clean environment
- run lint
- run type checks where configured
- run tests
- enforce coverage threshold
- run build for buildable apps
- fail on architecture or security gates where those are part of the repository contract

If CI/CD is absent, broken, stale, or not representative of the real local workflow, that repository is not production-ready.

## E2E Requirement

E2E tests are mandatory for projects where user flows matter.

Examples:

- frontend applications with user interaction
- API + UI systems with critical workflows
- CLI tools with critical end-to-end scenarios
- data pipelines where integration flow matters more than isolated unit behavior

E2E tests must validate the real happy path and at least the most important failure path. A repository without E2E coverage for critical behavior is not considered complete unless a human explicitly waives that requirement.

## Agent Execution Standard

Every agent working under `/home/tibor/PythonProjects` must operate under the following standard:

1. Start with truth, not optimism.
   Read the repo state first. Verify the actual toolchain, the actual venv, the actual node modules, the actual tests, and the actual gates.

2. Do not trust green output until you prove it is real.
   If a gate says tools are missing, determine whether the tools are actually missing or the environment activation is broken.

3. Fix root causes, not symptoms.
   Broken PATH activation, template import-linter configs, missing runtime packages, oversized files, invalid CI wiring, and absent E2E coverage are root-cause-level issues.

4. Treat “dirty but probably fine” as failure.
   Dirty worktree, broken local setup, and missing dependency installation are production blockers unless intentionally documented and resolved.

5. Do not stop at unit tests.
   Validate the full path required by the repo type: build, startup, CLI, API, frontend, integration, and E2E where applicable.

6. Do not declare success early.
   The repository is done only when the repository contract is green, not when one command happens to pass.

7. Treat desktop launchers as part of production.
   If a user launches the app from `Asztal` or `Desktop`, that path is part of the supported runtime contract and must be verified.

## Required Reporting Standard

When reviewing or fixing a repository, agents must report using concrete facts:

- exact command run
- exact result
- whether the result is trustworthy or a false positive/false negative
- exact blocking files when relevant
- whether the worktree is clean or dirty
- whether the remote is safe to update
- whether CI/CD and E2E exist and are passing
- whether desktop launcher files exist, what they execute, and whether that chain was validated

Do not use vague statements like “looks fine”, “mostly ready”, or “probably okay”.

## Repository Completion Checklist

Before calling any repository production-ready, all items below must be true:

- repository worktree clean
- repository branch reviewable
- remote state safe to push
- runtime dependencies installed
- dev dependencies installed
- all required gates green
- tests green
- build green if applicable
- CI green
- E2E green where required
- desktop launcher green where desktop launch is part of the real workflow
- no known critical or medium findings left undocumented
- no false green status due to broken environment setup

## Escalation Rule

If a repository cannot meet this standard in one pass, the agent must not lower the bar. The agent must document the exact blockers and continue with the next highest-leverage remediation path.

The correct reaction to failure is escalation of rigor, not reduction of standards.

## Final Principle

Every repository under `/home/tibor/PythonProjects` is expected to converge to the same standard:

- clean codebase
- clean git state
- clean remote state
- real validation
- real CI/CD
- real E2E where needed
- no excuses

Production-ready means defensible under scrutiny.
If it cannot survive scrutiny, it is not ready.
