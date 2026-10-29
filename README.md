<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-light-static.svg">
  <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-light-static.svg" width="100%" alt="Kian — Computer Engineering. Systems, Compilers & Applied AI.">
</picture>
</p>

<sub>**Focus:** Compilers, firmware & applied AI &nbsp;·&nbsp; **Portfolio:** [kicode01.github.io](https://kicode01.github.io/) &nbsp;·&nbsp; **Contact:** [Open a prefilled issue](https://github.com/kicode01/kicode01/issues/new?title=Hi%20Kian&body=Where%20I%20found%20you%3A%0A%0AWhat%20you%27re%20working%20on%3A%0A%0A)</sub>

---

<table width="100%">
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/kicode01/blackmamba-lang" title="Black Mamba v1.1.0 — Python syntax compiled to x86-64 machine code &amp; 1.7 KB WASM (26.1x faster than CPython 3.14). Click to open repository.">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-dark-static.svg">
          <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-light-static.svg">
          <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-light-static.svg" width="100%" alt="M-01 Black Mamba Compiler">
        </picture>
      </a>
      <details>
        <summary><code>Inspect M-01 — compiler internals &amp; benchmarks</code></summary>
        <br>
        <sub><b>Architecture:</b> Indentation-sensitive lexer/parser, dynamic C3 diamond multiple inheritance (0.42 ms linearization), Hindley-Milner static type propagation, LLVM 18 IR emitter with tail-call collapse (5M frames to 0), direct <code>mmap</code> x86-64 JIT, and zero-dependency PE32+ / ELF64 / 1.7 KB WASM linkers.</sub><br><br>
        <sub><b>Standard Library:</b> Pure-native TLS 1.3, relational SQL engine, and 24-bit RGB GUI.</sub><br><br>
        <sub><a href="https://github.com/kicode01/blackmamba-lang">Repository ↗</a></sub>
      </details>
    </td>
    <td width="50%" valign="top">
      <a href="https://voltsense-iot.vercel.app" title="VoltSense IoT — ESP32 load &amp; occupancy telemetry with air-gapped push credentials. Click to open live operator console.">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-voltsense-dark-static.svg">
          <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-voltsense-light-static.svg">
          <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-voltsense-light-static.svg" width="100%" alt="M-02 VoltSense IoT">
        </picture>
      </a>
      <details>
        <summary><code>Inspect M-02 — firmware isolation &amp; live deployment</code></summary>
        <br>
        <sub><b>Architecture:</b> Three separated layers — memory-bounded C++ on an ESP32 sampling real electrical load and occupancy, Vercel serverless functions that hold Firebase Cloud Messaging credentials so the hardware flash never contains a secret key, and a React 19 operator PWA with per-port relay switching.</sub><br><br>
        <sub><a href="https://voltsense-iot.vercel.app">Live Operator PWA ↗</a> &nbsp;·&nbsp; <a href="https://github.com/kicode01/voltsense-iot">Repository ↗</a></sub>
      </details>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="https://github.com/kicode01/typenscrape" title="TypenScrape — Offline-first recipe engine with Groq (Llama 3) to Gemini failover and 16-chunk IndexedDB streaming. Click to open repository.">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-dark-static.svg">
          <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-light-static.svg">
          <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-light-static.svg" width="100%" alt="M-03 TypenScrape">
        </picture>
      </a>
      <details>
        <summary><code>Inspect M-03 — failover routing &amp; memory bounds</code></summary>
        <br>
        <sub><b>Architecture:</b> Queries route to Groq (Llama 3, ~420 ms) first and fail over automatically to Gemini on HTTP 429 rate limits. The offline catalog is split into 16 sequential chunks streamed one at a time into IndexedDB so mobile browsers never spike peak heap memory.</sub><br><br>
        <sub><a href="https://github.com/kicode01/typenscrape">Repository ↗</a></sub>
      </details>
    </td>
    <td width="50%" valign="top">
      <a href="https://github.com/kicode01/meemomini" title="meemomini — Browser photo booth running MediaPipe ImageSegmenter in WebAssembly (~18 ms per frame, zero server uploads). Click to open repository.">
        <picture>
          <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-dark-static.svg">
          <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-light-static.svg">
          <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-light-static.svg" width="100%" alt="M-04 meemomini">
        </picture>
      </a>
      <details>
        <summary><code>Inspect M-04 — on-device WASM vision pipeline</code></summary>
        <br>
        <sub><b>Architecture:</b> MediaPipe's <code>ImageSegmenter</code> runs entirely in client-side WebAssembly (~18 ms/frame). No camera frame ever leaves the device. Includes WebGL compositing, export to still/GIF/MP4, and local QR handoff as an installable PWA.</sub><br><br>
        <sub><a href="https://github.com/kicode01/meemomini">Repository ↗</a></sub>
      </details>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <details>
        <summary><code>M-05 / klyph-txt</code> — closed-loop NLP &amp; beam-search scoring</summary>
        <br>
        <sub>Nine paraphrase modes built on dependency-tree restructuring, 50,000+ grammar rules via LanguageTool and SymSpell, WordNet 3.1 synonym ranking, and a closed-loop beam search that scores every candidate before emitting output.</sub><br><br>
        <sub><code>Python · spaCy · AST · LanguageTool · WordNet · LLM</code> &nbsp;·&nbsp; <a href="https://github.com/kicode01/klyph-txt">Repository ↗</a></sub>
      </details>
    </td>
    <td width="50%" valign="top">
      <details>
        <summary><code>M-06 / shim-platform</code> — verifiable credentials &amp; font-metric layout</summary>
        <br>
        <sub>Bulk event credential issuance where every certificate carries a unique ID and QR code resolving to a public verification endpoint with audit logging. Template text is fitted against real font kerning tables rather than estimated.</sub><br><br>
        <sub><code>Next.js 16 · React 19 · Prisma · jsPDF · QR</code> &nbsp;·&nbsp; <a href="https://shim-hq.vercel.app">Live ↗</a> &nbsp;·&nbsp; <a href="https://github.com/kicode01/shim-platform">Repository ↗</a></sub>
      </details>
    </td>
  </tr>
</table>

---

### Interactive Specification Plates

<sub>Click any plate below to unfold its full-width schematic, benchmark data, or live repository feed.</sub>

<details open>
<summary><code>01 / benchmark suite</code> — Black Mamba JIT vs. CPython 3.14 (empirical kernel timings)</summary>
<br>
<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-light-static.svg">
  <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-light-static.svg" width="100%" alt="Benchmark suite comparing Black Mamba JIT against CPython 3.14">
</picture>
</p>
<sub>The tail-call recursion kernel (5,000,000 frames) is omitted from the ratio chart because CPython raises <code>RecursionError</code> on it, while Black Mamba collapses it into a single stack frame.</sub>
</details>

<details>
<summary><code>02 / compiler pipeline</code> — 5-stage AST, C3 MRO, Hindley-Milner &amp; LLVM 18 schematic</summary>
<br>
<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-light-static.svg">
  <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-light-static.svg" width="100%" alt="Black Mamba 5-stage compilation pipeline">
</picture>
</p>
</details>

<details>
<summary><code>03 / contribution cadence</code> — 12-month distribution &amp; repository language filter</summary>
<br>
<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-light-static.svg">
  <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-light-static.svg" width="100%" alt="12-month contribution distribution">
</picture>
</p>

<!-- signal:start -->
**306 of 399** contributions landed in October alone. Flat for months, then it isn't.
<!-- signal:end -->

Filter public repositories by language:
[`Python`](https://github.com/kicode01?tab=repositories&q=language%3APython "Filter repositories by Python") 4 &nbsp;·&nbsp; [`TypeScript`](https://github.com/kicode01?tab=repositories&q=language%3ATypeScript "Filter repositories by TypeScript") 4 &nbsp;·&nbsp; [`HTML`](https://github.com/kicode01?tab=repositories&q=language%3AHTML "Filter repositories by HTML") 3 &nbsp;·&nbsp; [`CSS`](https://github.com/kicode01?tab=repositories&q=language%3ACSS "Filter repositories by CSS") 1 &nbsp;·&nbsp; [`JavaScript`](https://github.com/kicode01?tab=repositories&q=language%3AJavaScript "Filter repositories by JavaScript") 1
</details>

<details>
<summary><code>04 / git log --ecosystem</code> — live commit feed across public repositories</summary>
<br>

<!-- pulse:start -->
```
blackmamba-lang    fc780cd  2026-10-29  feat(v1.3.0): full Python syntactic parity & ergonomics (context managers, comprehensions, dunder operators, match guards)
voltsense-iot      ec3e8f7  2026-10-27  fix(demo): resolve black screen on app collapse/expand by eliminating WebGL buffer thrashing and adding context recovery
typenscrape        ec8d20d  2026-10-24  Bring the repository up to the current build
meemomini          0af15f7  2026-10-24  Publish meemomini: browser photo booth PWA
klyph-txt          148b6e7  2026-10-23  chore: track logo-design-skill directly instead of embedded submodule
shim-platform      92e1bf7  2026-10-12  fix: resolve case-sensitive lookups, cookie security protocol, template coordinate guards, and UI error states
```
<!-- pulse:end -->

Recent commits to this profile repository:

<!-- log:start -->
```
28751f1  refactor: static architectural specification plates with interactive inspectors
a4a5943  chore: refresh profile assets
0179b87  feat: Next-Gen Apple-Precision Bento Console (Kinetic SVG Cards, Gyroscopic Reactor, 0 Text Clutter)
9d0e522  chore: refresh profile assets
59adb5e  feat: Interactive Visual Console layout (zero text clutter, interactive modules, personal cybernetic crest)
```
<!-- log:end -->
</details>

<details>
<summary><code>05 / issueops handshake</code> — event-driven GitHub Actions visitor log</summary>
<br>
<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-signal-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-signal-light-static.svg">
  <img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-signal-light-static.svg" width="100%" alt="Verified IssueOps telemetry log">
</picture>
</p>

<!-- telemetry:start -->
| Signal | Sender | Organization | Focus | Timestamp |
| :--- | :--- | :--- | :--- | :--- |
| `SIG-001` | **@kicode01** | Core Systems Lab | `Applied AI / Compilers` | 2026-10-28 15:15 UTC |
| `SIG-002` | **@guest-engineer** | Compiler Engineering | `LLVM IR / Runtime Performance` | 2026-10-28 12:40 UTC |
| `SIG-003` | **@recruiter-network** | Global Frontier AI | `Applied AI Systems & Firmware` | 2026-10-27 21:05 UTC |
<!-- telemetry:end -->

<sub>Want to test the state machine? <a href="https://github.com/kicode01/kicode01/issues/new?template=telemetry_ping.yml&title=%5BTELEMETRY+PING%5D+from+%40your-handle">Submit a handshake issue ↗</a> — a GitHub Action validates it, updates <code>telemetry.json</code>, regenerates the SVG plate above, and closes the issue in ~15 seconds.</sub>
</details>

---

<p align="center">
  <sub>
    All specification plates are static SVG generated from the GitHub API by <a href="./generate.py"><code>generate.py</code></a> — no third-party stat cards, no animations, and full dark/light theme support via <code>&lt;picture&gt;</code>.
  </sub>
</p>
