<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-light-static.svg?v=apple7" width="100%" alt="Kian — Computer Engineering · Systems &amp; Applied AI"></picture>
</p>

<p align="center">
  <a href="https://github.com/kicode01/blackmamba-lang" title="Black Mamba v2.1 — Python syntax compiled to native x86-64, WASM &amp; WebGPU (26.1x faster than CPython 3.14)"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-light-static.svg?v=apple7" width="49%" alt="Black Mamba Compiler"></picture></a>&nbsp;<a href="https://shim-hq.vercel.app" title="Shim — Cryptographic credential platform with QR verification, attendee wallets &amp; font-metric kerning"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-shim-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-shim-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-shim-light-static.svg?v=apple7" width="49%" alt="Shim Platform"></picture></a>
</p>

<p align="center">
  <a href="https://typenscrape.web.app/" title="TypenScrape — Offline-first recipe PWA with Groq to Gemini failover &amp; 16-chunk IndexedDB"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-light-static.svg?v=apple7" width="49%" alt="TypenScrape"></picture></a>&nbsp;<a href="https://meemomini.web.app/" title="meemomini — Browser photo booth with on-device MediaPipe WASM segmentation (~18 ms/frame)"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-light-static.svg?v=apple7" width="49%" alt="meemomini"></picture></a>
</p>

<details>
<summary><b>Project notes &amp; more builds</b> <sub>(Black Mamba v2.1, AI Agent Verification Suite, Shim, TypenScrape, meemomini, nanobit, toccata-os)</sub></summary>
<br>

#### Compilers & Native Runtimes
- **[Black Mamba `v2.1`](https://github.com/kicode01/blackmamba-lang)** — Python's syntax with C's execution model (`26.1×` faster than CPython 3.14). Includes an in-browser WASM compiler, Jupyter kernel, WebGPU/SPIR-V backend, `0.4 ms` serverless deploy, dynamic C3 diamond MRO (`0.42 ms`), Hindley-Milner static type inference, LLVM 18 tail-call collapse (`5M -> 0` frames), direct `mmap` x86-64 JIT, and zero-dependency PE32+ / ELF64 / `1.7 KB` WASM linkers.

#### AI Agent Tooling, Verification & Distillation
- **[llm-distiller](https://github.com/kicode01/llm-distiller)** — Cognitive-to-deterministic compiler turning repetitive LLM prompts into sub-millisecond deterministic code.
- **[agent-immune-system](https://github.com/kicode01/agent-immune-system)** — Evolutionary genetic jailbreak fuzzer and AST tool-execution firewall for autonomous AI agents.
- **[spec-weaver](https://github.com/kicode01/spec-weaver)** — Mathematical state-space model checker and formal invariant proof engine for AI agents.
- **[data-time-machine](https://github.com/kicode01/data-time-machine)** — Zero-downtime database migration and cryptographic Merkle-tree parity engine for AI agents.
- **[code-archeologist](https://github.com/kicode01/code-archeologist)** — Legacy decompilation, memory-safe WebAssembly sandboxer, and differential mutation fuzzer.
- **[code-dissolver](https://github.com/kicode01/code-dissolver)** — AST static call-graph reachability and empirical production-telemetry tree-shaker for AI agents.

#### Web Systems, On-Device Vision & GPU Graphics
- **[Shim (`shim-platform`)](https://github.com/kicode01/shim-platform)** ([live app ↗](https://shim-hq.vercel.app)) — Cryptographic credential platform with instant QR verification, drag-and-drop font-metric kerning layout, audit logging, and attendee wallets in Next.js 16 & Prisma.
- **[TypenScrape](https://github.com/kicode01/typenscrape)** ([live app ↗](https://typenscrape.web.app/)) — Offline-first recipe PWA. Routes generation to Groq (Llama 3, `~420 ms`) with automatic Gemini failover and streams its catalog in 16 sequential chunks into IndexedDB.
- **[meemomini](https://github.com/kicode01/meemomini)** ([live app ↗](https://meemomini.web.app/)) — Browser photo booth running MediaPipe's `ImageSegmenter` in client-side WebAssembly (`~18 ms/frame`, zero server uploads) with AR filters, GIF/MP4 export, and QR sharing.
- **[nanobit](https://github.com/kicode01/nanobit)** ([live app ↗](https://nanobit.vercel.app)) — Interactive 3D particle dust & optical depth gallery powered by WebGL2, GPGPU, and monocular depth AI (*Depth Anything*).
- **[toccata-os](https://github.com/kicode01/toccata-os)** ([live app ↗](https://toccataos.vercel.app)) — Browser-based operating system environment *(in active development)*.
- **[VoltSense (`voltsense-iot`)](https://github.com/kicode01/voltsense-iot)** ([live app ↗](https://voltsense-iot.vercel.app)) — ESP32 occupancy-driven electrical load monitor and cloud relay console with server-isolated push credentials.
- **[klyph-txt](https://github.com/kicode01/klyph-txt)** — Text-engineering suite built around a closed-loop beam-search scorer over dependency-tree restructuring, 50,000+ LanguageTool/SymSpell rules, and WordNet 3.1 synonym ranking.

</details>

<details>
<summary><b>Speed benchmarks &amp; how the compiler works</b> <sub>(Black Mamba v2.1 JIT vs. CPython 3.14)</sub></summary>
<br>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-light-static.svg?v=apple7" width="100%" alt="Benchmark suite comparing Black Mamba JIT against CPython 3.14"></picture>
</p>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-light-static.svg?v=apple7" width="100%" alt="Black Mamba 5-stage compilation pipeline"></picture>
</p>
</details>

<details>
<summary><b>Coding activity &amp; recent commits</b> <sub>(12-month chart &amp; live repo feed)</sub></summary>
<br>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-dark-static.svg?v=apple7"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-light-static.svg?v=apple7"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-light-static.svg?v=apple7" width="100%" alt="12-month contribution distribution"></picture>
</p>

<!-- signal:start -->
**353 of 557** contributions landed in October alone.
<!-- signal:end -->

Filter repositories by language:
<!-- langs:start -->
[`Python`](https://github.com/kicode01?tab=repositories&q=language%3APython) 10 &nbsp;·&nbsp; [`TypeScript`](https://github.com/kicode01?tab=repositories&q=language%3ATypeScript) 5 &nbsp;·&nbsp; [`HTML`](https://github.com/kicode01?tab=repositories&q=language%3AHTML) 4 &nbsp;·&nbsp; [`JavaScript`](https://github.com/kicode01?tab=repositories&q=language%3AJavaScript) 2 &nbsp;·&nbsp; [`CSS`](https://github.com/kicode01?tab=repositories&q=language%3ACSS) 1 &nbsp;·&nbsp; [`Jupyter Notebook`](https://github.com/kicode01?tab=repositories&q=language%3AJupyter%20Notebook) 1
<!-- langs:end -->

<!-- pulse:start -->
```
code-dissolver       3ca4e68  2026-11-03  feat: add automated AST stale feature flag inliner and branch pruner
code-archeologist    e09c194  2026-11-03  feat: add coverage-guided corpus evolution and seed accumulator
data-time-machine    ea07fe9  2026-11-03  feat: add adaptive replica lag rate-limiting and throughput controller
spec-weaver          61a76b3  2026-11-03  feat: add continuous invariant discovery and mining engine
agent-immune-system  eb27420  2026-11-03  feat: add automated adversarial vaccine generator and reverse-shell blocker
llm-distiller        3f2edb6  2026-11-03  feat: add continuous trace ingestion and self-training loop
toccata-os           4f39b34  2026-11-03  docs: state project status as under active development
blackmamba-lang      b97839a  2026-10-30  feat(v2.1): Pillar 0 (In-Browser WASM Compiler, Jupyter Kernel, WebGPU/SPIR-V Backend, 0.4ms Serverless Deploy) + Consumer Playground Speed Duel
```
<!-- pulse:end -->
</details>

---

<p align="center">
  <sub>
    <b>Portfolio:</b> <a href="https://kicode01.github.io/">kicode01.github.io</a> &nbsp;·&nbsp;
    <b>Say hi:</b> <a href="https://github.com/kicode01/kicode01/issues/new?title=Hi%20Kian&body=Where%20I%20found%20you%3A%0A%0AWhat%20you%27re%20working%20on%3A%0A%0A">Open a prefilled issue ↗</a> &nbsp;·&nbsp;
    <b>Visitor guestbook:</b> <a href="https://github.com/kicode01/kicode01/issues/new?template=telemetry_ping.yml&title=%5BTELEMETRY+PING%5D+from+%40your-handle">Leave a ping ↗</a>
  </sub>
</p>
