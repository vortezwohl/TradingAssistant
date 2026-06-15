
## 1. Chart Hover Data Contract

- [x] 1.1 Extend `tradingassistant/frontend/charting.py` to generate structured hover metadata for the primary chart candles instead of exposing only latest-value legend output
- [x] 1.2 Extend `tradingassistant/frontend/charting.py` to generate route-aware hover metadata for lower study panes using the same shared chart index contract
- [x] 1.3 Extend `tradingassistant/frontend/state.py` with derived hover-ready chart payload accessors needed by the chart console without coupling hover logic to SVG parsing

## 2. Hover Interaction Surface

- [x] 2.1 Refactor the center chart stage in `tradingassistant/frontend/app.py` so the primary chart stage can host a compact in-console hover detail surface
- [x] 2.2 Add shared hover index wiring so the primary chart and lower study strip update from the same active chart position
- [x] 2.3 Add hover-exit reset behavior so stale historical readouts do not remain active after the pointer leaves the chart interaction region

## 3. Left Rail Density And Alignment Fixes

- [x] 3.1 Audit and tighten left-rail row sizing, padding, line-height, and min-width rules in `tradingassistant/frontend/theme.py` and `tradingassistant/frontend/app.py`
- [x] 3.2 Fix watchlist and movers row text fitting so symbol identity, secondary metadata, and numeric fields remain aligned and readable under dense terminal width constraints
- [x] 3.3 Fix lower-left snapshot cell text fitting so labels, values, and captions remain fully readable within the cell bounds

## 4. Verification

- [x] 4.1 Extend `tests/test_frontend.py` with regression coverage for hover metadata availability, shared hover contract shape, and left-rail density/alignment rules
- [x] 4.2 Re-run frontend validation with `py_compile`, frontend tests, and `python -m reflex export --no-zip`
- [ ] 4.3 Manually verify on desktop that chart hover detail follows the active chart unit and that left-rail rows no longer show clipped or vertically shifted text
