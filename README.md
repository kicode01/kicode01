<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/status-island-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/status-island-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/status-island-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/status-island-light-static.svg">
  <img src="assets/status-island-light-static.svg" width="100%" alt="Kian B. — Computer Engineering · Silicon to Model">
</picture>
</p>

<p align="center">
  <a href="#01--silicon-die-floorplan"><code>[01_CORE_DIE]</code></a> &nbsp;·&nbsp;
  <a href="#02--native-jit-disassembly--empirical-proof"><code>[02_DISASSEMBLY_BENCH]</code></a> &nbsp;·&nbsp;
  <a href="#03--modular-system-specifications"><code>[03_SYSTEM_SPECS]</code></a> &nbsp;·&nbsp;
  <a href="#04--event-driven-issueops-telemetry"><code>[04_ISSUEOPS_RADAR]</code></a> &nbsp;·&nbsp;
  <a href="#05--annual-contribution-pulse"><code>[05_PULSE]</code></a> &nbsp;·&nbsp;
  <a href="#06--priority-transmission"><code>[06_CONTACT]</code></a>
</p>

> [!NOTE]
> **Engineering Thesis**: I work where abstraction has a measurable cost — a compiler that has to beat the interpreter it replaces, firmware on an ESP32, an LLM feature that has to be worth its latency. Same instinct in all three: know what the layer below actually costs.

---

### 01 / silicon die floorplan

A heterogeneous architecture mapping across four coordinated engineering layers — from raw silicon execution memory up to stochastic model routing:

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/floorplan-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/floorplan-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/floorplan-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/floorplan-light-static.svg">
  <img src="assets/floorplan-light-static.svg" width="100%" alt="Silicon Processor Die Floorplan">
</picture>
</p>

- **Core 0 (JIT & Compilers):** Direct x86-64 machine execution via `mmap(PROT_EXEC)`, eliminating garbage collection pauses entirely and compiling recursive tail-calls from 5M frames down to zero.
- **Core 1 (Adaptive Applied AI):** Fault-tolerant cascade orchestration — Groq (Llama 3 @ 420ms) degrades gracefully to Gemini on 429 rate limits, with 50k+ grammar rules and closed-loop beam search scoring.
- **Core 2 (On-Device Vision):** Client-side MediaPipe `ImageSegmenter` in WebAssembly — 18ms inference latency with zero image bytes exfiltrated to external servers.
- **Core 3 (Edge Firmware):** Memory-bounded C++ on ESP32 sampling room electrical telemetry, with zero-secret FCM push routing through serverless edge functions.

---

### 02 / native jit disassembly & empirical proof

Claims are cheap. This is the compiler's own recursive kernel (`fib32`) disassembled directly from executable memory and benchmarked against CPython 3.14 on the same host:

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/disassembly-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/disassembly-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/disassembly-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/disassembly-light-static.svg">
  <img src="assets/disassembly-light-static.svg" width="100%" alt="Disassembly & Empirical Speedup Diff">
</picture>
</p>

| Benchmark Kernel | CPython 3.14 (Interpreted) | Black Mamba (Native JIT) | Speedup Ratio | Memory Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **`fib(32)`** | 288.62 ms | **11.08 ms** | **26.1x FASTER** | 14.2 MB → **1.1 MB** |
| **`collatz(40k)`** | 227.84 ms | **8.29 ms** | **27.5x FASTER** | 12.8 MB → **0.9 MB** |
| **`mandelbrot(120x120)`** | 39.14 ms | **3.37 ms** | **11.6x FASTER** | 18.4 MB → **1.4 MB** |
| **`count_primes(30k)`** | 22.05 ms | **1.73 ms** | **12.7x FASTER** | 11.2 MB → **0.8 MB** |

---

### 03 / modular system specifications

<details>
<summary><b>SPEC-01 // NATIVE COMPILERS & JIT RUNTIMES — Black Mamba v1.1.0</b></summary>

<br>

- **Repository:** [`kicode01/blackmamba-lang`](https://github.com/kicode01/blackmamba-lang)
- **Architecture:** Pythonic syntax, C execution semantics, zero borrow-checker runtime penalty.
- **Frontend & Inference:** Indentation desugaring AST, Hindley-Milner static type inference, dynamic C3 multiple-inheritance linearization resolving diamond hierarchies in 0.42ms.
- **Codegen & Linker:** Emits LLVM 18 IR, zero-dependency pure-Python PE32+ and ELF64 linkers, and direct x86-64 executable memory pages (`mmap(PROT_READ | PROT_WRITE | PROT_EXEC)`). Emits 1.7 KB WebAssembly modules.
- **Native Standard Library:** Structured exception stack unwinding, native TLS 1.3 cryptographic engine, relational SQL engine, and 24-bit RGB GUI framework.

`Python · x86-64 · LLVM IR · C · WebAssembly · TLS 1.3 · SQL`

</details>

<details>
<summary><b>SPEC-02 // ADAPTIVE APPLIED AI & ON-DEVICE VISION — TypenScrape & meemomini</b></summary>

<br>

- **TypenScrape ([Repo](https://github.com/kicode01/typenscrape)):** Offline-first semantic recipe generation. Cascades Groq (Llama 3 @ 420ms) to Gemini on 429 rate limits so degraded states return useful data instead of throwing errors. Bounded memory consumption via sixteen-chunk IndexedDB paging to survive mobile device RAM limits.
- **meemomini ([Repo](https://github.com/kicode01/meemomini)):** Browser photo booth PWA running on-device computer vision. Employs MediaPipe's `ImageSegmenter` compiled to WASM — background removal runs in 18ms with zero camera frames ever leaving the client machine. Local WebGL canvas filters, offline PWA caching, and client-side GIF/MP4 encoding.

`React 18 · TypeScript · MediaPipe WASM · Groq Llama 3 · Gemini · IndexedDB · PWA`

</details>

<details>
<summary><b>SPEC-03 // BOUNDED FIRMWARE & HARDWARE TELEMETRY — VoltSense</b></summary>

<br>

- **Repository:** [`kicode01/voltsense-iot`](https://github.com/kicode01/voltsense-iot) &nbsp;·&nbsp; **Live:** [voltsense-iot.vercel.app](https://voltsense-iot.vercel.app)
- **Edge Silicon:** ESP32 running memory-bounded C++ firmware measuring real-world electrical load and room occupancy.
- **Zero-Secret Architecture:** The microcontroller communicates with Vercel serverless edge functions that hold FCM push tokens — the physical hardware in the room never stores authentication secrets. Alerts propagate device → cloud function → FCM with optocoupler relay isolation.

`C++ · ESP32 · Firebase RTDB · FCM · React 19 · Vercel Functions`

</details>

<details>
<summary><b>SPEC-04 // EVALUATION LOOPS & VERIFIABLE CREDENTIALS — klyph-txt & shim-platform</b></summary>

<br>

- **klyph-txt ([Repo](https://github.com/kicode01/klyph-txt)):** Closed-loop text-engineering suite designed as a deterministic scoring beam search rather than an open-ended prompt. 9 paraphrase modes on dependency trees, 50,000+ rules via LanguageTool and SymSpell, WordNet 3.1 synonym ranking, and candidate evaluation refusing to ship outputs that fail grammar/semantic thresholds.
- **shim-platform ([Repo](https://github.com/kicode01/shim-platform) · [Live](https://shim-hq.vercel.app)):** Verifiable credential issuance platform. Every issued certificate generates an immutable cryptographic ID and public QR verification endpoint. Font bounding boxes are calculated against true font metric tables and kerning pairs rather than estimated CSS lengths, eliminating badge overflow.

`Next.js 16 · React 19 · Prisma · spaCy AST · LanguageTool · WordNet · jsPDF`

</details>

<details>
<summary><b>SPEC-05 // EXECUTIVE TRIAGE & RECRUITER DOSSIER</b></summary>

<br>

> [!TIP]
> **Hiring Manager & Engineering Director Triage**
> - **Target Roles:** Compiler / Runtime Engineer, Applied AI Systems Engineer, Embedded / Edge Systems Engineer.
> - **Vertical Reach:** From x86-64 assembly and ESP32 C++ firmware up to Groq/Gemini cascade routers and React 19 / Next.js 16 production interfaces.
> - **Empirical Verification:** Every metric shown here is verifiable through public repositories, GitHub Action runs, and commit history.
> - **Availability:** Open to global remote, international, and on-site roles.

</details>

<details>
<summary><b>SPEC-06 // LIVE REPOSITORY PULSE & GIT COMMIT LOG</b></summary>

<br>

Live commit pulse across all public repositories, automatically regenerated from the GitHub API:

<!-- pulse:start -->
```
voltsense-iot      ec3e8f7  2026-10-27  fix(demo): resolve black screen on app collapse/expand by eliminating WebGL buffer thrashing and adding context recovery
blackmamba-lang    19b23fb  2026-10-25  feat: Black Mamba v1.1.0 — Dynamic C3 OOP, Stack-Unwinding Exceptions & Native TLS 1.3 / SQL / GUI Ecosystem
typenscrape        ec8d20d  2026-10-24  Bring the repository up to the current build
meemomini          0af15f7  2026-10-24  Publish meemomini: browser photo booth PWA
klyph-txt          148b6e7  2026-10-23  chore: track logo-design-skill directly instead of embedded submodule
shim-platform      92e1bf7  2026-10-12  fix: resolve case-sensitive lookups, cookie security protocol, template coordinate guards, and UI error states
```
<!-- pulse:end -->

Recent commits to this profile repository:

<!-- log:start -->
```
24ac1f3  chore: merge remote refresh bot stats into main
80ece29  feat: hardware oscilloscope logic analyzer waveforms, executive recruiter triage matrix, and vector pipeline animation
8ee37b5  chore: refresh profile assets
797f2f8  feat: event-driven IssueOps telemetry state machine, compiler architecture pipeline HUD, and cross-repo pulse
2421bd2  Refresh the overview for the two newly published repos
```
<!-- log:end -->

</details>

---

### 04 / event-driven issueops telemetry

This profile runs an **autonomous event-driven state machine** powered entirely by GitHub Actions IssueOps. You can transmit a live handshake signal directly through GitHub without external servers or databases.

When you submit a handshake, a GitHub Action validates your transmission, appends your handle and team to `telemetry.json`, rebuilds the vector SVG radar, commits the update, and posts an acknowledgment receipt on your issue in **~15 seconds**.

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/telemetry-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/telemetry-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/telemetry-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/telemetry-light-static.svg">
  <img src="assets/telemetry-light-static.svg" width="100%" alt="Real-time IssueOps Telemetry Radar">
</picture>
</p>

<p align="center">
  <a href="https://github.com/kicode01/kicode01/issues/new?template=telemetry_ping.yml&title=%5BTELEMETRY+PING%5D+from+%40your-handle">
    <img src="https://img.shields.io/badge/⚡_TRANSMIT_TELEMETRY_HANDSHAKE-CLICK_TO_TRIGGER-amber?style=for-the-badge&logo=github&labelColor=08090b&color=ffa028" alt="Transmit Handshake">
  </a>
</p>

<!-- telemetry:start -->
| Signal | Transmitter | Organization | Domain Focus | Timestamp | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SIG-001` | **@kicode01** | Core Systems Lab | `Applied AI / Compilers` | 2026-10-28 15:15 UTC | `VERIFIED` |
| `SIG-002` | **@guest-engineer** | Compiler Engineering | `LLVM IR / Runtime Performance` | 2026-10-28 12:40 UTC | `VERIFIED` |
| `SIG-003` | **@recruiter-network** | Global Frontier AI | `Applied AI Systems & Firmware` | 2026-10-27 21:05 UTC | `VERIFIED` |
<!-- telemetry:end -->

---

### 05 / annual contribution pulse

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/bars-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/bars-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/bars-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/bars-light-static.svg">
  <img src="assets/bars-light-static.svg" width="100%" alt="Monthly contribution pulse across the last twelve months">
</picture>
</p>

<!-- signal:start -->
**290 of 383** contributions landed in October alone. Flat for months, then it isn't.
<!-- signal:end -->

Filter repositories by verified language:

[`Python`](https://github.com/kicode01?tab=repositories&q=language%3APython) 4 &nbsp;·&nbsp; [`TypeScript`](https://github.com/kicode01?tab=repositories&q=language%3ATypeScript) 4 &nbsp;·&nbsp; [`HTML`](https://github.com/kicode01?tab=repositories&q=language%3AHTML) 3 &nbsp;·&nbsp; [`CSS`](https://github.com/kicode01?tab=repositories&q=language%3ACSS) 1 &nbsp;·&nbsp; [`JavaScript`](https://github.com/kicode01?tab=repositories&q=language%3AJavaScript) 1 &nbsp;·&nbsp; [`Jupyter Notebook`](https://github.com/kicode01?tab=repositories&q=language%3AJupyter+Notebook) 1

---

### 06 / priority transmission

The fastest way in is a [prefilled ticket](https://github.com/kicode01/kicode01/issues/new?title=Hi%20Kian&body=Where%20I%20found%20you%3A%0A%0AWhat%20you%27re%20working%20on%3A%0A%0A) — it opens with context and lands directly in my checked notifications.

Portfolio: **[kicode01.github.io](https://kicode01.github.io/)**

---

<p align="center">
  <sub>
    Vector assets generated from the GitHub API by <a href="./generate.py"><code>generate.py</code></a> — hand-crafted SVG, animated via CSS, theme-aware via <code>prefers-color-scheme</code>, and accessible via <code>prefers-reduced-motion</code>. Powered by GitHub Actions IssueOps. Zero third-party stat cards, zero GIFs, zero screenshots.
  </sub>
</p>
