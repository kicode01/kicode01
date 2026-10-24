<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/boot-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/boot-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/boot-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/boot-light-static.svg">
  <img src="assets/boot-light-static.svg" width="100%" alt="Kian — Computer Engineering student. I write compilers and firmware, then put models on top of them.">
</picture>
</p>

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/ticker-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/ticker-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/ticker-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/ticker-light-static.svg">
  <img src="assets/ticker-light-static.svg" width="100%" alt="Technologies: Python, C, C++, x86-64, LLVM IR, WebAssembly, TypeScript, React, Next.js, Vite, Tailwind, LLM, Firebase, ESP32, OpenSCAD, spaCy, Shopify API, Node, Git.">
</picture>
</p>

<sub>**Aiming at** applied AI &nbsp;·&nbsp; **Building** Black Mamba &nbsp;·&nbsp; **Open to** applied AI roles &nbsp;·&nbsp; **[Start here ↓](#01--console)**</sub>

I'm a Computer Engineering student. I work where abstraction has a measurable cost — a compiler that has to beat the interpreter it replaces, firmware on an ESP32, an LLM feature that has to be worth its latency. Same instinct in all three: know what the layer below actually costs.

---

## 01 / console

This section is a working console. Each line below is a native `<details>` element, so it opens on click — no JavaScript, no image of a terminal, no third-party widget. GitHub renders it, your browser does the rest.

<details>
<summary><code>kian@github:~$ whoami</code></summary>

<br>

Computer Engineering student, heading toward **applied AI** — building products on top of models rather than training them. I came at it from below: compilers, firmware, the layers where you can measure what a decision costs.

Currently building **[Black Mamba](https://github.com/kicode01/blackmamba-lang)**, a language with Python's syntax and C's execution model.

</details>

<details>
<summary><code>kian@github:~$ cat ai.md</code></summary>

<br>

```
direction   applied ai — systems underneath, models on top
method      core logic is mine · scaffolding is ai-assisted · all of it reviewed
evidence    klyph-txt — generate, score, select
not yet     model training and fine-tuning
```

There's a longer version [below](#02--ai).

</details>

<details>
<summary><code>kian@github:~$ ls projects/</code></summary>

<br>

```
drwxr-xr-x  blackmamba-lang/            compiler · python · llvm · wasm
drwxr-xr-x  klyph-txt/                  nlp · llm rewriter · candidate scoring
drwxr-xr-x  voltsense-iot/              esp32 firmware · react pwa · firebase
drwxr-xr-x  aurakeys-storefront/        next.js 15 · three.js · shopify api
drwxr-xr-x  servyfy-platform/           react 19 · firebase · offline-first
drwxr-xr-x  oppa-k-ramyeon-hub/         php · html · shipped and live
drwxr-xr-x  employee-attendance-viewer/ pyside6 · desktop · mit
```

Three of them are worth your time. They're below.

</details>

<details>
<summary><code>kian@github:~$ cat stack.txt</code></summary>

<br>

**AI** — LLM integration · candidate generation + scoring · spaCy · NLTK · LanguageTool · WordNet<br>
**Systems** — Python · C · C++ · x86-64 · WebAssembly · LLVM IR<br>
**Web** — TypeScript · React 19 · Next.js 15 · Vite · Tailwind · Node<br>
**Data & cloud** — Firebase (RTDB, FCM) · Vercel · Dexie · Shopify Storefront API<br>
**Hardware** — ESP32 · OpenSCAD · firmware in C++

</details>

<details>
<summary><code>kian@github:~$ git log --oneline -5</code></summary>

<br>

The actual log of the repository you're reading. The page regenerates it, so it can't go stale.

<!-- log:start -->
```
d25616a  Rebuild the profile as an instrument panel with a working console
16e4a8f  Make the profile animate itself
0c68510  Require a user-scoped token for the refresh job
981596d  chore: refresh profile assets
3c8f2d2  CI: stage README.md and rebase before pushing
```
<!-- log:end -->

</details>

<details>
<summary><code>kian@github:~$ open contact</code></summary>

<br>

| | |
| :-- | :-- |
| **Portfolio** | [kicode01.github.io](https://kicode01.github.io/) |
| **Start a conversation** | [Open a ticket](https://github.com/kicode01/kicode01/issues/new?title=Hi%20Kian&body=Where%20I%20found%20you%3A%0A%0AWhat%20you%27re%20working%20on%3A%0A%0A) — this opens a prefilled issue, not a mail client |

</details>

---

## 02 / ai

I'm aiming at **applied AI**: products built on top of models, not models built from scratch. The case for hiring me isn't a list of frameworks — it's that I can work a level below the API. I've written a compiler and firmware, so token budgets, latency, and verification aren't things I've only read about.

**How I work.** The core logic and the architecture are mine. Scaffolding — UI, boilerplate, glue — is largely AI-generated, and I read it before it ships. I use AI the way I use a compiler: much faster than me at the mechanical part, and wrong often enough that you check the output.

**What that looks like in code.** [`klyph-txt`](https://github.com/kicode01/klyph-txt) is a generate-score-select loop. It produces structural candidates, scores each against a rubric, and keeps the lowest-risk one. The model is a single component inside a deterministic pipeline, not the pipeline itself — which is the shape most applied-AI systems end up needing once the demo is over.

**What I'm not claiming.** I haven't trained or fine-tuned a model, and I'm not going to imply otherwise. If the role is model architecture or distributed training, I'm not the hire yet. If it's shipping LLM features that survive contact with real users — retrieval, evaluation, cost, failure modes — that's the work I want, and the systems background is exactly why I'd be useful at it.

---

## 03 / builds

<sub>`M-01` &nbsp;·&nbsp; COMPILER &nbsp;·&nbsp; SYSTEMS &nbsp;·&nbsp; MIT</sub>

#### [Black Mamba](https://github.com/kicode01/blackmamba-lang)

Python's syntax, C's execution model, no borrow checker in between. A lexer and parser, an x86-64 JIT that allocates executable memory directly, zero-dependency PE32+ and ELF64 linkers in pure Python, and a WebAssembly backend that emits 1.7 KB modules. Automatic tail-call optimization collapses 5,000,000 recursive frames into zero stack frames.

`Python · x86-64 · LLVM IR · C · WebAssembly`

<sub>`M-02` &nbsp;·&nbsp; NLP &nbsp;·&nbsp; LLM &nbsp;·&nbsp; EVALUATION</sub>

#### [klyph-txt](https://github.com/kicode01/klyph-txt)

A text-engineering suite built as a scoring loop rather than a prompt. Nine paraphrase modes on dependency-tree restructuring, 50,000+ grammar rules via LanguageTool and SymSpell, WordNet 3.1 synonym ranking, an optional LLM rewrite pass — and a closed-loop beam search that scores every candidate before choosing one. The interesting part isn't the model; it's that every output is measurable and the system refuses to ship one it can't score.

`Python · spaCy · AST · LanguageTool · WordNet · LLM`

<sub>`M-03` &nbsp;·&nbsp; FIRMWARE &nbsp;·&nbsp; SERVERLESS &nbsp;·&nbsp; PWA</sub>

#### [VoltSense](https://github.com/kicode01/voltsense-iot)

An ESP32 measures a room's real electrical load and occupancy, publishes telemetry to Firebase, and exposes per-port relay control. Three deliberately separate layers: C++ firmware, Vercel functions that hold the push credentials so the device never has to, and a React 19 PWA an operator would actually use. Alerts travel device → server → FCM without the device ever holding a messaging key.

`C++ · ESP32 · Firebase RTDB · FCM · React 19 · Vercel` &nbsp;—&nbsp; **[live ↗](https://voltsense-iot.vercel.app)**

---

## 04 / evidence

Claims are cheap. This is the compiler's own benchmark suite, run against CPython 3.14 — same kernels, same machine.

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/bench-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/bench-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/bench-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/bench-light-static.svg">
  <img src="assets/bench-light-static.svg" width="100%" alt="Benchmark: Black Mamba versus CPython 3.14. fib(32) 288.62ms vs 11.078ms, 26.1x faster. collatz 227.84ms vs 8.291ms, 27.5x. mandelbrot 39.14ms vs 3.368ms, 11.6x. count_primes 22.05ms vs 1.73ms, 12.7x.">
</picture>
</p>

The tail-call kernel is left out on purpose: CPython raises `RecursionError` on it, so there is no ratio to draw.

---

## 05 / signal

<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: no-preference)" srcset="assets/bars-dark-anim.svg">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: no-preference)" srcset="assets/bars-light-anim.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/bars-dark-static.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/bars-light-static.svg">
  <img src="assets/bars-light-static.svg" width="100%" alt="Monthly contribution bars for the last twelve months: flat through mid-year, then rising sharply into October.">
</picture>
</p>

<!-- signal:start -->
**131 of 229** contributions landed in October alone. Flat for months, then it isn't.
<!-- signal:end -->

I'd rather show the shape of the year than a streak counter.

---

## 06 / stack

Each chip filters my repositories by language — GitHub's own `?q=` filter, nothing custom.

[`Python`](https://github.com/kicode01?tab=repositories&q=language%3APython) 4 &nbsp;·&nbsp; [`TypeScript`](https://github.com/kicode01?tab=repositories&q=language%3ATypeScript) 4 &nbsp;·&nbsp; [`HTML`](https://github.com/kicode01?tab=repositories&q=language%3AHTML) 3 &nbsp;·&nbsp; [`CSS`](https://github.com/kicode01?tab=repositories&q=language%3ACSS) 1 &nbsp;·&nbsp; [`JavaScript`](https://github.com/kicode01?tab=repositories&q=language%3AJavaScript) 1 &nbsp;·&nbsp; [`Jupyter Notebook`](https://github.com/kicode01?tab=repositories&q=language%3AJupyter+Notebook) 1

---

## 07 / contact

The fastest way in is a [prefilled issue](https://github.com/kicode01/kicode01/issues/new?title=Hi%20Kian&body=Where%20I%20found%20you%3A%0A%0AWhat%20you%27re%20working%20on%3A%0A%0A) — it opens with the fields already started, and it lands somewhere I actually check.

Portfolio: **[kicode01.github.io](https://kicode01.github.io/)**

---

<p align="center">
  <sub>
    Every asset here is generated from the GitHub API by <a href="./generate.py"><code>generate.py</code></a> — hand-built SVG, animated with CSS, theme-aware, and static for anyone who asks for reduced motion. No stat-card services, no GIFs, no screenshots.
  </sub>
</p>
