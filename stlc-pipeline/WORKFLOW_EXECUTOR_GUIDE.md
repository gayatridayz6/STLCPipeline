## Local STLC execution

The Python runner in `stlc-pipeline\workflow\run_stlc.py` makes the stage graph resumable without
requiring a Copilot runtime. It **does not invoke AI agents or simulate test
results**. Author each stage's Markdown with the corresponding Copilot agent (or
another approved runtime), review it, and then hand it to the runner.

Run these commands from the repository root with Python 3:

```powershell
python stlc-pipeline\workflow\run_stlc.py start --ticket EPMCDMETST-66524 --input-file stlc-pipeline\artifacts\inputs\EPMCDMETST-66524.txt
python stlc-pipeline\workflow\run_stlc.py status --ticket EPMCDMETST-66524
```

The input file is an offline copy of requirements, **not a verified Jira read**.
If the configured Jira endpoint is unavailable, do not assert Jira status, links,
or remote execution evidence. `start` runs configuration/artifact/approval hooks
and records the input under `stlc-pipeline\artifacts\runs\<ticket>\requirements.txt`.

After the human explicitly approves the current stage, record their actual name
and the reviewed Markdown:

```powershell
python stlc-pipeline\workflow\run_stlc.py approve --ticket EPMCDMETST-66524 --stage stage-01 --by "Reviewer name"
python stlc-pipeline\workflow\run_stlc.py complete --ticket EPMCDMETST-66524 --stage stage-01 --source stlc-pipeline\artifacts\requirement_analysis.md --route generate-new-tests
```

Do not issue `approve` on a human's behalf without their explicit consent. This
local recorder logs assertions of approval, but does not authenticate approvers.
`status` identifies the next stage. Repeat `approve` and `complete` using reviewed
stage artifacts; for Stage 7 record an explicit human go/no-go before completion.
Stage 1 must specify exactly one route: `generate-new-tests` leads to Stage 2,
while `reuse-existing-tests` skips to Stage 4b and stops after the execution
summary. The normal route runs Stage 4a before 4b.

If prerequisites are missing, record the blocker:

```powershell
python stlc-pipeline\workflow\run_stlc.py block --ticket EPMCDMETST-66524 --reason "Missing actual application URL"
```

Blocking revokes the current stage approval. `unblock --ticket ... --reason
"Actual application URL supplied"` clears the blocker, but requires **new
human approval** before completing that stage.

If a human explicitly waives real-app execution, Stage 4b may instead hand off
as **review-only** (never as a passed application test). While Stage 4b is
blocked, run `python stlc-pipeline\workflow\run_stlc.py waive-execution --ticket
EPMCDMETST-66524 --by "Reviewer name" --reason "No real application target"`.
The waiver is audited, clears the blocker, changes run mode to `review-only`,
and still requires a fresh Stage 4b approval. The Stage 4b artifact must
include `REAL_APP_NOT_EXECUTED` and `review-only`; later stage reports must
preserve the limitation. This does not authorize scans, PRs, Jira writes, or
real-app execution.

Each completion snapshots the evidence and audit trail in
`stlc-pipeline\artifacts\runs\<ticket>\` and updates the configured stage artifact under
`stlc-pipeline\artifacts\`. Live Jira/GitHub reads or mutations, test execution, and security
scanning are **not** performed by this runner; they require separately available
integrations, real evidence, and the appropriate human approval.

Validate the runner and Java workflow definition:

```powershell
python -m unittest discover -s stlc-pipeline\workflow -p "test_*.py"
python .github\hooks\java_validation_guard.py
mvn -f stlc-pipeline\pom.xml test
```

## Book-search UI test package

The two ACs have opt-in Cucumber/Selenium scenarios in
`stlc-pipeline\src\test\resources\features\book_search.feature`. `mvn -f stlc-pipeline\pom.xml test` compiles the
step definitions and runs the settings unit tests, **not** the UI suite.
Provide a real book-store deployment and the following environment variables
before requesting Stage 4b execution approval:

| Variable | Meaning |
| --- | --- |
| `BOOK_STORE_URL` | HTTP(S) URL of the book store homepage |
| `BOOK_STORE_SEARCH_INPUT` | CSS selector for the search input |
| `BOOK_STORE_SEARCH_BUTTON` | CSS selector for the Search button |
| `BOOK_STORE_DETAIL_CONTAINER` | CSS selector for a book detail result |
| `BOOK_STORE_EMPTY_MESSAGE` | CSS selector for the no-results message |
| `BOOK_STORE_EXPECTED_DETAILS` | Known non-title detail text for the "Java Programming" fixture |

The target catalog must contain "Java Programming" and not contain
"Unknown Book XYZ". Chrome and a compatible driver must be available
(Selenium Manager may fetch the driver when network access is permitted).
After a human approves Stage 4b and the target is available:

```powershell
mvn -f stlc-pipeline\pom.xml -Dtest=BookStoreE2ESuite test
```

The UI suite fails if required configuration or actual assertions are missing;
do not report passing search scenarios based on compilation or unit tests.

When no real app exists, `python stlc-pipeline\workflow\book_store_fixture.py` serves a
test-only page on `127.0.0.1:8765`. Its CSS selectors are `#search`, `#submit`,
`.details`, and `.empty`; fixture detail text is `Example Author`. Running
the UI suite against it validates the test wiring only, **not the real
application's acceptance criteria**. Stop the fixture server afterward.