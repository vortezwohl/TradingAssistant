## Context

The current redesign proposal moved the page toward a fixed-viewport market board, but it is still too close to a modern SaaS dashboard: large radii, soft cards, decorative gradients, and summary-first composition. The user has now raised the bar and wants a more traditional Wall Street terminal feel, closer to Bloomberg in posture rather than to a marketing-grade exchange landing page.

That changes more than cosmetics. The page can no longer be modeled as a chart plus supporting cards. It needs to behave like a terminal workspace with a primary chart console, secondary technical-analysis routes, and dedicated market microstructure surfaces. The static HTML reference also needs to be fully English to avoid further encoding risk and to match the tone of a global financial workstation.

## Goals / Non-Goals

**Goals:**

- Replace the current soft glass visual direction with a hard-edge, terminal-style financial workspace.
- Make the desktop layout feel like a professional market workstation rather than a consumer dashboard.
- Support main-chart overlays for indicators that belong on the price pane, including moving averages, EMA, Bollinger Bands, and VWAP.
- Support route switching for technical studies that need their own dedicated analysis pane, such as MACD, RSI, KDJ, ATR, OBV, and ADX.
- Add explicit market depth, order book, and recent prints areas as first-class modules.
- Keep the desktop workspace fixed to the viewport with only local scrolling containers.
- Produce an English static HTML reference that can be implemented later in Reflex with minimal ambiguity.

**Non-Goals:**

- This redesign does not yet implement a live trading ticket, order submission flow, or broker-side execution UX.
- This redesign does not require a one-to-one copy of Bloomberg terminal screens; it only adopts their hard-edge density, hierarchy, and tone.
- This redesign does not modify backend chart transport protocols or market data semantics.
- This redesign does not require every technical indicator to be rendered simultaneously; routing and grouping are part of the solution.

## Decisions

### 1. Move from board layout to terminal layout

**Decision**

The desktop page will use a terminal-style structure with a thin header bar, a left market navigator, a center chart console, a right market microstructure rail, and a lower analysis route strip.

**Rationale**

- A terminal layout makes it easier to express chart reading, route switching, and depth inspection as parallel tasks.
- It removes the visual softness of the current banner-plus-card composition.
- It creates a more credible financial-workstation posture for the target audience.

**Alternatives considered**

- Option A: keep the current three-panel board and only restyle it.
  - Rejected because the current composition is still summary-card centric and does not naturally fit depth / order book / route switching.
- Option B: create a fully tabbed single-pane layout.
  - Rejected because it hides too much context and weakens the workstation feel.

### 2. Adopt hard-edge Bloomberg-inspired visual language

**Decision**

The UI will use flat dark surfaces, minimal radius, dense separators, tight typography, restrained highlight colors, and almost no glass, blur, or ornamental gradients.

**Rationale**

- This is the clearest way to shift the page from consumer UI toward professional terminal UI.
- Hard surfaces and dense dividers improve scanability in data-heavy layouts.
- The user explicitly rejected rounded glass styling and asked for a more traditional financial-terminal tone.

**Alternatives considered**

- Option A: keep blur and gradients but reduce them.
  - Rejected because that still leaves the core SaaS aesthetic intact.

### 3. Split technical analysis into overlays and routes

**Decision**

Indicators that belong on the price pane will be treated as overlays on the main chart, while indicators that need dedicated reading space will be placed behind route switches in a secondary analysis console.

**Rationale**

- This prevents the main chart from becoming unreadable.
- It provides a clean way to expand indicator coverage without growing the default viewport height.
- It matches how real terminals separate overlay studies from lower-panel oscillator and momentum studies.

**Alternatives considered**

- Option A: show all indicators at once below the chart.
  - Rejected because it increases visual clutter and height pressure.
- Option B: put every indicator into a side drawer.
  - Rejected because it buries analysis too deeply for active watch usage.

### 4. Treat market depth and order book as core workspace modules

**Decision**

Market depth, order book, and recent prints will be explicit terminal modules in the right rail rather than optional summary cards or hidden diagnostics.

**Rationale**

- These are core reading surfaces for active market users.
- Their structure is fundamentally different from narrative summaries and should be designed as data ladders and tables.
- Treating them as first-class modules keeps the workspace aligned with serious trading-terminal expectations.

**Alternatives considered**

- Option A: keep the right rail as a summary / news column only.
  - Rejected because it ignores the user's request for depth and order book support.

### 5. Rewrite the static reference entirely in English

**Decision**

The HTML reference will be rewritten fully in English, including labels, panel titles, helper text, routes, and market copy.

**Rationale**

- The current file already contains damaged Chinese text, so patching it is lower quality than replacing it.
- English better matches the requested Wall Street tone.
- It eliminates a recurring encoding failure path for this static design artifact.

**Alternatives considered**

- Option A: repair the Chinese text and keep the same language.
  - Rejected because the user explicitly asked to switch to English.

## Risks / Trade-offs

- [Higher information density can become visually harsh] → Use disciplined alignment, spacing, and color semantics instead of decorative relief.
- [Depth and order book panels can compete with the chart] → Keep the chart console central and constrain microstructure modules to a stable right rail.
- [Too many indicators can overwhelm the workspace] → Separate overlays from route-based secondary studies and provide explicit route grouping.
- [Static HTML may still under-specify final chart interactions] → Encode panel roles, route names, and module responsibilities clearly in the static reference and OpenSpec docs.

## Migration Plan

1. Rewrite the proposal and specs so the implementation target is a terminal workspace instead of a soft board.
2. Rewrite the static HTML reference in English with hard-edge terminal styling.
3. Define the overlay indicators and analysis routes that the center chart console must support.
4. Define the market depth, order book, and time-and-sales panels in the right rail.
5. Use the rewritten static reference as the contract for the later Reflex implementation.

## Open Questions

- Should the right rail default to a split `Depth + Order Book` view, or should one of them be tabbed with `Time & Sales`?
- Should the lower analysis console be a horizontal route strip or a full-width tabbed pane with multiple stacked studies?
- Do we want a dedicated `Compare` route for relative performance charts later, or keep the first version focused on single-symbol study routes?