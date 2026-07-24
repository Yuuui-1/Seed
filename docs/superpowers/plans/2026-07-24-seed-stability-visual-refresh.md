# Seed Stability and Visual Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a secure, deterministic logged-in assessment flow and a polished Apple-inspired interface that can be built, tested, pushed, and reviewed as a deployable portfolio project.

**Architecture:** FastAPI owns authentication, assessment ownership, completion state, and idempotent report creation. Vue treats assessment IDs and report IDs as distinct values, protects private routes, and uses a single-flight token refresh path. Shared design tokens and focused view components provide a consistent responsive interface without replacing the existing stack.

**Tech Stack:** FastAPI, SQLAlchemy async, pytest, Vue 3, Pinia, Vue Router, Axios, TypeScript, Vitest, Tailwind CSS, ECharts, Vite PWA.

---

## File Map

- Modify `backend/requirements.txt`: add the runtime dependency required by Pydantic `EmailStr`.
- Modify `backend/app/services/assessment_service.py`: centralize owned-assessment lookup and secure report generation.
- Modify `backend/app/api/v1/endpoints/assessment.py`: require authentication on all private assessment operations.
- Modify `backend/app/api/v1/endpoints/report.py`: return consistent report IDs and map incomplete assessments to 409.
- Modify `backend/tests/test_assessment.py`: cover unauthenticated and cross-user access.
- Modify `backend/tests/test_report.py`: cover incomplete, cross-user, idempotent, and unequal ID behavior.
- Modify `frontend/package.json` and `frontend/package-lock.json`: add the frontend test runner and keep the standard build reproducible.
- Modify `frontend/tsconfig.app.json`: remove the TypeScript 6 build blocker.
- Modify `frontend/src/api/client.ts`: implement non-recursive, single-flight refresh.
- Modify `frontend/src/api/assessment.ts`: align authenticated assessment calls.
- Modify `frontend/src/api/report.ts`: distinguish generation by assessment ID from reading by report ID.
- Modify `frontend/src/stores/auth.ts`: expose reliable session restoration and remove refresh recursion.
- Modify `frontend/src/router/index.ts`: enforce authentication and safe redirect restoration.
- Create `frontend/src/router/guards.ts`: keep guard decisions independently testable.
- Create `frontend/src/api/refresh.ts`: keep refresh coordination independently testable.
- Create `frontend/src/tests/auth-flow.test.ts`: regression tests for guards and refresh behavior.
- Modify `frontend/src/style.css`: define design tokens, base styles, focus states, and motion preferences.
- Modify `frontend/src/App.vue`: provide the global shell and route transitions.
- Modify `frontend/src/views/HomeView.vue`: redesign the landing page and logged-in CTA.
- Modify `frontend/src/views/LoginView.vue`: redesign login and restore target route.
- Modify `frontend/src/views/RegisterView.vue`: redesign registration and restore target route.
- Modify `frontend/src/views/AssessmentView.vue`: simplify the interaction and navigate with returned report ID.
- Modify `frontend/src/views/ReportView.vue`: read report only and show complete loading/error/content states.
- Modify `frontend/src/views/HistoryView.vue`: present report history with clear empty and loading states.
- Modify `frontend/src/views/SharedReportView.vue`: align shared-report visual language.

### Task 1: Restore Reproducible Baselines

- [ ] **Step 1: Add a backend dependency regression check**

Run:

```powershell
.\.venv\Scripts\python.exe -c "from app.schemas.auth import RegisterRequest"
```

Expected before the fix: import fails because `email_validator` is missing.

- [ ] **Step 2: Add the missing declared dependency**

Add this exact line to `backend/requirements.txt`:

```text
email-validator==2.2.0
```

- [ ] **Step 3: Verify the frontend build fails for the known reason**

Run:

```powershell
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Expected before the fix: `TS5101` for deprecated `baseUrl`.

- [ ] **Step 4: Remove obsolete TypeScript configuration**

Remove only `"baseUrl": "."` from `frontend/tsconfig.app.json`; retain the existing `paths` mapping.

- [ ] **Step 5: Install from the declared manifests and verify baselines**

Run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
& 'C:\Program Files\nodejs\npm.cmd' ci
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Expected: schema import succeeds and the complete frontend build exits 0.

- [ ] **Step 6: Commit**

```powershell
git add backend/requirements.txt frontend/tsconfig.app.json
git commit -m "fix: restore reproducible project builds"
```

### Task 2: Enforce Assessment Ownership

- [ ] **Step 1: Write failing backend tests**

Add tests equivalent to:

```python
@pytest.mark.asyncio
async def test_assessment_routes_require_auth(client):
    start = await client.post("/api/v1/assessment/start")
    answer = await client.post(
        "/api/v1/assessment/1/answer",
        json={"question_id": load_questions()[0]["id"], "answer_value": 3},
    )
    progress = await client.get("/api/v1/assessment/1/progress")
    assert start.status_code == 401
    assert answer.status_code == 401
    assert progress.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_assessment(client):
    owner = await _register(client, "owner@test.com")
    stranger = await _register(client, "stranger@test.com")
    assessment_id = await _start_assessment(client, owner)
    headers = {"Authorization": f"Bearer {stranger}"}
    assert (await client.get(
        f"/api/v1/assessment/{assessment_id}/progress", headers=headers
    )).status_code == 404
    assert (await client.post(
        f"/api/v1/assessment/{assessment_id}/answer",
        headers=headers,
        json={"question_id": load_questions()[0]["id"], "answer_value": 3},
    )).status_code == 404
```

- [ ] **Step 2: Run the focused tests and observe the security failure**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_assessment.py -v
```

Expected: new tests fail because routes permit anonymous or cross-user access.

- [ ] **Step 3: Implement owned lookup**

Add a service function with this contract:

```python
async def get_owned_assessment(
    db: AsyncSession, assessment_id: int, user_id: int
) -> Assessment | None:
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()
```

Pass `user_id` into answer and progress flows. Require `Depends(require_auth)` in the three assessment routes and return the same 404 for missing and foreign records.

- [ ] **Step 4: Run focused and full backend tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_assessment.py -v
.\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: ownership regressions and the existing suite pass.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/services/assessment_service.py backend/app/api/v1/endpoints/assessment.py backend/tests/test_assessment.py
git commit -m "fix: enforce assessment ownership"
```

### Task 3: Make Report Creation Secure and ID-Safe

- [ ] **Step 1: Write failing report regressions**

Add tests equivalent to:

```python
@pytest.mark.asyncio
async def test_cannot_generate_report_for_incomplete_assessment(client):
    token = await _register(client, "incomplete@test.com")
    assessment_id = await _start_assessment(client, token)
    response = await client.post(
        f"/api/v1/reports/generate/{assessment_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_report_generation_is_owned_and_idempotent(client):
    owner = await _register(client, "report-owner@test.com")
    stranger = await _register(client, "report-stranger@test.com")
    assessment_id = await _complete_assessment(client, owner)
    foreign = await client.post(
        f"/api/v1/reports/generate/{assessment_id}",
        headers={"Authorization": f"Bearer {stranger}"},
    )
    assert foreign.status_code == 404
    first = await client.post(
        f"/api/v1/reports/generate/{assessment_id}",
        headers={"Authorization": f"Bearer {owner}"},
    )
    second = await client.post(
        f"/api/v1/reports/generate/{assessment_id}",
        headers={"Authorization": f"Bearer {owner}"},
    )
    assert first.json()["data"]["id"] == second.json()["data"]["id"]
```

Create an extra assessment before report creation, then assert `GET /reports/{report_id}` works while `report_id != assessment_id`.

- [ ] **Step 2: Verify the new tests fail**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_report.py -v
```

Expected: incomplete or foreign report generation succeeds incorrectly, or the ID mismatch assertion fails.

- [ ] **Step 3: Implement the secure report contract**

Make `finalize_report`:

```python
assessment = await get_owned_assessment(db, assessment_id, user_id)
if assessment is None:
    raise AssessmentNotFoundError
if assessment.status != "completed":
    raise AssessmentNotCompletedError
existing = await db.execute(
    select(Report).where(
        Report.assessment_id == assessment_id,
        Report.user_id == user_id,
    )
)
```

Map the two domain errors to 404 and 409 in the endpoint. Keep report detail and sharing keyed strictly by `report_id`.

- [ ] **Step 4: Verify focused and full backend tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_report.py -v
.\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: all tests pass and ID values are no longer assumed equal.

- [ ] **Step 5: Commit**

```powershell
git add backend/app/services/assessment_service.py backend/app/api/v1/endpoints/report.py backend/tests/test_report.py
git commit -m "fix: secure report generation and identifiers"
```

### Task 4: Fix Frontend Authentication and Report Navigation

- [ ] **Step 1: Add the frontend test harness**

Add scripts and development dependencies:

```json
{
  "scripts": {
    "test": "vitest run"
  },
  "devDependencies": {
    "@vue/test-utils": "^2.4.6",
    "jsdom": "^26.1.0",
    "vitest": "^3.2.4"
  }
}
```

- [ ] **Step 2: Write failing guard and refresh tests**

Test these public contracts:

```typescript
it('redirects a guest to login with the original path', () => {
  expect(resolveAuthNavigation(false, '/report/42')).toEqual({
    name: 'login',
    query: { redirect: '/report/42' },
  })
})

it('shares one refresh request across concurrent 401 responses', async () => {
  const refresh = vi.fn().mockResolvedValue('new-token')
  const coordinator = createRefreshCoordinator(refresh)
  await Promise.all([coordinator.refresh(), coordinator.refresh()])
  expect(refresh).toHaveBeenCalledTimes(1)
})

it('does not retry the refresh endpoint after refresh failure', async () => {
  const refresh = vi.fn().mockRejectedValue(new Error('expired'))
  const coordinator = createRefreshCoordinator(refresh)
  await expect(coordinator.refresh()).rejects.toThrow('expired')
  expect(refresh).toHaveBeenCalledTimes(1)
})
```

- [ ] **Step 3: Run tests and observe failure**

Run:

```powershell
& 'C:\Program Files\nodejs\npm.cmd' test
```

Expected: imports fail because guard and refresh helpers do not exist.

- [ ] **Step 4: Implement guard and refresh helpers**

Implement:

```typescript
export function resolveAuthNavigation(authenticated: boolean, fullPath: string) {
  return authenticated
    ? true
    : { name: 'login', query: { redirect: fullPath } }
}
```

Implement a coordinator that caches one in-flight Promise and clears it in `finally`. Use a bare Axios instance for `/auth/refresh`, retry the original request once, and never intercept the refresh request.

- [ ] **Step 5: Separate report route semantics**

Change the completion path to:

```typescript
const generated = await generateReport(assessmentId.value)
router.push(`/report/${generated.data.id}`)
```

Make `ReportView` call only:

```typescript
const response = await getReport(Number(route.params.id))
report.value = response.data
```

Remove the anonymous preview/register branch and unused bind API from the active flow.

- [ ] **Step 6: Verify tests and build**

Run:

```powershell
& 'C:\Program Files\nodejs\npm.cmd' test
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Expected: Vitest and the standard build pass.

- [ ] **Step 7: Commit**

```powershell
git add frontend/package.json frontend/package-lock.json frontend/src/api frontend/src/stores/auth.ts frontend/src/router frontend/src/views/AssessmentView.vue frontend/src/views/ReportView.vue frontend/src/tests
git commit -m "fix: stabilize authenticated report flow"
```

### Task 5: Apply the Apple-Inspired Visual System

- [ ] **Step 1: Record the visual acceptance checklist**

Before production edits, verify the current pages against:

```text
- 375px and 1440px widths
- visible keyboard focus
- 44px minimum primary controls
- loading, empty, error, and success states
- no content overflow
- reduced-motion support
```

Expected: current interface lacks a unified system and several explicit states.

- [ ] **Step 2: Implement global tokens**

Define CSS custom properties:

```css
:root {
  --seed-canvas: #f5f3ed;
  --seed-surface: rgba(255, 255, 255, 0.86);
  --seed-ink: #17211b;
  --seed-muted: #6f786f;
  --seed-green: #2f6f4e;
  --seed-green-soft: #dfece4;
  --seed-gold: #b48a4a;
  --seed-border: rgba(23, 33, 27, 0.09);
  --seed-shadow: 0 24px 70px rgba(31, 45, 36, 0.10);
}
```

Add focus-visible and reduced-motion rules. Keep contrast ratios suitable for body text.

- [ ] **Step 3: Redesign authentication and home**

Use one primary CTA, concise copy, generous spacing, a restrained botanical Seed mark, and shared form primitives. Preserve all existing actions and validation.

- [ ] **Step 4: Redesign assessment**

Keep one active question visually dominant, show progress and question count, disable answers during submission, and provide explicit network errors with retry. Do not restore anonymous preview behavior.

- [ ] **Step 5: Redesign report and history**

Report sections must include summary, radar chart, six dimension cards, career suggestions, share action, and repeat-assessment CTA. History cards use report ID for navigation and expose date plus top dimensions.

- [ ] **Step 6: Align the shared report**

Apply the same tokens and report hierarchy while keeping shared access public and excluding private actions.

- [ ] **Step 7: Run automated validation**

Run:

```powershell
& 'C:\Program Files\nodejs\npm.cmd' test
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Expected: all frontend tests pass and production assets build.

- [ ] **Step 8: Commit**

```powershell
git add frontend/src/App.vue frontend/src/style.css frontend/src/views
git commit -m "feat: polish the Seed assessment experience"
```

### Task 6: End-to-End Verification and Publication

- [ ] **Step 1: Run complete backend verification**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Expected: zero failures and zero collection errors.

- [ ] **Step 2: Run complete frontend verification**

```powershell
& 'C:\Program Files\nodejs\npm.cmd' test
& 'C:\Program Files\nodejs\npm.cmd' run build
```

Expected: zero test failures and build exit code 0.

- [ ] **Step 3: Inspect final scope**

```powershell
git status --short --branch
git diff --check origin/main...HEAD
git diff --stat origin/main...HEAD
```

Expected: only design, plan, backend security/build, frontend flow/tests, and visual files are present.

- [ ] **Step 4: Request code review**

Review `origin/main...HEAD` for correctness, security, accessibility, and scope. Fix all critical and important findings, then rerun Steps 1–3.

- [ ] **Step 5: Push**

```powershell
git push -u origin agent/stabilize-and-polish-seed
```

- [ ] **Step 6: Open a draft pull request**

Target `Yuuui-1/Seed:main`. The PR body must describe root causes, security impact, visual changes, migrations/dependency changes, and exact verification results.
