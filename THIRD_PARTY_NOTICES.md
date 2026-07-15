# Third-party notices

## Lucide

The Explorer uses the locally bundled Lucide icon library, version 1.24.0, to
render consistent SVG icons in the diagram navigation. No CDN or network call
is required at runtime. Lucide is distributed under the ISC License; a copy is
included at `licenses/LUCIDE_LICENSE.txt`.

## draw.io

The local editor runtime in `vendor/drawio/` is derived from the draw.io source
repository and is distributed under the Apache License 2.0. A copy of the
license is included at `vendor/drawio/LICENSE`.

The Explorer adds `plugins/petakerja-explorer.js` and registers that plugin in
the vendored `js/diagramly/App.js`. These changes provide same-origin selection,
focus and validation messages between the editor and PetaKerja Architecture
Explorer. They do not imply affiliation with or endorsement by draw.io.

The draw.io name and trademarks remain the property of their respective owner.

## Page Agent design patterns

The Explorer-specific Agent Mode adapts design patterns studied from the
MIT-licensed Page Agent project, including reflection before action,
activity/history events, bounded retries, cancellation and a visible simulator
cursor. Its running-only canvas status glow is conceptually based on Page
Agent's `MotionOverlay`, but is independently implemented with local CSS. The
Explorer does not bundle `ai-motion`, embed Page Agent's generic DOM-clicking
interface or permit arbitrary JavaScript execution.

Copyright (c) 2026 SimonLuvRamen
Copyright (c) 2026 Alibaba Group Holding Limited

The complete MIT licence is included at `licenses/PAGE_AGENT_LICENSE.txt`.

## drawio-ai-kit development tooling

The flow-chart regeneration workflow can use the MIT-licensed
`sparklabx/drawio-ai-kit` command-line tool for structural validation, audit
and rendering. It is a development tool and is not loaded by the Explorer at
runtime. The implementation pins release `v1.0.0` and uses only the generic
workflow and diagram-principle rules for these flow charts.

Copyright (c) 2026 sparklabx

The complete MIT licence is included at
`licenses/DRAWIO_AI_KIT_LICENSE.txt`.
