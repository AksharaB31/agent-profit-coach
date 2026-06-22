# Agent Profit Coach — Implementation Plan

## Overview
Fix, stabilize, and enhance the Agent Profit Coach pipeline to reliably
"guide agents toward higher-margin decisions."

---

## Phase 1 — Fix Broken Core (High Priority)

### 1.1 Fix ML Model Loading Path

**Files:** `app/domain/ai_engine/inference_engine.py`  
**Issue:** `__init__` line 19 points to `saved_models/` dir which doesn't exist.  
**Fix:**
```python
# change line 19 from:
self.model_dir = Path(__file__).resolve().parent / "saved_models"
# to:
self.model_dir = Path(__file__).resolve().parents[3] / "ml" / "models"
```
**Result:** Actually loads `conversion_model.pkl` from `app/ml/models/`.

**Verify:** Check that `self.conversion_model` is no longer `None` at startup.

---

### 1.2 Replace Dummy Training Scripts with Real Training

**Files:**
- `app/ml/training/train_conversion_model.py`
- `app/ml/training/train_profit_model.py`

**Current state:** Both generate dummy models that return constant values (0.75 and 1500).

**Proposed changes:**

**`train_conversion_model.py`:**
- Query `Booking` + `BookingProcess` from the read-only DB
- Feature columns: `price`, `duration_minutes`, `stops`, `is_refundable`, `month`, `day_of_week`, `advance_purchase_days`
- Target: `is_successful` (1 if `BookingProcess.state` in `SUCCESS|COMPLETED|TICKETED|CONFIRMED`)
- Train a `RandomForestClassifier(n_estimators=100, max_depth=10)`
- Save to `app/ml/models/conversion_model.pkl` via `joblib.dump`

**`train_profit_model.py`:**
- Query `BookingAdjustedFare.agent_profit` grouped by supplier/airline/route
- Train simple model predicting expected agent profit
- Save to `app/ml/models/ml_profit_model_oneway_v1.pkl` and `ml_profit_model_roundtrip_v1.pkl`

**Addition:** Add a `scripts/retrain_models.py` helper that runs both scripts and logs results.

---

### 1.3 Wire AgentLoader into Scoring Pipeline

**Files:**
- `app/services/agent_profit_coach/response_builder/enterprise_response_builder.py`
- `app/services/agent_profit_coach/db_loader/agent_loader.py`
- `app/api/schemas.py` (add optional `agent_id` to `ProfitCoachRequest`)
- `app/api/v1/endpoints/agent_profit_coach.py` (pass `agent_id` from payload)

**Changes:**

**Step 1 — Add optional `agent_id` to request schema:**
```python
class ProfitCoachRequest(BaseModel):
    trip_type: str
    origin: str
    destination: str
    departure_date: str
    agent_id: Optional[int] = None          # NEW
```

**Step 2 — Initialize AgentLoader in `EnterpriseResponseBuilder.__init__`:**
```python
self.agent_loader = AgentLoader(db)
```

**Step 3 — In `build()`, load profile and adjust scoring:**
Before scoring each itinerary:
```python
agent_profile = self.agent_loader.get_agent_profile(payload.agent_id)
```
Then in the scoring pass, pass `agent_profile` to `scoring_engine.score_itinerary()`.

**Step 4 — Scoring engine uses profile to adjust weights:**
In `itinerary_scoring_engine.py`, use agent profile to influence:
- `profit_score` weight (premium agents care more about profit)
- `refundability_score` weight (agents with high refund preference get a boost for refundable fares)
- Preferred supplier bias (small score boost for agent's historically preferred supplier)

**Step 5 — Update frontend sidebar:**
Add optional `Agent ID` input field in `frontend/components/sidebar.py`.

---

## Phase 2 — Stabilize & Clean Up (Medium Priority)

### 2.1 Use Config Weights in Main Pipeline

**File:** `app/services/agent_profit_coach/response_builder/enterprise_response_builder.py`

**Current (line 141):**
```python
profit_opportunity_score_100 = (revenue_score * 0.65) + (reliability_score_norm * 0.20) + (convenience_score_norm * 0.15)
```

**Replace with:**
```python
from app.core.config import settings
profit_opportunity_score_100 = (
    revenue_score * settings.PROFIT_WEIGHT +
    reliability_score_norm * settings.RELIABILITY_WEIGHT +
    convenience_score_norm * (1.0 - settings.PROFIT_WEIGHT - settings.RELIABILITY_WEIGHT)
)
```

Also apply to `score_breakdown` dict. This makes weights configurable via `.env`.

---

### 2.2 Fix FinalRankingService Crash

**File:** `app/services/profit_coach/ranking/final_ranking_service.py`

**Current (lines 11-18):** References nonexistent `settings.PROFIT_COACH_WEIGHT_PRICE`, etc.

**Option A — Fix (if keeping the old engine):**
```python
from app.core.config import settings

final_score = (
    scores.get("price_score", 0) * settings.PRICE_WEIGHT +
    scores.get("profit_score", 0) * settings.PROFIT_WEIGHT +
    scores.get("reliability_score", 0) * settings.RELIABILITY_WEIGHT +
    scores.get("duration_score", 0) * settings.CONVENIENCE_WEIGHT * 0.5 +
    scores.get("convenience_score", 0) * settings.CONVENIENCE_WEIGHT * 0.5
    # baggage, refundability, meals — weighted within remaining margin
)
```

**Option B — Deprecate:** Mark the old `ProfitCoachEngine` and all its callers as deprecated with a `DeprecationWarning`.

---

### 2.3 Remove Dead Code

**Rationale:** Reduces maintenance surface, eliminates confusion, and makes the codebase reflect what actually runs.

**Action Plan:**

| File / Directory | Disposition |
|---|---|
| `app/services/analytics/*.py` (4 files) | Delete — logic is duplicated in the new engine |
| `app/services/supplier_profit_service.py` | Delete — unused |
| `app/services/route_profit_service.py` | Delete — unused |
| `app/services/recommendation_service.py` | Delete — unused |
| `app/services/profit_insight_service.py` | Delete — unused |
| `app/infra/mysql/*_queries.py` (4 files) | Delete — raw SQL never called, ORM used instead |
| `app/infra/external/*.py` (3 files) | Delete — stubs, no integration wired |
| `app/ml/inference/*.py` (3 files) | Delete — superseded by `AIInferenceEngine` |
| `app/services/profit_coach/` (entire dir) | Either delete OR rename to `_legacy_profit_coach/` |

**Keep (in use):**
- `app/services/agent_profit_coach/` — the main engine
- `app/domain/`, `app/infra/mysql/` (models, database), `app/infra/` (redis, telemetry)
- `app/ml/` (models + training scripts)

---

### 2.4 Add File Upload Endpoint

**Rationale:** Laravel team sends flight search JSON files. Currently must be manually saved to `data/`. Add an API endpoint so they can push results programmatically.

**New file:** `app/api/v1/endpoints/search_upload.py`

```python
router = APIRouter()

@router.post("/upload-search-results")
def upload_search_results(
    payload: SearchUploadRequest,
    db: Session = Depends(get_db)
):
    """Accepts flight search JSON from Laravel team, validates, stores to data/."""
    # 1. Validate JSON structure
    # 2. Detect trip_type from content
    # 3. Write to data/{trip_type}_{timestamp}.json
    # 4. Return file_id for later use in /agent-profit-coach
```

**Schema addition** in `app/api/schemas.py`:
```python
class SearchUploadRequest(BaseModel):
    trip_type: Literal["oneway", "roundtrip"]
    search_data: List[Dict[str, Any]]
```

**Update `ProfitCoachRequest`** to accept optional `search_file` parameter so a specific uploaded file can be referenced:
```python
search_file: Optional[str] = None  # filename to use instead of default roundtrip/oneway.json
```

**Wire into router** in `app/api/v1/endpoints/__init__.py` or `app/api/router.py`.

---

### 2.5 Clean Up Routing Inconsistency

**Files:** `app/api/router.py`, `app/api/v1/router.py`

**Current state:**
- `/api/v1/agent-profit-coach` — main endpoint (correct)
- `/api/route-profit` — old endpoint (no `/v1`)
- `/api/supplier-profit` — old endpoint (no `/v1`)
- `/api/profit-recommendation` — old endpoint (no `/v1`)
- `/api/profit-insights` — old endpoint (no `/v1`)
- `/api/missed-profit` — old endpoint (no `/v1`)
- `/api/health` — health check
- `/api/version` — version

**Fix:**
1. Move all old endpoints under `/api/v1/...` by including them through the v1 router
2. Or remove them if they're truly unused (only frontend agent calls `/agent-profit-coach`)

**Simplified `app/api/router.py`:**
```python
router = APIRouter(prefix="/v1")
router.include_router(agent_router)
router.include_router(health_router)
router.include_router(version_router)
router.include_router(search_upload_router)   # new from 2.4
# optionally: router.include_router(old_endpoint_routers) under /v1

api_router = APIRouter(prefix="/api")
api_router.include_router(router)
```

---

## Phase 3 — Enhancements (Lower Priority)

### 3.1 Close the Feedback Loop

**Files:**
- `app/services/agent_profit_coach/db_loader/feedback_repository.py` (rename from `AIFeedbackRepository`)

**Steps:**
1. After a booking is completed (via the Laravel system), the Laravel team calls a new webhook:
   ```
   POST /api/v1/booking-outcome
   {
     "recommendation_id": "...",
     "booked": true,
     "cancelled": false,
     "profit_earned": 125.50,
     "supplier_code": "SABRE",
     "route": "DXB-DEL"
   }
   ```
2. This writes to `data/ai_training/feedback_loop.json`
3. Monthly scheduled job calls `train_conversion_model.py` which ingests this feedback data and retrains the model

**Add new endpoint:** `app/api/v1/endpoints/booking_outcome.py`

---

### 3.2 Per-Agent Scoring (Continuation of 1.3)

Once AgentLoader is wired in (1.3), enhance the scoring with:

- **Weight adjustment matrix** in config:
  ```python
  class Settings:
      AGENT_PROFILE_WEIGHTS = {
          "premium": {"profit": 0.50, "reliability": 0.20, "convenience": 0.15},
          "budget":  {"profit": 0.30, "reliability": 0.25, "convenience": 0.25},
      }
  ```
- **Preferred supplier boost:** +0.05 score bonus for agent's top 3 suppliers
- **Refund preference:** Increase refundability weight for agents with high historical refund rate

---

### 3.3 Secure Secrets

**File:** `.env.example`

```diff
- SECRET_KEY=super-secret-key
- API_KEY=agentprofit-secret
+ SECRET_KEY=change-this-in-production
+ API_KEY=change-this-in-production
```

Add `.env.example` entries for the new configurable scoring weights:
```env
PROFIT_WEIGHT=0.40
RELIABILITY_WEIGHT=0.25
PRICE_WEIGHT=0.15
CONVENIENCE_WEIGHT=0.10
CONVERSION_WEIGHT=0.10
```

---

### 3.4 Align Frontend Payload with Pydantic Schema

**File:** `frontend/components/sidebar.py` (lines 37-45)

**Current payload sends** `adults`, `children`, `cabin_class` which are NOT in `ProfitCoachRequest` Pydantic schema:

```python
payload = {
    "origin": origin,
    "destination": destination,
    "trip_type": trip_type,
    "departure_date": departure_date.strftime("%Y-%m-%d"),
    "adults": 1,            # REMOVE — not in schema
    "children": 0,          # REMOVE — not in schema
    "cabin_class": "Economy"  # REMOVE — not in schema
}
```

**Option A — Remove unused fields** if the API doesn't need them.

**Option B — Add them to the Pydantic schema** if they should influence scoring:
```python
class ProfitCoachRequest(BaseModel):
    trip_type: str
    origin: str
    destination: str
    departure_date: str
    adults: int = 1              # ADD
    children: int = 0            # ADD
    cabin_class: str = "Economy" # ADD
```

If Option B, also:
- Add `adults + children` as `passenger_count` to scoring features (influences total price threshold)
- Add `cabin_class` to itinerary scoring (business class = different profit profile)

---

## Verification Checklist

| After each phase | Command |
|---|---|
| App starts without import errors | `uvicorn app.main:app --reload` |
| Root endpoint responds | `curl http://localhost:8000/` |
| Health check passes | `curl http://localhost:8000/api/v1/health` |
| Agent profit coach returns valid response | `curl -X POST http://localhost:8000/api/v1/agent-profit-coach -H "Content-Type: application/json" -d '{"trip_type":"oneway","origin":"DXB","destination":"DEL","departure_date":"2026-07-15"}'` |
| Unit tests pass | `pytest app/tests/ -v` |
| Frontend renders | `streamlit run frontend/app.py` |
| ML model returns non-zero | Check logs for `conversion_probability > 0` |
| Dead code removal doesn't break app | `uvicorn app.main:app --reload` after each deletion |

---

## Effort Estimate

| Phase | Estimated Effort | Dependencies |
|---|---|---|
| **1.1** Fix model path | 15 min | None |
| **1.2** Real training scripts | 2-4 hours | DB access, understanding of historical data schema |
| **1.3** Wire AgentLoader | 4-6 hours | 1.1, schema change, frontend update |
| **2.1** Config weights | 30 min | None |
| **2.2** Fix FinalRankingService | 30 min | Decision: fix or deprecate |
| **2.3** Remove dead code | 1-2 hours | Careful per-file verification |
| **2.4** File upload endpoint | 2-3 hours | Schema + router wiring |
| **2.5** Routing cleanup | 1 hour | Coordinate with Laravel team on URL changes |
| **3.1** Feedback loop | 3-4 hours | Laravel team cooperation for webhook |
| **3.2** Per-agent scoring | 2-3 hours | Depends on 1.3 |
| **3.3** Secure secrets | 15 min | None |
| **3.4** Frontend payload | 30 min | Decision: A or B |

**Total:** ~18-26 hours

---

## Questions to Resolve

1. **Old endpoints** — Should the 4 legacy endpoints (`/supplier-profit`, `/route-profit`, `/profit-recommendation`, `/profit-insights`) be removed or kept under `/v1`?
2. **Agent personalization** — Should we make agent-specific profiles a priority (Phase 1.3) or is one-size-fits-all fine for now?
3. **Conversion model** — Should I train a real Random Forest on the historical DB data, or keep the dummy model that always returns 0.75?
4. **Frontend extra fields** — Add `adults`/`cabin_class` to the API schema (Option B) or just remove them from the frontend payload (Option A)?
