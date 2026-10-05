# Security Compliance Report: EPMCDMETST-66524

Status: DRAFT for human review. Run mode: review-only.
Limitation carried forward from Stage 4b: REAL_APP_NOT_EXECUTED. No real
book-store application was tested, so nothing in this report says anything
about the real application.

## Decision summary

**No security scan was run.** The local runner cannot run scanners, and no
scanner, ruleset or severity threshold has been configured or approved for this
run. `security-scan` requires separate human approval under
`.claude/config/project.json`. Every scan result below is therefore
NOT_EXECUTED, which is different from "no findings".

This report is a manual, read-only inspection of repository files. It is not a
security clearance and must not be read as release or PR approval.

## SAST results

- Status: NOT_EXECUTED. No static analysis tool was run and no tool is configured.
- Scope that would be scanned: `src/test/java/bookstore/` (4 Java files),
  `workflow/*.py`, `.claude/hooks/*.py`.
- Manual observation only (not a substitute for SAST):
  - `BookStoreSettings` accepts only `http` or `https` for `BOOK_STORE_URL`
    and reads its configuration from environment variables.
  - Application configuration is read via `System.getenv`, not hard-coded.
  - No committed value resembling a secret was found in `src`, `workflow`
    or `.claude/config` (a keyword search found only variable names and
    references, listed under Compliance observations).

## SCA results

- Status: NOT_EXECUTED. No dependency or vulnerability scanner was run, so no
  CVE status is asserted for any dependency.
- Declared dependencies in `pom.xml`, all test scope:
  - JUnit Jupiter 5.11.1
  - Cucumber 7.18.1 (`cucumber-java`, `cucumber-junit-platform-engine`)
  - `junit-platform-suite` 1.11.1
  - Selenium Java 4.25.0
  - `maven-surefire-plugin` 3.2.5
- Observations: there are no compile or runtime dependencies. Selenium Manager
  may download a browser driver at run time when network access is permitted,
  which is an unverified supply-chain input.

## Compliance observations (manual, for reviewer attention)

1. **Credential reference mismatch (needs owner confirmation).**
   `.claude/config/mcp/jira_mcp_config.json` defines a `github` server using
   `${GITHUB_PAT}`, while `.claude/config/mcp/github_mcp_config.json` names the
   secret reference `GITHUB_TOKEN`. Two different variable names for the same
   purpose may indicate misconfiguration. Both are references only, with no
   secret values present.
2. **Live integration flags disagree.** `project.json` has
   `liveIntegrationsEnabled: false`, but `github_mcp_config.json` has
   `enabled: true` and targets a specific owner and repo for Stage 6 PR
   creation. Both config files are uncommitted local modifications. Confirm
   the intended state before Stage 6. Nothing was read from or written to
   GitHub or Jira during this stage.
3. **Secret handling.** `project.json` sets `secretHandling: references-only`,
   and the configs follow that. `.gitignore` excludes `.env` and `target/`.
4. **Uncommitted changes not reviewed.** Modified hooks
   (`artifact_contract_guard.py`, `java_validation_guard.py`) and the new
   runner and fixture scripts under `workflow/` were not security-reviewed.
   `book_store_fixture.py` serves a test-only page on `127.0.0.1:8765` and
   should not be exposed beyond localhost.
5. **Offline requirements.** Requirements came from an offline input copy, not
   a verified Jira read.

## Blockers

- B1: Security scan (SAST and SCA) not executed. Needs human approval, a chosen
  tool and a severity threshold.
- B2: Real-application acceptance criteria (AC1, AC2) not validated, since no
  real target exists.

## Approved exceptions

None recorded. No policy exception has been requested or approved.

## Remediation recommendations

- Decide the SAST and SCA tooling and thresholds, then approve the scan or
  explicitly waive it with a recorded reason.
- Unify the GitHub secret reference name (`GITHUB_PAT` vs `GITHUB_TOKEN`).
- Reconcile `enabled: true` in the GitHub config with
  `liveIntegrationsEnabled: false` before any Stage 6 action.
- Review the new scripts under `workflow/` and the modified hooks.

## Human review questions

1. Should a scan be run (and with what tool), or is the scan waived for this
   review-only run?
2. Is `GITHUB_PAT` or `GITHUB_TOKEN` the intended secret reference?
3. Should Stage 6 be limited to a local PR summary until live GitHub access is
   explicitly approved?

## Human review decision

Pending. Not recorded by this draft.
