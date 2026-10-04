# ZoomThai Frontend (Rust + Leptos)

## Table of Contents
1. [Framework Selection: Why Leptos?](#framework-selection-why-leptos)
2. [The Learning Curve & Process](#the-learning-curve--process)
3. [Implementation Pain Points](#implementation-pain-points)
4. [Bundle Size](#bundle-size)
5. [Honest Reflection](#honest-reflection)
6. [Project Directory Tree](#project-directory-tree)

## Framework Selection: Why Leptos?
For this project, I chose **Leptos** over alternatives like Yew, Dioxus, or Sycamore for the following reasons:
1. **Fine-grained Reactivity:** Leptos uses a Signals-based reactivity system that updates the DOM precisely where changes occur, eliminating the need for a Virtual DOM. This results in performance closely rivaling Vanilla JavaScript.
2. **First-class Server-Side Rendering (SSR):** Although this challenge only requires Client-Side Rendering (CSR), Leptos's architecture makes it extremely straightforward to transition to a full-stack (Isomorphic) framework in the future.
3. **Familiarity with SolidJS/React:** The component-authoring model closely resembles SolidJS, making state management easier to reason about compared to other Rust UI frameworks.

**Compared to JS Frameworks (e.g., React/Vue):**
- **Pros:** Absolute type safety extending from the API client to application state, and no runtime exceptions caused by `undefined` or `null`.
- **Cons:** A significantly steeper learning curve, especially regarding Rust's lifetimes and ownership when passing closures (e.g., heavily utilizing `move ||` blocks).

## The Learning Curve & Process
Initiating frontend development with Rust was a highly rewarding challenge.
- **Initial Phase (Hours 1-2):** Adapting to the `view!` macro and Rust's strict closure ownership rules was demanding. Grasping that a Signal is a `Copy` type requiring explicit `.get()` and `.set()` calls required a mental shift from React's `useState`.
- **Intermediate Phase (Hours 3-5):** Fetching asynchronous data via `create_resource` and `create_action` became intuitive. Implementing global state management through `provide_context` and modularizing the UI into smaller components (e.g., within `ui.rs`) significantly improved code maintainability.

## Implementation Pain Points
1. **API Serialization Overhead:** The `create_resource` primitive mandates that the resulting data structures (e.g., `SearchResponse`) implement both `Serialize` and `Deserialize` traits via Serde. This initially caused opaque compiler errors until the correct derive macros were applied across all deeply nested structs.
2. **String Management:** Navigating the strict dichotomy between `&str` and `String` inside the HTML macro proved cumbersome, particularly when constructing dynamic route links (e.g., applying `urlencoding`).
3. **CSS Integration:** The `trunk` bundler lacks native integration for Tailwind's `@apply` directives within external stylesheets. To prevent bundle bloat, I resolved this by utilizing a Pure CSS approach with Design Tokens in `style.css`.

## Bundle Size
- After compiling the application in `--release` mode and applying WebAssembly optimization via the `wasm-opt -Oz` command...
- The final `.wasm` bundle size was reduced to **2.2 MB**.
- *(Note: Further reduction is possible by utilizing a custom allocator like `wee_alloc` or pruning unused dependencies such as `regex` if they are not strictly required.)*

## Honest Reflection
Although setting up a Rust frontend requires a larger initial time investment compared to React, the paradigm of **"if it compiles, it works"** is profoundly accurate. The uncompromising type system successfully caught all potential runtime errors (e.g., null API fields) during compilation. This experience provided a transformative perspective on building robust, enterprise-grade web applications.

## Project Directory Tree
```text
frontend/
├── Cargo.toml
├── Dockerfile
├── README.md
├── index.html
├── screenshots/
├── src/
│   ├── app.rs
│   ├── components/
│   │   ├── chat.rs
│   │   ├── home.rs
│   │   ├── procurement_table.rs
│   │   └── ui.rs
│   ├── config.rs
│   ├── environments/
│   ├── main.rs
│   ├── models/
│   └── services/
│       └── api.rs
└── style.css
```
