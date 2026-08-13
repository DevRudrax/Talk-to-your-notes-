---
name: Quiet Intelligence
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#434656'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#747688'
  outline-variant: '#c4c5d9'
  surface-tint: '#104af0'
  primary: '#0040df'
  on-primary: '#ffffff'
  primary-container: '#2d5bff'
  on-primary-container: '#efefff'
  inverse-primary: '#b8c3ff'
  secondary: '#5f5e5c'
  on-secondary: '#ffffff'
  secondary-container: '#e4e2df'
  on-secondary-container: '#656462'
  tertiary: '#993100'
  on-tertiary: '#ffffff'
  tertiary-container: '#c24100'
  on-tertiary-container: '#ffece6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#b8c3ff'
  on-primary-fixed: '#001355'
  on-primary-fixed-variant: '#0035bd'
  secondary-fixed: '#e4e2df'
  secondary-fixed-dim: '#c8c6c3'
  on-secondary-fixed: '#1b1c1a'
  on-secondary-fixed-variant: '#474745'
  tertiary-fixed: '#ffdbcf'
  tertiary-fixed-dim: '#ffb59b'
  on-tertiary-fixed: '#380d00'
  on-tertiary-fixed-variant: '#812900'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is anchored in the concept of "Quiet Intelligence." It prioritizes the user's content over the interface itself, creating a focused environment for deep thought and synthesis. The style is **Ultra-Minimalist**, drawing heavy inspiration from the utility of developer tools and the clarity of modern AI interfaces.

The emotional goal is to provide a sense of calm and competence. There are no distractions—no gradients, no vibrant "AI" purples, and no superfluous decorations. Instead, the system relies on precise alignment, generous but purposeful whitespace, and a monochromatic palette to convey sophistication and speed.

## Colors

The palette is strictly functional. The primary background uses a warm off-white in light mode to reduce eye strain, while dark mode utilizes a deep charcoal to maintain contrast without the harshness of pure black.

- **Primary:** A restrained Blue (#2D5BFF) used exclusively for primary actions and active indicators.
- **Surface:** Subtle variations in gray levels define hierarchy. In dark mode, `#1E1E1E` is used for elevated panels.
- **Borders:** Very thin, low-contrast grays create structure without visual noise.
- **Text:** High-contrast charcoal or off-white for maximum legibility, with secondary text dropping significantly in opacity to create a visual "recede" for metadata.

## Typography

This design system uses **Geist** for its technical precision and monospaced-adjacent feel, which lends an air of "engineered" reliability. 

The hierarchy is achieved through weight and color rather than excessive scale. Headings are kept small to maintain high information density. Body text is prioritized for long-form reading of notes. Labels and metadata use semi-bold weights at small sizes to remain legible while occupying minimal space.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid** model. Navigation and sidebar elements are fixed-width to ensure tool accessibility, while the central note/chat area is fluid with a maximum readable width of 768px.

A strict 4px grid governs all spacing. Vertical rhythm is tight, favoring a "high-density" feel that mimics professional productivity software. 

- **Desktop:** 3-column layout (Navigation, Content, Contextual Sidebar).
- **Mobile:** Single column with bottom-anchored input and top-level navigation hidden behind a simple trigger.

## Elevation & Depth

Elevation is primarily communicated through **Tonal Layers** and **Subtle Outlines** rather than heavy shadows. 

1. **Level 0 (Base):** The main background.
2. **Level 1 (Panels):** Slightly lighter (dark mode) or darker (light mode) surfaces with a 1px solid border.
3. **Level 2 (Popovers/Modals):** These use a very soft, diffused shadow (0px 4px 12px rgba(0,0,0,0.05)) and a crisp border to separate them from the content below.

There is no glassmorphism. Surfaces are 100% opaque to maintain focus and performance perception.

## Shapes

The shape language is "Soft-Square." A universal radius of **4px to 6px** is applied to buttons, inputs, and panels. This is enough to feel modern and human, but sharp enough to feel professional and precise.

Interactive elements (buttons, checkboxes) use the same radius to maintain a consistent visual rhythm across the UI.

## Components

### Buttons
- **Primary:** Solid neutral background with off-white text. No gradients.
- **Secondary:** Transparent background with a 1px border.
- **Ghost:** No background or border until hover. Used for low-priority actions in toolbars.

### Input Fields
- Inputs are subtle, using a light gray background and a 1px border that shifts to the primary accent color on focus.
- The AI chat input is the most prominent element, featuring a slightly larger vertical padding and a soft inner shadow to denote "depth" for text entry.

### Lists
- High-density list items (12px to 14px text) separated by subtle 1px lines. 
- Hover states use a very light gray (#F0F0EF) or charcoal (#1A1A1A) fill to indicate interactivity.

### Chips/Tags
- Rectangular with minimal rounding (2px). 
- Use a monochromatic palette (light gray background, dark text) to avoid competing with primary actions.

### Micro-interactions
- Transitions are near-instant (150ms). 
- Use "Ease-Out" for entering elements to make the interface feel responsive and snappy.