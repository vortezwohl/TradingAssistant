## Why

The current watch page already has live chart plumbing, but the interface still reads like an engineering dashboard rather than a market terminal. It needs to move from a soft, card-based consumer shell to a hard-edged Wall Street workspace that supports serious chart reading, technical analysis switching, market depth inspection, and order book monitoring without whole-page scrolling.

## What Changes

- Redefine the homepage as an English-language terminal workspace instead of a soft consumer board with mixed business and engineering semantics.
- Replace rounded glass panels and decorative SaaS styling with a harder Bloomberg-inspired visual system built on dense grids, flat dark surfaces, sharp borders, restrained highlights, and high-contrast data typography.
- Upgrade the primary chart area into a chart console that supports price overlays such as moving averages, exponential moving averages, Bollinger Bands, and VWAP directly on the main chart surface.
- Introduce a first-class analysis routing model so users can switch the secondary chart console between grouped technical studies such as momentum, trend, volatility, and order-flow views when an indicator should not live directly on the main price pane.
- Add dedicated market microstructure modules for market depth, order book, and recent prints / time-and-sales rather than collapsing all secondary data into summary cards.
- Preserve the fixed desktop viewport rule and local scrolling rule while extending the workspace into a denser terminal-style multi-panel layout.
- Rewrite the static HTML design reference in English so it can serve as the clean visual and structural contract for the Reflex implementation.

## Capabilities

### New Capabilities
- `market-microstructure-workspace`: defines market depth, order book, spread, imbalance, and time-and-sales behavior inside the trading terminal workspace
- `technical-analysis-routing`: defines chart overlay groups, secondary indicator routes, and how users switch among technical study views

### Modified Capabilities
- `c-end-market-workspace`: expand the workspace definition from a generic customer-facing board into an English-language hard-edge terminal shell
- `trading-workspace-ui`: upgrade the desktop workspace requirements to support terminal-style density, chart console routing, and microstructure side panels

## Impact

- Primarily affects `tradingassistant/frontend/app.py`, `tradingassistant/frontend/theme.py`, and `tradingassistant/frontend/charting.py` because the page skeleton, tone, and visual tokens will all change.
- Requires new OpenSpec specs for `market-microstructure-workspace` and `technical-analysis-routing`.
- Requires updates to the existing `c-end-market-workspace` and `trading-workspace-ui` change specs so the static reference and implementation plan match the new target.
- Requires a full rewrite of `docs/20260613-ui-design.html` into an English Bloomberg-style terminal reference with indicator routes, market depth, and order book panels.