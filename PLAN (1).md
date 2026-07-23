Coding Prompt: Market Watch Horizontal Ticker
Objective: Implement a financial market ticker component for "The Daily Digest," a newspaper-style news aggregator.

1. Layout & Structure:

Positioning: Place the ticker as a full-width horizontal strip directly below the primary navigation bar and above the main content area.
Container: Use a low-density, fixed-height container with a background color of #fdf8f7 (Surface).
Dividers: Encapsulate the row with single-pixel hairline borders (border-y border-outline/20) to mimic traditional print rule lines.
Label: On the far left, include a static "MARKET WATCH" label in small, tracked-out, uppercase monospace text.
2. Data Display:

Horizontal Row: Arrange 4–5 financial indices (e.g., SENSEX, NIFTY 50, GOLD, USD/INR) in a single horizontal flex row with generous spacing (gap-8).
Data Point Formatting: Each item should follow this inline pattern: [INDEX NAME] [VALUE] [CHANGE] ([PERCENTAGE]).
Typographic Contrast:
Index Name: Uppercase monospace (e.g., Courier or JetBrains Mono), font-size: 10px, color: #1a1a17.
Value: Bold monospace, font-size: 12px.
Indicators: Use a professional "Business Green" (#2e7d32) for positive movements and a muted red for negative. Use simple + or - symbols rather than heavy arrows.
3. Visual Language (Design System Integration):

Aesthetic: Maintain a "Tactile Broadsheet" feel. No gradients, shadows, or rounded corners. Everything should feel like ink on paper.
Spacing: Ensure the vertical height of the ticker is minimal (approx. 40-48px) to provide a quick "at-a-glance" update without pushing the headline news too far down the fold.
Design Rationale for the Coding Agent:
Information Hierarchy: The horizontal ticker serves as a "functional bridge" between the branding/navigation header and the editorial content.
Print-First UX: By using monospace fonts for data, we evoke the style of 20th-century financial broadsheets, providing a high-contrast, legible, and authoritative market summary.