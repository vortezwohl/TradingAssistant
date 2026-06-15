## Why

The native terminal workspace now matches the Bloomberg-style layout and module density target, but two critical usability gaps remain: the chart console does not expose hover-following data detail for candles and studies, and the left rail still shows clipped or misaligned watchlist and snapshot text in dense rows. Both issues directly reduce scanability for financial users and make the terminal feel unfinished even though the overall page architecture is already in place.

## What Changes

- Add an explicit chart hover-detail interaction model so the primary chart and lower study panes can show cursor-following value detail for the active candle or study point without leaving the fixed terminal workspace.
- Add a synchronized hover status surface that follows the chart interaction context and updates both price-pane data and lower-study data together.
- Tighten left-rail text layout rules for watchlist, movers, and snapshot modules so symbol rows, secondary labels, and bottom-left summary cells no longer render with clipping, vertical drift, or incomplete text.
- Clarify the density and alignment rules for terminal typography so compact financial labels remain readable inside narrow side rails.

## Capabilities

### New Capabilities
- `terminal-chart-hover-details`: defines hover-following chart and study detail behavior inside the terminal chart console
- `terminal-left-rail-density-fixes`: defines dense side-rail text fitting, alignment, and truncation behavior for watchlist and snapshot modules

### Modified Capabilities
- `trading-workspace-ui`: extend the terminal workspace requirements so chart inspection includes hover detail surfaces and dense left-rail modules preserve readable alignment under terminal constraints

## Impact

- Primarily affects `tradingassistant/frontend/app.py`, `tradingassistant/frontend/charting.py`, `tradingassistant/frontend/state.py`, and `tradingassistant/frontend/theme.py` because the chart stage needs hover state wiring and the left rail needs layout token adjustments.
- Will likely require a lightweight event/overlay layer for SVG-based chart rendering or a small native chart-hover abstraction if the current static SVG path approach is kept.
- Requires new OpenSpec specs for hover detail behavior and left-rail density/alignment behavior, plus a delta spec for `trading-workspace-ui`.
- Should add or extend frontend verification coverage so hover detail containers and left-rail text-fit rules are protected by regression tests.
