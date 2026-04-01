# VERIFICATION_RECORD — S1: Repo Scaffold & Compose Skeleton

| Field | Value |
|---|---|
| Session | S1 — Repo Scaffold & Compose Skeleton |
| Date | 2026-03-31 |
| Engineer | Y Vaishali Rao |

> This record is completed during the session — not after. Predictions are written before tests are run. CD Challenge output is pasted verbatim. Nothing is backdated.

---

## Task 1.1 — Directory Layout

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 1.1 TC-1 | All directories exist | find lists every directory with no missing entries | PASS |
| 1.1 TC-2 | All placeholder files exist | find lists every .py, .sql, .yml, .md, .txt, .html file | PASS |
| 1.1 TC-3 | No extra files created | find output matches spec list exactly — no __pycache__, .DS_Store | PASS |

**Predictions** (fill in before running):

- 1.1 TC-1: find will list all 7 directories — expect no missing entries
- 1.1 TC-2: all 12 placeholder files present from the spec
- 1.1 TC-3: no extra files — Claude Code was given a strict list

**Verification command:**
```
find customer-risk-api -type f | sort
```

**CD Challenge Output:**
```
customer-risk-api/.env.example
customer-risk-api/README.md
customer-risk-api/api/Dockerfile
customer-risk-api/api/app/__init__.py
customer-risk-api/api/app/auth.py
customer-risk-api/api/app/db.py
customer-risk-api/api/app/main.py
customer-risk-api/api/app/routers/__init__.py
customer-risk-api/api/app/routers/customers.py
customer-risk-api/api/app/static/index.html
customer-risk-api/api/requirements.txt
customer-risk-api/db/migrations/001_schema.sql
customer-risk-api/db/seed/seed.sql
customer-risk-api/docker-compose.yml
customer-risk-api/tests/conftest.py
customer-risk-api/tests/test_auth.py
customer-risk-api/tests/test_customers.py
customer-risk-api/tests/test_errors.py
customer-risk-api/tests/test_seed.py
customer-risk-api/tests/test_ui.py
```

**Code Review:** All files are empty placeholders as required. No application logic present. Directory structure matches spec exactly.

---

## Task 1.2 — .env.example and README

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 1.2 TC-1 | All 6 env vars in .env.example | grep -c '=' .env.example returns 6 | PASS |
| 1.2 TC-2 | No secret values in .env.example | POSTGRES_PASSWORD and API_KEY lines have empty values after = | PASS |
| 1.2 TC-3 | README contains quickstart command | grep 'docker compose up' README.md returns a match | PASS |
| 1.2 TC-4 | README mentions training demo | grep -i 'training demo' README.md returns a match | PASS |

**Predictions** (fill in before running):

- 1.2 TC-1: exactly 6 — the 6 vars from the architecture doc
- 1.2 TC-2: both secret lines will have empty values, just the = sign
- 1.2 TC-3: quickstart section will include docker compose up
- 1.2 TC-4: README will mention training demo in the description paragraph

**Verification command:**
```
grep -c '=' customer-risk-api/.env.example
grep 'API_KEY' customer-risk-api/.env.example
grep 'docker compose up' customer-risk-api/README.md
```

**CD Challenge Output:**
```
6
API_KEY=                    # any non-empty string; used in X-API-Key header
docker compose up
```

**Code Review:** .env.example has correct comments on each line. POSTGRES_HOST comment notes it must match the Compose service name. README curl example includes the X-API-Key header. Training demo notice is in the first paragraph.

---

## Task 1.3 — docker-compose.yml

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 1.3 TC-1 | Compose config is valid | docker compose config exits 0 | PASS |
| 1.3 TC-2 | postgres port not exposed to host | no '5432:5432' under postgres ports | PASS |
| 1.3 TC-3 | fastapi-app port 8000 exposed | contains '8000:8000' or published: 8000 | PASS |
| 1.3 TC-4 | depends_on condition is service_healthy | contains service_healthy under fastapi-app | PASS |
| 1.3 TC-5 | postgres healthcheck uses pg_isready | contains pg_isready | PASS |

**Predictions** (fill in before running):

- 1.3 TC-1: config will be valid — straightforward two-service file
- 1.3 TC-2: postgres has no ports: block at all
- 1.3 TC-3: fastapi-app ports block will show 8000:8000
- 1.3 TC-4: depends_on will use condition: service_healthy
- 1.3 TC-5: healthcheck test will call pg_isready with -U and -d flags

**Verification command:**
```
cd customer-risk-api && docker compose config
docker compose config | grep -A5 'depends_on'
docker compose config | grep 'pg_isready'
```


**Code Review:** postgres has no ports block — confirmed not exposed to host. depends_on uses service_healthy. No restart policy present (deviation from 1.4 was caught and removed — see SESSION_LOG deviations).

---

## Task 1.4 — Dockerfile and requirements.txt

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 1.4 TC-1 | Container builds without error | docker compose up --build exits 0 | PASS |
| 1.4 TC-2 | App responds on port 8000 | curl http://localhost:8000/ returns {"status":"ok"} | PASS |
| 1.4 TC-3 | docs_url is disabled | curl http://localhost:8000/docs returns 404 | PASS |
| 1.4 TC-4 | openapi.json is disabled | curl http://localhost:8000/openapi.json returns 404 | PASS |
| 1.4 TC-5 | Postgres container is healthy | docker compose ps shows postgres as healthy | PASS |

**Predictions** (fill in before running):

- 1.4 TC-1: build will succeed — slim image, small requirements list, no compile steps
- 1.4 TC-2: placeholder route returns {"status":"ok"}
- 1.4 TC-3: 404 — docs_url=None is set on the FastAPI constructor
- 1.4 TC-4: 404 — openapi_url=None is set on the FastAPI constructor
- 1.4 TC-5: postgres healthcheck passes within 15s — pg_isready returns 0

**Verification command:**
```
cd customer-risk-api && docker compose up --build -d
sleep 15
curl -s http://localhost:8000/
curl -o /dev/null -w '%{http_code}' http://localhost:8000/docs
docker compose ps
```

**CD Challenge Output:**
```
[+] Building 18.3s (10/10) FINISHED
[+] Running 2/2
 ✔ Container customer-risk-api-postgres-1     Healthy
 ✔ Container customer-risk-api-fastapi-app-1  Started

{"status":"ok"}
404

NAME                                  IMAGE         STATUS
customer-risk-api-fastapi-app-1       ...           running
customer-risk-api-postgres-1          postgres:15   running (healthy)
```

**Code Review:** requirements.txt pins all four packages to exact versions as specified. Dockerfile copies requirements first (layer caching), then app/. CMD uses uvicorn with --host 0.0.0.0. docs_url, redoc_url, and openapi_url all set to None on FastAPI constructor.

---

## Test Cases Added During Session

| Case | Scenario | Expected Outcome | Reason for Addition |
|---|---|---|---|
| — | — | — | — |

---

## Scope Decisions

S1 has no invariant-touching tasks. No test coverage for INV-01 through INV-11 is expected at this stage — all invariant verification is scoped to S2 onwards per the execution plan.

---

## Verification Verdict

- [x] All test cases have a Result entry
- [x] All CD Challenge outputs are pasted verbatim
- [x] All deviations are recorded in SESSION_LOG.md
- [x] No invariant was violated — or if violated, recorded and escalated

**Status:** Complete

**Engineer sign-off:**  Y Vaishali Rao — 2026-03-31

# VERIFICATION_RECORD — S2: Database Layer
**Customer Risk API · Training Demo System**

| Field | Value |
|---|---|
| Session | S2 — Database Layer |
| Date |2026-03-31 |
| Engineer | Y Vaishali Rao|

> This record is completed during the session — not after. Predictions are written before tests are run. CD Challenge output is pasted verbatim. Nothing is backdated.

---

## Task 2.1 — Schema Migration SQL

> **INVARIANT TOUCH: INV-01, INV-03**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 2.1 TC-1 | Schema creates without error | psql exits 0 on first run | PASS |
| 2.1 TC-2 | Schema is idempotent | psql exits 0 on second run with no errors | PASS|
| 2.1 TC-3 | Table exists with correct columns | \d risk_profiles shows customer_id, risk_tier, risk_factors, created_at |PASS |
| 2.1 TC-4 | risk_tier column is ENUM not VARCHAR | \d risk_profiles shows type risk_tier_enum for risk_tier column |PASS |
| 2.1 TC-5 | No triggers on table | SELECT count(*) FROM pg_trigger WHERE tgrelid = 'risk_profiles'::regclass returns 0 |PASS |



**Verification command:**
```
cd customer-risk-api
docker compose exec -T postgres psql -U riskapi -d riskdb \
  -f /dev/stdin < db/migrations/001_schema.sql
docker compose exec -T postgres psql -U riskapi -d riskdb \
  -f /dev/stdin < db/migrations/001_schema.sql
docker compose exec postgres psql -U riskapi -d riskdb \
  -c "SELECT count(*) FROM pg_trigger WHERE tgrelid = 'risk_profiles'::regclass;"
```


**Code Review:**

> Check: no triggers attached to risk_profiles.
> Check: TEXT[] not JSONB (order preservation).
> Check: IF NOT EXISTS on both CREATE statements.

---

## Task 2.2 — Seed Script

> **INVARIANT TOUCH: INV-01, INV-11**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 2.2 TC-1 | First run inserts 9 rows | SELECT COUNT(*) returns 9 after first run |PASS |
| 2.2 TC-2 | Second run does not change row count | SELECT COUNT(*) still returns 9 after second run |PASS |
| 2.2 TC-3 | DEMO-007 is HIGH tier | SELECT risk_tier FROM risk_profiles WHERE customer_id='DEMO-007' returns HIGH |PASS |
| 2.2 TC-4 | DEMO-001 has 3 factors in correct order | SELECT risk_factors FROM risk_profiles WHERE customer_id='DEMO-001' returns the exact array specified | PASS|
| 2.2 TC-5 | No DEMO-010 or other records exist | SELECT COUNT(*) FROM risk_profiles returns exactly 9 |PASS |



**Verification command:**
```
cd customer-risk-api
docker compose exec -T postgres psql -U riskapi -d riskdb \
  -f /dev/stdin < db/seed/seed.sql
docker compose exec -T postgres psql -U riskapi -d riskdb \
  -f /dev/stdin < db/seed/seed.sql
docker compose exec postgres psql -U riskapi -d riskdb \
  -c "SELECT COUNT(*) FROM risk_profiles;"
docker compose exec postgres psql -U riskapi -d riskdb \
  -c "SELECT risk_tier FROM risk_profiles WHERE customer_id='DEMO-007';"
```


**Code Review:**

> Check: ON CONFLICT (customer_id) DO NOTHING on every INSERT.
> Check: exactly 9 rows after two runs.
> Check: factor arrays match the spec order exactly — no sorting.

---

## Task 2.3 — psycopg2 Connection Pool Module

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 2.3 TC-1 | Pool initialises without error | python import exits 0 | PASS|
| 2.3 TC-2 | get_conn returns a live connection | SELECT 1 returns (1,) |PASS |
| 2.3 TC-3 | release_conn returns conn to pool | get_conn called 5 times then release_conn x5 then get_conn again succeeds | PASS|
| 2.3 TC-4 | Credentials not logged | docker compose logs fastapi-app contains no POSTGRES_PASSWORD value | PASS|



**Verification command:**
```
docker compose exec fastapi-app python -c \
  "from app.db import get_conn, release_conn; c=get_conn(); \
   cur=c.cursor(); cur.execute('SELECT 1'); \
   print(cur.fetchone()); release_conn(c)"
```



**Code Review:**

> Check: module-level pool initialised at import time, not per-request.
> Check: get_conn() does not catch exceptions — lets them propagate.
> Check: no ORM abstraction — bare psycopg2 only.
> Check: credentials sourced from os.environ, not hardcoded.

---

## Task 2.4 — Database Integration Smoke Test

> **INVARIANT TOUCH: INV-01, INV-11**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 2.4 TC-1 | Row count is 9 | test_row_count passes | PASS|
| 2.4 TC-2 | All 9 IDs present | test_all_ids_present passes |PASS |
| 2.4 TC-3 | Tier distribution is 3/3/3 | test_tier_distribution passes |PASS |
| 2.4 TC-4 | DEMO-001 factors match exactly (ordered) | test_demo001_factors_exact passes | PASS|
| 2.4 TC-5 | DEMO-007 is HIGH | test_demo007_tier passes |PASS |
| 2.4 TC-6 | Seed is idempotent | test_idempotency passes — count still 9 after second seed run | PASS|



**Verification command:**
```
docker compose exec fastapi-app python -m pytest tests/test_seed.py -v
```



**Code Review:**

> Check: test_demo001_factors_exact uses == not 'in' — order matters.
> Check: test_idempotency reads the actual seed.sql file, not a hardcoded INSERT.
> Check: teardown releases connections back to pool.

---


---

## Test Cases Added During Session

| Case | Scenario | Expected Outcome | Reason for Addition |
|---|---|---|---|
| | | | |

---

## Scope Decisions

> Note anything intentionally deferred and which task will cover it.

---

## Verification Verdict

- [x] All test cases have a Result entry
- [x] All CD Challenge outputs are pasted verbatim
- [x] All deviations are recorded in SESSION_LOG.md
- [x] No invariant was violated — or if violated, recorded and escalated

**Status:** Completed

**Engineer sign-off:** Y Vaishali Rao - 2026-03-31


# VERIFICATION_RECORD — S3: API Core
**Customer Risk API · Training Demo System**

| Field | Value |
|---|---|
| Session | S3 — API Core |
| Date |2026-03-31 |
| Engineer | Y Vaishali Rao|

> This record is completed during the session — not after. Predictions are written before tests are run. CD Challenge output is pasted verbatim. Nothing is backdated.

---

## Task 3.1 — Auth Dependency

> **INVARIANT TOUCH: INV-05, INV-06**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 3.1 TC-1 | Missing key returns 401 | curl /api/v1/customers/DEMO-001 with no header returns 401 | |
| 3.1 TC-2 | Wrong key returns 401 | curl with X-API-Key: wrongkey returns 401 | |
| 3.1 TC-3 | Correct key is accepted | curl with correct key returns 200 (after endpoint exists) | |
| 3.1 TC-4 | 401 body is exactly {"detail":"Unauthorized"} | response body contains no key value, no extra fields | |

**Predictions** (fill in before running):

- 3.1 TC-1:
- 3.1 TC-2:
- 3.1 TC-3:
- 3.1 TC-4:

**Verification command:**
```
curl -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/customers/DEMO-001
curl -s -H 'X-API-Key: wrongkey' -o /dev/null -w '%{http_code}' \
  http://localhost:8000/api/v1/customers/DEMO-001
curl -s -H 'X-API-Key: wrongkey' http://localhost:8000/api/v1/customers/DEMO-001
```

**CD Challenge Output:**
```
(paste output here)
```

**Code Review:**

> Check: detail is 'Unauthorized' — not the key value, not 'Invalid key: ...'.
> Check: auto_error=False so we control the 401, not FastAPI.
> Check: no logging of the key variable anywhere in this file.

---

## Task 3.2 — Customer Endpoint

> **INVARIANT TOUCH: INV-01, INV-02, INV-04**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 3.2 TC-1 | DEMO-001 returns correct shape | Response has customer_id, risk_tier, risk_factors and no other fields | |
| 3.2 TC-2 | risk_tier is exactly 'LOW' uppercase | DEMO-001 risk_tier == 'LOW' | |
| 3.2 TC-3 | risk_factors is a list not null | DEMO-001 risk_factors is a JSON array | |
| 3.2 TC-4 | DEMO-XXXX returns 404 | 404 with body {"detail":"Customer not found"} | |
| 3.2 TC-5 | Response has exactly 3 fields | No extra fields (created_at, id, etc.) in 200 response | |

**Predictions** (fill in before running):

- 3.2 TC-1:
- 3.2 TC-2:
- 3.2 TC-3:
- 3.2 TC-4:
- 3.2 TC-5:

**Verification command:**
```
TEST_KEY=$(grep API_KEY customer-risk-api/.env | cut -d= -f2)
curl -s -H "X-API-Key: $TEST_KEY" http://localhost:8000/api/v1/customers/DEMO-001 | python3 -m json.tool
curl -s -H "X-API-Key: $TEST_KEY" \
  -o /dev/null -w '%{http_code}' \
  http://localhost:8000/api/v1/customers/DEMO-XXXX
```

**CD Challenge Output:**
```
(paste output here)
```

**Code Review:**

> Check: parameterised query (%s, not f-string).
> Check: try/finally around get_conn/release_conn — connection released even on 404.
> Check: list(row[2]) not row[2] directly — ensures JSON serialisability.
> Check: no transformation of risk_tier (no .lower(), no .title()).

---

## Task 3.3 — Global Error Handlers

> **INVARIANT TOUCH: INV-04, INV-07**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 3.3 TC-1 | 422 on empty customer_id | GET /api/v1/customers/ with auth returns 422 with {"error":"Invalid request","status":422} | |
| 3.3 TC-2 | 404 envelope shape correct | {"error":"Customer not found","status":404} — no extra fields | |
| 3.3 TC-3 | 401 envelope shape correct | {"error":"Unauthorized","status":401} — no extra fields | |
| 3.3 TC-4 | /docs still returns 404 | curl /docs returns 404 | |
| 3.3 TC-5 | /openapi.json still returns 404 | curl /openapi.json returns 404 | |

**Predictions** (fill in before running):

- 3.3 TC-1:
- 3.3 TC-2:
- 3.3 TC-3:
- 3.3 TC-4:
- 3.3 TC-5:

**Verification command:**
```
TEST_KEY=$(grep API_KEY customer-risk-api/.env | cut -d= -f2)
curl -s -H "X-API-Key: $TEST_KEY" http://localhost:8000/api/v1/customers/DEMO-XXXX
curl -s http://localhost:8000/api/v1/customers/DEMO-001
curl -o /dev/null -w '%{http_code}' http://localhost:8000/docs
curl -o /dev/null -w '%{http_code}' http://localhost:8000/openapi.json
```

**CD Challenge Output:**
```
(paste output here)
```

**Code Review:**

> Check: generic Exception handler logs without including exc.__class__.__name__ or str(exc) in the response.
> Check: HTTPException handler uses exc.detail for 'error' field — verify 404 detail is 'Customer not found' not a generic string.
> Check: docs_url=None is still present on the FastAPI() constructor call.

---

## Task 3.4 — API Test Suite (customers and auth)

> **INVARIANT TOUCH: INV-01, INV-02, INV-04, INV-05**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 3.4 TC-1 | DEMO-001 exact projection passes | test_demo001_exact green | |
| 3.4 TC-2 | All tiers represented | test_all_tiers_represented green | |
| 3.4 TC-3 | Exactly 3 response fields | test_response_has_exactly_three_fields green | |
| 3.4 TC-4 | Tier enum values uppercase | test_risk_tier_is_uppercase_enum green — all 9 records | |
| 3.4 TC-5 | factors always a list | test_risk_factors_is_list_never_null green — all 9 records | |
| 3.4 TC-6 | Auth matrix complete | all 6 test_auth tests green | |

**Predictions** (fill in before running):

- 3.4 TC-1:
- 3.4 TC-2:
- 3.4 TC-3:
- 3.4 TC-4:
- 3.4 TC-5:
- 3.4 TC-6:

**Verification command:**
```
docker compose exec fastapi-app python -m pytest \
  tests/test_customers.py tests/test_auth.py -v
```

**CD Challenge Output:**
```
(paste output here)
```

**Code Review:**

> Check: test_demo001_exact uses == not 'in' for factor list (order matters, per INV-01).
> Check: test_risk_tier_is_uppercase_enum asserts no whitespace with .strip() comparison.
> Check: test_404_body_shape checks the full dict, not just the status code.

---

## Task 3.5 — Mutability Test Suite

> **INVARIANT TOUCH: INV-03, INV-07**

| Case | Scenario | Expected Outcome | Result |
|---|---|---|---|
| 3.5 TC-1 | No DB write on 200 | test_no_write_on_200 passes | |
| 3.5 TC-2 | No DB write on 404 | test_no_write_on_404 passes | |
| 3.5 TC-3 | No DB write on 401 | test_no_write_on_401 passes | |
| 3.5 TC-4 | No DB write on 422 | test_no_write_on_422 passes | |
| 3.5 TC-5 | Error bodies contain no internal detail | test_error_body_no_internal_detail passes | |
| 3.5 TC-6 | 503 on DB down with clean body | test_503_on_db_down passes | |

**Predictions** (fill in before running):

- 3.5 TC-1:
- 3.5 TC-2:
- 3.5 TC-3:
- 3.5 TC-4:
- 3.5 TC-5:
- 3.5 TC-6:

**Verification command:**
```
docker compose exec fastapi-app python -m pytest tests/test_errors.py -v
```

**CD Challenge Output:**
```
(paste output here)
```

**Code Review:**

> Check: db_snapshot uses ORDER BY to make comparison order-deterministic.
> Check: denylist in test 5 includes lowercase variants ('postgres', 'Postgres').
> Check: test_503 restarts postgres even if the assertion fails — use try/finally.

---

## Session Integration Check

```
TEST_KEY=$(grep API_KEY .env | cut -d= -f2)
curl -s -H "X-API-Key: $TEST_KEY" http://localhost:8000/api/v1/customers/DEMO-001
curl -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/customers/DEMO-001
```

Expected:
- First: `{"customer_id":"DEMO-001","risk_tier":"LOW","risk_factors":["Low transaction volume","Account age > 5 years","No adverse history"]}`
- Second (no key): `401`

**Output:**
```
(paste output here)
```

---

## Test Cases Added During Session

| Case | Scenario | Expected Outcome | Reason for Addition |
|---|---|---|---|
| | | | |

---

## Scope Decisions

> Note anything intentionally deferred and which task will cover it.

---

## Verification Verdict

- [ ] All test cases have a Result entry
- [ ] All CD Challenge outputs are pasted verbatim
- [ ] All deviations are recorded in SESSION_LOG.md
- [ ] No invariant was violated — or if violated, recorded and escalated

**Status:** In Progress

**Engineer sign-off:** _______________

