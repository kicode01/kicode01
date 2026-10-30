<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-hero-light-static.svg?v=sketch3" width="100%" alt="Hi, I'm Kian — Computer Engineering student building compilers, ESP32 firmware, and applied AI tools"></picture>
</p>

<p align="center">
  <a href="https://github.com/kicode01/blackmamba-lang" title="Black Mamba — Python syntax compiled to native x86-64 &amp; WASM (26.1x faster than CPython 3.14)"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-mamba-light-static.svg?v=sketch3" width="49%" alt="Black Mamba Compiler"></picture></a>&nbsp;<a href="https://voltsense-iot.vercel.app" title="VoltSense — ESP32 load &amp; occupancy monitor with isolated cloud push credentials"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-voltsense-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-voltsense-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-voltsense-light-static.svg?v=sketch3" width="49%" alt="VoltSense IoT"></picture></a>
</p>

<p align="center">
  <a href="https://github.com/kicode01/typenscrape" title="TypenScrape — Offline-first recipe generator with Groq to Gemini failover &amp; 16-chunk IndexedDB"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-typenscrape-light-static.svg?v=sketch3" width="49%" alt="TypenScrape"></picture></a>&nbsp;<a href="https://github.com/kicode01/meemomini" title="meemomini — Browser photo booth with on-device MediaPipe WASM segmentation (~18 ms/frame)"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/card-meemomini-light-static.svg?v=sketch3" width="49%" alt="meemomini"></picture></a>
</p>

<details>
<summary><b>Project notes &amp; more builds</b> <sub>(Black Mamba, VoltSense, TypenScrape, meemomini, klyph-txt, shim-platform)</sub></summary>
<br>

- **[Black Mamba](https://github.com/kicode01/blackmamba-lang)** — Python's syntax with C's execution model. Includes an indentation-sensitive lexer/parser, dynamic C3 diamond multiple inheritance (`0.42 ms`), Hindley-Milner static type inference, LLVM 18 IR tail-call collapse (`5M -> 0` frames), direct `mmap` x86-64 JIT, and zero-dependency PE32+ / ELF64 / `1.7 KB` WASM linkers, plus native TLS 1.3, SQL, and RGB GUI libraries.
- **[VoltSense](https://github.com/kicode01/voltsense-iot)** ([live app ↗](https://voltsense-iot.vercel.app)) — ESP32 electrical load & occupancy monitor in memory-bounded C++. Push credentials stay on Vercel serverless functions so the hardware flash never holds a secret key. Paired with a React 19 operator PWA.
- **[TypenScrape](https://github.com/kicode01/typenscrape)** — Offline-first recipe PWA. Routes generation to Groq (Llama 3, `~420 ms`) first and falls back to Gemini on rate limits. Streams its local catalog in 16 sequential chunks into IndexedDB to cap mobile RAM usage.
- **[meemomini](https://github.com/kicode01/meemomini)** — Browser photo booth running MediaPipe's `ImageSegmenter` in client-side WebAssembly (`~18 ms/frame`, zero server uploads) with still/GIF/MP4 export and QR handoff.
- **[klyph-txt](https://github.com/kicode01/klyph-txt)** — Text-engineering suite built around a closed-loop beam-search scorer over dependency-tree restructuring, 50,000+ LanguageTool/SymSpell rules, and WordNet 3.1 synonym ranking.
- **[shim-platform](https://github.com/kicode01/shim-platform)** ([live app ↗](https://shim-hq.vercel.app)) — Bulk verifiable event credentials with QR verification, audit logging, and real font-metric kerning layout in Next.js 16 & Prisma.

</details>

<details>
<summary><b>Speed benchmarks &amp; how the compiler works</b> <sub>(Black Mamba JIT vs. CPython 3.14)</sub></summary>
<br>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-benchmark-light-static.svg?v=sketch3" width="100%" alt="Benchmark suite comparing Black Mamba JIT against CPython 3.14"></picture>
</p>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-topology-light-static.svg?v=sketch3" width="100%" alt="Black Mamba 5-stage compilation pipeline"></picture>
</p>
</details>

<details>
<summary><b>Coding activity &amp; recent commits</b> <sub>(12-month chart &amp; live repo feed)</sub></summary>
<br>
<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-dark-static.svg?v=sketch3"><source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-light-static.svg?v=sketch3"><img src="https://raw.githubusercontent.com/kicode01/kicode01/main/assets/sys-pulse-light-static.svg?v=sketch3" width="100%" alt="12-month contribution distribution"></picture>
</p>

<!-- signal:start -->
**308 of 401** contributions landed in October alone.
<!-- signal:end -->

Filter repositories by language:
[`Python`](https://github.com/kicode01?tab=repositories&q=language%3APython) 4 &nbsp;·&nbsp; [`TypeScript`](https://github.com/kicode01?tab=repositories&q=language%3ATypeScript) 4 &nbsp;·&nbsp; [`HTML`](https://github.com/kicode01?tab=repositories&q=language%3AHTML) 3 &nbsp;·&nbsp; [`CSS`](https://github.com/kicode01?tab=repositories&q=language%3ACSS) 1 &nbsp;·&nbsp; [`JavaScript`](https://github.com/kicode01?tab=repositories&q=language%3AJavaScript) 1

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
</details>

---

<p align="center">
  <sub>
    <b>Portfolio:</b> <a href="https://kicode01.github.io/">kicode01.github.io</a> &nbsp;·&nbsp;
    <b>Say hi:</b> <a href="https://github.com/kicode01/kicode01/issues/new?title=Hi%20Kian&body=Where%20I%20found%20you%3A%0A%0AWhat%20you%27re%20working%20on%3A%0A%0A">Open a prefilled issue ↗</a> &nbsp;·&nbsp;
    <b>Visitor guestbook:</b> <a href="https://github.com/kicode01/kicode01/issues/new?template=telemetry_ping.yml&title=%5BTELEMETRY+PING%5D+from+%40your-handle">Leave a ping ↗</a>
  </sub>
</p>
