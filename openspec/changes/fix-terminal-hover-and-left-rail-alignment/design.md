## Context

The current native terminal workspace is already structurally correct: the desktop viewport is fixed, the left watchlist rail, center chart console, and right microstructure rail are all in place, and the page builds successfully through Reflex export. The remaining defects are not architecture-level layout gaps but interaction and readability gaps inside that terminal shell.

The first gap is chart inspection. The main chart and lower studies are rendered as static SVG strings inserted through `rx.html(...)`, which means users can see the latest legend values but cannot inspect a historical candle or indicator point by hovering. For a financial terminal workflow, this is a significant usability defect because users expect cursor-following price, overlay, and study readouts when scanning chart structure.

The second gap is dense side-rail readability. The left watchlist rows and the lower-left snapshot area are narrow, tightly packed modules. Their current typography and row layout allow clipping, visual drift, and incomplete labels under dense content. This weakens the terminal feel because Bloomberg-style rails depend on strict alignment, predictable truncation, and stable baselines.

## Goals / Non-Goals

**Goals:**
- Add a native hover-detail model for the center chart console so users can inspect the active candle and linked study values without leaving the terminal workspace.
- Keep hover detail synchronized between the primary chart and lower study strip so one cursor position drives one coherent data readout.
- Preserve the fixed desktop terminal posture while introducing the hover surface.
- Remove clipping and alignment defects in the left watchlist, movers, and snapshot modules.
- Define explicit truncation, line-height, and baseline rules for dense left-rail text.
- Add regression coverage for both the new hover-detail contract and the left-rail density contract.

**Non-Goals:**
- Replacing the mock market model with live market data.
- Rebuilding the chart console with an external charting library.
- Adding drag-to-zoom, crosshair trading tools, or order-entry interactions.
- Redesigning the overall information architecture of the terminal page.
- Expanding this fix into unrelated right-rail or top-bar visual refinements.

## Decisions

### Decision: Keep the current SVG-based chart rendering and add a lightweight hover overlay layer
The implementation should preserve the current Python-generated SVG approach for the primary chart and study panes. Instead of replacing the chart with a new external library, add a lightweight hover overlay layer that maps pointer position to a candle or study index and renders a terminal-style detail box inside the chart stage.

Rationale:
- The current SVG renderer already supports overlays, route-aware studies, and export-safe static generation.
- Replacing it with another rendering stack would expand scope far beyond a fix change.
- A hover overlay can be added incrementally by exposing chart point metadata, a cursor index, and a positioned detail surface.

Alternatives considered:
- Replace the whole chart with a JS charting library: rejected because it is too broad for a defect-focused fix.
- Keep the chart static and only update the top legend on hover: rejected because it does not satisfy the user's request for a data block that follows the chart unit.

### Decision: Use one shared hover state for the main chart and lower studies
The chart console should expose one active hover index and one shared hover payload so the main chart and the lower study strip always describe the same bar position.

Rationale:
- Financial users read the price pane and lower indicators together.
- A shared hover index prevents the main chart and studies from drifting into separate interaction states.
- This keeps the hover behavior understandable and testable.

Alternatives considered:
- Independent hover states per study pane: rejected because it fragments the chart-reading workflow.
- Tooltip logic entirely inside raw HTML/JS with no state contract: rejected because it is harder to verify and maintain in the Reflex page model.

### Decision: Add explicit chart metadata builders instead of scraping values from SVG markup
The chart layer should provide structured hover metadata per candle and per route study point, generated alongside the SVG rather than derived from DOM inspection.

Rationale:
- Structured data is easier to test than parsing SVG output.
- It separates rendering concerns from interaction concerns.
- It gives the page a stable contract for hover cards, crosshair labels, and future chart inspection extensions.

Alternatives considered:
- Parse SVG node attributes in the browser: rejected because it is brittle and tightly coupled to markup format.

### Decision: Fix left-rail text by tightening row layout contracts, not by enlarging the rail width first
The left rail should remain visually dense. The first fix should be row-level alignment, overflow, and truncation discipline: stable row heights, explicit min-width rules, ellipsis or clipping policy for secondary labels, and corrected line-height/padding.

Rationale:
- The current issue is a text-fit bug, not an information-architecture bug.
- Widening the rail first would change desktop balance and could reduce center chart space unnecessarily.
- Stable line-height and truncation are core terminal-density requirements anyway.

Alternatives considered:
- Increase left rail width globally: possible fallback, but not the preferred first move.
- Reduce font size across the rail: rejected because it can hurt readability and does not solve baseline drift by itself.

## Risks / Trade-offs

- [Risk] Pointer-to-index mapping may feel imprecise at the chart edges. ? Mitigation: clamp hover indices, define a stable nearest-bar mapping, and add tests for first/middle/last bar behavior.
- [Risk] Hover overlay logic may become split between Reflex state and inline browser behavior. ? Mitigation: keep one explicit hover contract and minimize raw imperative code to pointer capture and local overlay updates.
- [Risk] Dense left-rail truncation could hide useful secondary labels. ? Mitigation: preserve the primary code field in full where possible and apply truncation first to secondary metadata.
- [Risk] Additional hover surfaces could visually clutter the chart. ? Mitigation: use one compact terminal detail box and one thin crosshair treatment rather than multiple floating cards.
- [Risk] Mock-data hover behavior may diverge from future live data wiring. ? Mitigation: define hover metadata in a data-driven shape that can later be populated from live bar payloads without changing the UI contract.
