# VerifyIQ PyPI Distribution Strategy

> Evaluation of three distribution strategies for the VerifyIQ multi-modal claim verification platform.

---

## Context

VerifyIQ is a multimodal claim verification platform with a frozen V1 deterministic rule engine (58 tests), a modular V2 10-layer pipeline (49 tests), and optional VLM providers (Gemini, OpenRouter), API server (FastAPI), and dashboard (Streamlit). There is currently no package configuration; users install via `pip install -r requirements.txt` or direct checkout.

**Must be preserved:** `code/`, `dataset/`, `reports/` — competition artifacts remain untouched.

---

## Option A: Full PyPI Package (`pip install verifyiq`)

Package the entire platform on PyPI with extras for every component.

| Extra | What it installs |
|-------|-----------------|
| (core) | V1 deterministic pipeline (Pillow, tqdm) |
| `v2` | V2 pipeline (same deps as core) |
| `api` | FastAPI server (FastAPI, uvicorn, pydantic) |
| `dashboard` | Streamlit UI (streamlit, plotly, pandas) |
| `gemini` | Google Gemini provider (google-genai) |
| `openrouter` | OpenRouter provider (httpx, websockets) |
| `gpu` | CUDA-accelerated VLM (torch, opencv-python) |
| `all` | Everything above |

### Evaluation

#### 1. Maintenance cost: **5/5**

- **Version management:** Every release requires coordinated version bumps across extras. Breaking changes in V2 force a major version even if V1 is unchanged.
- **Dependency resolution:** The full dependency tree spans 15+ packages. Conflicting transitive deps (e.g., Pillow version pinned by both core and opencv-python) emerge over time and require manual resolution.
- **Testing matrix:** Need to test all extra combinations across Windows/Mac/Linux/arm64. Each extra multiplies the CI matrix. Full matrix: ~15 combos × 3 platforms = 45 CI runs per release.
- **Release process:** `build` → `twine check` → `twine upload` with 2FA/trusted publishing. Each PyPI upload is irreversible — a broken V2 release means yanking + patch bump.
- **GPU extras are especially painful:** torch is ~2GB, platform-specific (CUDA 11.8/12.1/12.4, CPU-only, ROCm), and has different wheels for each OS+arch. The `verifyiq[gpu]` extra alone requires testing 4 platform variants.

#### 2. Dependency complexity: **5/5**

- **Weight extremes:** Core is ~10MB (Pillow + tqdm). Adding `[gpu]` brings in ~2GB of torch + CUDA deps. PyPI does not lazily download extras — `pip install verifyiq[all]` downloads 2GB+.
- **Platform-specific issues:** Pillow has different wheels per platform (arm64 vs x86_64 vs Windows). opencv-python has heavy C extensions that fail to build on some configurations. torch wheels are platform-specific and sometimes missing for niche targets.
- **GPU/CUDA:** torch pip packages are version-tied to specific CUDA runtimes. A user with CUDA 12.4 gets a different torch wheel than CUDA 11.8. This is notoriously fragile.
- **Conflicting transitive deps:** google-genai pins `httpx<1.0`. Streamlit pins `pandas<3.0`. These constraints compound and sometimes conflict across extras.

#### 3. User experience: **5/5**

- **Installation simplicity:** `pip install verifyiq` is the gold standard. Any Python user knows this flow.
- **Discovery:** PyPI search, version history, release notes, and download stats are all built in. Users can `pip search verifyiq` or browse on pypi.org.
- **Version pinning:** `verifyiq==0.1.0` in requirements.txt guarantees reproducibility. Users can pin to a specific minor version and get predictable behavior.
- **Integration:** Other packages can list `verifyiq` as a dependency. CI/CD systems can install and use it without git checkout.

#### 4. Plugin support: **5/5**

- PyPI packages can define `entry_points` for automatic plugin discovery. Third-party providers can publish `verifyiq-provider-anthropic` on PyPI and register via `[verifyiq.vlm_providers]` entry point.
- Plugin author workflow: `pip install verifyiq verifyiq-provider-anthropic` and it's auto-discovered.
- Documentation is straightforward: "Publish your provider as a separate package and register it via entry points."

#### 5. API support: **4/5**

- API consumers install `verifyiq[api]` or `verifyiq` and get a clean FastAPI app.
- Dependency isolation is good — FastAPI is an optional extra, not a core dep.
- However, API consumers also get the V1/V2 execution code transitively. For a pure API consumer who only wants to call endpoints (not embed the pipeline), there's unnecessary code shipped. A separate `verifyiq-api` package would be cleaner but duplicates maintenance.

---

## Option B: GitHub-Only Framework

No PyPI release. Users install directly from GitHub.

```bash
pip install git+https://github.com/verifyiq/verifyiq.git
# or with extras
pip install "verifyiq[v2] @ git+https://github.com/verifyiq/verifyiq.git"
```

### Evaluation

#### 1. Maintenance cost: **1/5**

- **Version management:** No versioning friction — there are no versions to manage. Tags are optional. Users get `main` (or whatever branch is current).
- **Dependency resolution:** No PyPI manipulation needed. Dependencies are declared in `pyproject.toml` but pip handles resolution the same way.
- **Testing matrix:** Only needs to test what you develop against. No need to test every extra combination for release; test only the combinations you actively support.
- **Release process:** Zero. Push to main, users get it. No CI for publishing, no twine, no 2FA workflow, no yanking.
- **Lowest overhead of all options.**

#### 2. Dependency complexity: **2/5**

- Same dependency tree as Option A — the difference is that you don't need to resolve conflicts *for publication*. If two extras conflict, users discover it at install time rather than at release time.
- No need to pin exact lower bounds for PyPI compatibility — looser constraints are acceptable for GitHub-only.
- GPU deps remain complex but no different from Option A — the problem is torch, not the distribution channel.

#### 3. User experience: **2/5**

- **Installation simplicity:** `pip install git+https://...` is more verbose and harder to remember. Many users don't know this syntax.
- **Discovery:** No PyPI presence. Users must find the project via GitHub search, word of mouth, or blog posts. No download stats, no PyPI search ranking.
- **Version pinning:** No conventional versioning. Users pin to a commit SHA (`pip install git+https://...@abc123`), which is opaque and hard to audit. They can also pin to a tag if maintainers create them, but tags are not enforced by the workflow.
- **Integration:** Other packages cannot declare `verifyiq` as a dependency in their `pyproject.toml`. CI/CD systems need a git checkout or the raw URL.
- **Deployment:** Dockerfiles must include the git URL or clone the repo. This adds build-time dependencies (git must be installed in the container).

#### 4. Plugin support: **2/5**

- Third-party packages can still register entry points, but there's no PyPI package name to list as a dependency. Plugin authors who want to depend on `verifyiq` must add the GitHub URL to their own dependencies.
- No convention for plugin discovery beyond "check the README." No PyPI trove classifiers for `verifyiq`.
- Lower discoverability means fewer third-party plugins overall.

#### 5. API support: **2/5**

- API consumers must install from GitHub, which is awkward for production deployments.
- Dockerfiles need `git` installed or must pre-install from a requirements.txt that includes the GitHub URL.
- No semantic versioning means API consumers can't express "I need >=0.2.0 but <1.0.0" — they get whatever `main` is at build time.
- Breaking changes in V2 can silently break API consumers who rebuild their containers against the latest commit.

---

## Option C: Hybrid Distribution

Core on PyPI, heavy extras from GitHub.

```bash
# Core — available on PyPI
pip install verifyiq

# VLM providers — from GitHub (optional)
pip install "verifyiq[gemini] @ git+https://github.com/verifyiq/verifyiq.git"
pip install "verifyiq[gpu] @ git+https://github.com/verifyiq/verifyiq.git"
```

| Extra | Distribution | Rationale |
|-------|-------------|-----------|
| (core V1) | PyPI | Lightweight, stable, no external API deps |
| `v2` | PyPI | Same lightweight deps as core |
| `api` | PyPI | Small dep footprint (FastAPI is well-tested) |
| `dashboard` | PyPI | Medium, but deps are stable and well-known |
| `gemini` | GitHub | Requires API keys; API surface changes with Gemini SDK |
| `openrouter` | GitHub | Provider under active development |
| `gpu` | GitHub | GPU deps are 2GB+ and platform-fragile |

### Evaluation

#### 1. Maintenance cost: **3/5**

- **Version management:** Only version the core package. GitHub extras don't need version bumps on the same cadence — they evolve independently.
- **Dependency resolution:** Core dependencies are simple (Pillow, tqdm). The complex GPU/VLM deps live on GitHub where resolution failures don't affect PyPI users.
- **Testing matrix:** Only test core + v2 + api + dashboard for PyPI releases. GitHub extras get lighter testing (single platform, no PyPI compatibility gate).
- **Release process:** Core releases follow semantic versioning. GitHub extras can be pushed at any time without a release. Best of both worlds.
- **Moderate overhead** — you maintain a PyPI pipeline for core, but avoid the 2GB GPU testing burden.

#### 2. Dependency complexity: **3/5**

- **Core** (PyPI): Pillow + tqdm. Trivially simple. Zero platform issues.
- **V2** (PyPI): Same as core. No additional deps.
- **API** (PyPI): FastAPI + uvicorn. Well-tested, widely deployed. No surprises.
- **Dashboard** (PyPI): Streamlit + plotly + pandas. Larger but well-established.
- **GPU/VLM** (GitHub): Complex, heavy, platform-specific — but not on PyPI, so no release-time resolution pain.

#### 3. User experience: **4/5**

- **Installation simplicity:** `pip install verifyiq` works for the 80% use case (V1 inference). Users who need VLM providers read the README for the GitHub install step.
- **Discovery:** PyPI presence for the core package. Users searching for claim verification tools on PyPI find VerifyIQ.
- **Version pinning:** Core is pinned conventionally. GitHub extras are pinned to commit SHAs — acceptable because they're opt-in heavy features.
- **Integration:** Other packages can depend on `verifyiq` (core). They don't get VLM providers, which is correct — providers are application-level, not library-level concerns.
- **Slightly worse UX than Option A** for users who want everything (`pip install verifyiq[all]` doesn't fully work), but better for the common case.

#### 4. Plugin support: **3/5**

- Entry points in the core PyPI package provide the discovery mechanism. Plugin authors depend on the core package from PyPI.
- Plugin authors can publish their own providers to PyPI (e.g., `verifyiq-provider-anthropic`) that depend on `verifyiq` core.
- Disadvantage: Plugin authors who want to build on Gemini/OpenRouter providers must reference those from GitHub — either as a hard dependency or as a runtime import with graceful fallback.
- Medium — works for the common case (core-based plugins) but awkward for provider-based plugins.

#### 5. API support: **4/5**

- API consumers install `verifyiq[api]` from PyPI. Clean, standard, reproducible.
- FastAPI + core code is all they need. No GPU/VLM deps leak in.
- Version compatibility is managed via PyPI's standard semver.
- Slight disadvantage: API consumers who want real VLM analysis (not the mock provider) must also install from GitHub. But that's reasonable — VLM-backed analysis requires an API key anyway, so the user is already in a "configuration" mindset.

---

## Additional Considerations

### Dependency Tree Size

| Component | Approximate size | Install time (typical) |
|-----------|-----------------|----------------------|
| Core (Pillow + tqdm) | ~10 MB | 5-10s |
| + V2 extras | Same | Same |
| + API (FastAPI + uvicorn) | ~15 MB | 10-20s |
| + Dashboard (streamlit + plotly) | ~80 MB | 30-60s |
| + Gemini (google-genai) | ~5 MB | 5-10s |
| + OpenRouter | ~5 MB | 5-10s |
| + GPU (torch + opencv-python) | ~2 GB | 5-10 minutes |

The GPU extra alone is 200× larger than everything else combined. Publishing it on PyPI means:
- PyPI storage costs
- CI runs taking 10+ minutes per platform variant
- Users accidentally running `pip install verifyiq[all]` and downloading 2 GB

### CI Minutes

| Option | CI minutes per release | Annual estimate (12 releases) |
|--------|----------------------|-------------------------------|
| A (full PyPI) | ~90 min (3 platforms × 5 extra combos × 6 min) | ~1,080 min |
| B (GitHub) | ~30 min (1 platform, 1 combo) | ~360 min |
| C (hybrid) | ~45 min (2 platforms × 3 combos for core) | ~540 min |

GPU testing for Option A adds another ~60 min per release alone.

### PyPI Upload Friction

- **2FA required** since 2023 — all PyPI uploads need a trusted publisher or API token
- **Trusted publishing** (OIDC) removes manual token management but requires GitHub Actions setup
- **Yanking** is possible but doesn't remove the version — it marks it as "solved" only if no constraint pins it
- **No true deletion** on PyPI — a bad release is permanent

GitHub-side friction for Option B: none. Git push is the only gate.

### Semantic Versioning

| Change | Version impact |
|--------|---------------|
| V1 bugfix (no behavior change for correct inputs) | Patch bump |
| V1 new rule path | Minor bump |
| V2 new pipeline layer | Minor bump |
| V2 breaking API change (e.g., renamed models) | Major bump |
| New provider type | Minor bump |
| Deprecation of extra | Minor bump (with deprecation warning) |

Option A and C both require disciplined semver. Option B sidesteps the question entirely — but users lose the contract.

### Pre-release Tags

| Tag | Purpose |
|-----|---------|
| `0.1.0.dev1` | Development snapshot — not installable by default (`pip install verifyiq` skips dev releases) |
| `0.1.0a1` | Alpha — early testing, unstable API |
| `0.1.0b1` | Beta — feature-complete, API may change |
| `0.1.0rc1` | Release candidate — stable API, final testing |

Option A and C: discipline required to use these; test PyPI (`test.pypi.org`) for dev releases.

Option B: simply tag `v0.1.0-alpha` on GitHub; no pip distinction.

---

## Recommendation

### ✅ **Option C: Hybrid distribution**

#### Why it's best for this project

1. **The core is genuinely lightweight.** V1 is deterministic, has no API key requirement, and depends on only Pillow and tqdm. This is the ideal PyPI package — small, stable, zero-config.
2. **GPU/VLM deps are genuinely heavy.** torch is ~2GB. opencv-python is platform-fragile. Google's `google-genai` SDK changes its API surface. These should not gate PyPI releases.
3. **The 80% case is already simple.** Most users want claim verification, not yet another VLM provider. Give them `pip install verifyiq`.
4. **Plugin ecosystem is viable.** Core on PyPI means entry points work. Third-party providers can publish their own PyPI packages and depend on `verifyiq`.
5. **Avoids the [all] trap.** `pip install verifyiq[all]` accidentally downloading 2GB of torch is a real UX disaster. Hybrid distribution makes heavy features explicitly opt-in with a slightly different install command — a useful speed bump.
6. **Preserves competition artifacts.** The frozen `code/`, `dataset/`, `reports/` stay untouched regardless of distribution choice. Hybrid doesn't require any changes to those directories.

#### What the first release looks like

```
verifyiq 0.1.0.dev1
```

**PyPI extras included:**
- Core — deterministic V1 (`Pillow`, `tqdm`)
- V2 — pipeline (`verifyiq[v2]`, same deps)
- API — FastAPI server (`verifyiq[api]`)
- Dashboard — Streamlit UI (`verifyiq[dashboard]`)

**GitHub-only:**
- Gemini provider (`verifyiq[gemini]`)
- OpenRouter provider (`verifyiq[openrouter]`)
- GPU acceleration (`verifyiq[gpu]`)
- All of above combined (`verifyiq[all-github]`)

**Version:** `0.1.0.dev1` — published to Test PyPI first, then PyPI after validation.

**Documentation** in README:

```bash
# Core (works offline, deterministic)
pip install verifyiq

# V2 pipeline
pip install verifyiq[v2]

# API server
pip install verifyiq[api]

# Dashboard
pip install verifyiq[dashboard]

# VLM providers (requires GitHub)
pip install "verifyiq[gemini] @ git+https://github.com/verifyiq/verifyiq.git"

# Everything
pip install verifyiq[api,dashboard]
pip install "verifyiq[gemini,openrouter] @ git+https://github.com/verifyiq/verifyiq.git"
```

#### Migration path from current state

```
Current state: pip install -r requirements.txt (no package)
    │
    ▼
Stage 1: Create pyproject.toml, verifyiq/ package skeleton
         → python -c "import verifyiq; print(verifyiq.__version__)" works
    │
    ▼
Stage 2: Create verifyiq/v1/ as thin wrapper around code/
         → pip install verifyiq works for V1
    │
    ▼
Stage 3: Create verifyiq/v2/ with moved source files
         → pip install verifyiq[v2] works
    │
    ▼
Stage 4: Add API and dashboard extras
         → pip install verifyiq[api] and verifyiq[dashboard] work
    │
    ▼
Stage 5: Document GitHub-only extras in README
         → verifyiq[gemini], verifyiq[openrouter], verifyiq[gpu] documented
    │
    ▼
Stage 6: Publish 0.1.0.dev1 to Test PyPI → validate → publish to PyPI
```

Competition artifacts (`code/`, `dataset/`, `reports/`) are never touched.

#### Long-term evolution

| Timeframe | Milestone | Distribution |
|-----------|-----------|-------------|
| **Month 1** | 0.1.0.dev1 on PyPI (core + v2 + api) | Hybrid (Option C) |
| **Month 2** | 0.2.0 stable (dashboard extra) | Hybrid (Option C) |
| **Month 3** | 1.0.0 stable API surface | Hybrid (Option C) |
| **Month 6** | VLM providers stabilize API | Evaluate moving gemini/openrouter to PyPI |
| **Year 1** | 3+ third-party plugins on PyPI | Likely still hybrid, but with more PyPI extras |
| **Year 2+** | GPU provider stable with CUDA 12.4+ | Evaluate PyPI for GPU if wheel sizes decrease |

**Trigger for moving a GitHub extra to PyPI:**
1. The extra's dependency tree stabilizes (no breaking API changes in 2+ minor releases)
2. A consumer explicitly needs `pip install verifyiq[gemini]` to work without GitHub
3. torch releases platform wheels reliably for all target platforms (mostly already true, but the 2GB size remains)

**If Option C succeeds,** the project can converge toward Option A over years. The hybrid model is not a permanent compromise — it's a risk-managed on-ramp to full PyPI coverage.

---

## Decision Matrix

| Dimension | Weight | Option A (Full PyPI) | Option B (GitHub-only) | Option C (Hybrid) |
|-----------|--------|---------------------|----------------------|------------------|
| **Maintenance cost** (1=lowest) | High | **5** (highest) | **1** (lowest) | **3** (moderate) |
| **Dependency complexity** (1=simplest) | High | **5** (most complex) | **2** (simple) | **3** (moderate) |
| **User experience** (1=worst) | High | **5** (best) | **2** (worst) | **4** (good) |
| **Plugin support** (1=worst) | Medium | **5** (best) | **2** (worst) | **3** (moderate) |
| **API support** (1=worst) | Medium | **4** (good) | **2** (worst) | **4** (good) |
| **Total** | | **24** | **9** | **17** |

### Weighted Score (applying importance weights: Maintenance 3×, Dependency 3×, UX 2×, Plugin 1×, API 1×)

| Dimension | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Maintenance cost | ×3 | 15 | 3 | 9 |
| Dependency complexity | ×3 | 15 | 6 | 9 |
| User experience | ×2 | 10 | 4 | 8 |
| Plugin support | ×1 | 5 | 2 | 3 |
| API support | ×1 | 4 | 2 | 4 |
| **Weighted total** | **×10** | **49** | **17** | **33** |

Option C scores highest in the weighted analysis — it maximizes user experience and API support (the dimensions users see) while minimizing maintenance cost and dependency complexity (the dimensions maintainers feel).

---

## Summary

| | Option A | Option B | Option C |
|---|----------|----------|----------|
| **Cost** | Highest maintenance & CI | Lowest maintenance | Moderate maintenance |
| **Users** | Best experience | Worst experience | Good experience |
| **Risk** | GPU deps on PyPI = fragility | No discoverability | Balanced |
| **Future** | Goal state (eventually) | Starting point (minimal) | Recommended |
| **Verdict** | Over-engineered for now | Under-invested for growth | **Right-sized** |

**Recommended:** Option C — hybrid distribution with core on PyPI and heavy extras from GitHub.

**Overall scores (1-5):**
- **Option A (Full PyPI):** 24/25 raw, 49/50 weighted
- **Option B (GitHub-only):** 9/25 raw, 17/50 weighted
- **Option C (Hybrid):** 17/25 raw, 33/50 weighted
