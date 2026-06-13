## 1. Terminal Structure And Specs

- [ ] 1.1 Finalize the desktop terminal layout with header bar, left navigator, center chart console, right microstructure rail, and lower analysis route strip
- [ ] 1.2 Finalize English workspace terminology and remove all soft consumer-board assumptions from the design contract
- [ ] 1.3 Complete the `market-microstructure-workspace`, `technical-analysis-routing`, `c-end-market-workspace`, and `trading-workspace-ui` specs for the terminal redesign

## 2. Static HTML Terminal Reference

- [ ] 2.1 Rewrite `docs/20260613-ui-design.html` as a fully English Bloomberg-style static terminal reference
- [ ] 2.2 Replace rounded glass styling with hard dark surfaces, sharp borders, dense separators, and restrained highlights
- [ ] 2.3 Show main-chart overlays, technical analysis route switching, market depth, order book, and recent prints in the static terminal reference

## 3. Reflex Workspace Refactor

- [ ] 3.1 Refactor `tradingassistant/frontend/app.py` to match the terminal layout and panel responsibilities
- [ ] 3.2 Refactor `tradingassistant/frontend/theme.py` to provide hard-edge terminal tokens and fixed-workspace rules
- [ ] 3.3 Refactor `tradingassistant/frontend/charting.py` to support overlay studies, route-friendly chart regions, and microstructure-aware side panels

## 4. Verification

- [ ] 4.1 Verify that the desktop workspace still forbids whole-page scrolling while supporting local scrolling in navigator and microstructure regions
- [ ] 4.2 Verify that the default workspace uses only English user-facing labels and no diagnostics terminology
- [ ] 4.3 Verify that the terminal reference clearly expresses chart overlays, route switching, market depth, and order book behavior before implementation begins