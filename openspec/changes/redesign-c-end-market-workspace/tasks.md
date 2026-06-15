## 1. Terminal Reference Scope

- [x] 1.1 Lock the terminal workspace information architecture to the current static reference: top market bar, left watchlist rail, center chart console, right microstructure rail, and lower study strip
- [x] 1.2 Lock the English naming contract for all terminal modules, controls, and panel titles used in the static reference
- [x] 1.3 Record the desktop fixed-viewport rule and local-scroll-only rule as the baseline implementation constraint for all later frontend work

## 2. Static HTML Module Breakdown

- [x] 2.1 Top terminal bar
- [x] 2.1.1 Finalize the product lockup, live status marker, macro strip, and compact quote strip content
- [x] 2.1.2 Finalize the visual density, typography, and separator treatment for the top bar so it reads like a market terminal instead of a SaaS masthead
- [x] 2.2 Left navigator rail
- [x] 2.2.1 Finalize the watchlist panel with code-only add flow, sort toggle, active symbol selection, and local scrolling
- [x] 2.2.2 Finalize the market movers panel with leaders / laggards switching and dense table presentation
- [x] 2.2.3 Finalize the desk snapshot panel with compact risk, signal, and flow summary cells
- [x] 2.3 Center chart console
- [x] 2.3.1 Finalize the instrument strip with symbol identity, session metadata, last price block, and compact instrument metrics
- [x] 2.3.2 Finalize the time-scale selector from `30S` through `1Y` as a first-class chart control row
- [x] 2.3.3 Finalize the overlay selector for `MA`, `EMA`, `BOLL`, and `VWAP`
- [x] 2.3.4 Finalize the analysis route selector for `Main`, `Momentum`, `Trend`, `Volatility`, `Order Flow`, and `Microstructure`
- [x] 2.3.5 Finalize the primary chart stage with mocked candlesticks, overlay rendering, route-aware background data, and chart legend states
- [x] 2.3.6 Finalize the lower study strip with three linked study panes that change with the selected route
- [x] 2.4 Right microstructure rail
- [x] 2.4.1 Finalize the market depth panel with ladder, profile, and imbalance modes
- [x] 2.4.2 Finalize the trapezoidal bid / ask depth visualization treatment so depth size can be scanned visually, not just numerically
- [x] 2.4.3 Finalize the order book panel with fixed multi-level bid / ask rows and spread readout
- [x] 2.4.4 Finalize the right rail tab system with `Analysis`, `Tape`, `Signals`, and `News`
- [x] 2.4.5 Finalize the non-chat `Analysis` tab as scheduled AI push cards with summary, cadence, confidence, and risk notes
- [x] 2.5 Static interaction model
- [x] 2.5.1 Finalize the client-side state model for active code, active scale, active route, movers tab, depth mode, rail tab, sort mode, and overlay toggles
- [x] 2.5.2 Finalize deterministic mock data generation for symbol, scale, chart, studies, depth, order book, tape, signals, news, and scheduled analysis cards
- [x] 2.5.3 Finalize the single rerender flow so every control change updates the correct panels without page reload

## 3. Reflex Workspace Refactor Breakdown

- [x] 3.1 `tradingassistant/frontend/app.py`
- [x] 3.1.1 Rebuild the page shell to mirror the static terminal information architecture
- [x] 3.1.2 Implement the left watchlist, movers, and snapshot rails with local scrolling only
- [x] 3.1.3 Implement the center chart console layout, control rows, chart stage, and study strip containers
- [x] 3.1.4 Implement the right microstructure rail with depth, order book, and rail-tab containers
- [x] 3.2 `tradingassistant/frontend/theme.py`
- [x] 3.2.1 Define hard-edge terminal tokens for surfaces, separators, typography, semantic highlights, and monospace numeric display
- [x] 3.2.2 Define fixed-workspace sizing, local-scroll containers, and breakpoint behavior consistent with the terminal contract
- [x] 3.3 `tradingassistant/frontend/charting.py`
- [x] 3.3.1 Add main-pane overlay support for `MA`, `EMA`, `BOLL`, and `VWAP`
- [x] 3.3.2 Add route-aware lower study configuration for `Main`, `Momentum`, `Trend`, `Volatility`, `Order Flow`, and `Microstructure`
- [x] 3.3.3 Add chart legend and compact status support that matches the static terminal contract
- [x] 3.4 Data and interaction wiring
- [x] 3.4.1 Define state and event wiring for code entry, watch selection, time-scale switching, route switching, overlay toggles, depth mode switching, and rail tab switching
- [x] 3.4.2 Keep the static reference's non-chat `Analysis` rail concept available as a dedicated scheduled-analysis surface in the later live implementation

## 4. Verification Breakdown

- [x] 4.1 Static reference verification
- [x] 4.1.1 Verify that `docs/20260613-ui-design.html` remains fully English and free of mixed-language user-facing labels
- [x] 4.1.2 Verify that the embedded script parses successfully after each structural edit
- [x] 4.1.3 Verify that whole-page scrolling remains disabled on desktop while left and right dense modules can scroll locally
- [x] 4.2 UX contract verification
- [x] 4.2.1 Verify that the watchlist can add symbols by code without any search interaction
- [x] 4.2.2 Verify that the time-scale selector covers `30S`, `1M`, `5M`, `15M`, `1H`, `4H`, `1D`, `1W`, `1MO`, and `1Y`
- [x] 4.2.3 Verify that each overlay, route, depth mode, and rail tab causes visible state changes in the static reference
- [x] 4.2.4 Verify that the `Analysis` rail is clearly a scheduled AI push surface and not a chat box
- [x] 4.3 Reflex implementation verification
- [x] 4.3.1 Verify that the Reflex workspace preserves the same module hierarchy and fixed desktop posture as the static reference
- [x] 4.3.2 Verify that the implemented chart console, study strip, and microstructure rail remain readable at desktop density without reverting to card-based stacking
