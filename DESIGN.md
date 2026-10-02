---
name: Agent Underwriting Network
colors:
  background: "#0d0f0d"
  panel: "#151815"
  panelRaised: "#1b1f1a"
  border: "#2b3229"
  borderStrong: "#46513f"
  text: "#f2f2e9"
  muted: "#a4aa9d"
  accent: "#d9ff70"
  accentHover: "#b9e653"
  warning: "#ffc46b"
  danger: "#ff8f8f"
  information: "#9ecbff"
typography:
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: 16px
    lineHeight: 1.55
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
    fontWeight: 800
    letterSpacing: -0.055em
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 18px
  xl: 24px
  section: 84px
rounded:
  control: 9px
  card: 13px
  panel: 14px
  pill: 999px
---

## Overview

AUN is independent evidence infrastructure for evaluating AI agents and tools. The interface should feel precise, calm, candid, and technically credible. Preserve the graphite-and-lime identity; use restraint so bright accents mark actions and evidence state rather than decorate every surface. The product must distinguish discovery from verification and make unknown evidence visible.

## Colors

Use the dark background for page canvas, slightly lighter panels for grouped content, and thin borders to define structure. Reserve lime for primary actions, active navigation, and positive or selected states. Use amber for partial, stale, or unverified evidence; red for destructive or failed states; blue for linked provenance and informational data. Never communicate evidence status through color alone: pair it with plain labels. Maintain readable contrast for muted text and keyboard focus.

## Typography

Use the system sans stack with Inter first. Use compact uppercase labels only for metadata and section eyebrows. Headlines should be short, editorial, and responsive; body copy should explain evidence in plain language. Keep repository names and hashes legible, with hashes in a monospace face and safe wrapping.

## Layout

Use a centered content width near 1180px. Give the hero a clear headline, concise explanation, and one primary action; keep the underwriting question visible as supporting context. Use consistent section rhythm, two-column directory cards on wide screens, and a single-column flow on phones. Navigation must remain available at every viewport; on narrow screens it may scroll horizontally with full-size touch targets. Keep filters close to results and preserve visible empty, loading, and failure states.

## Elevation & Depth

Prefer flat panels with subtle surface changes and thin borders. Use shadows only for overlays that must sit above page content, such as the comparison tray and analytics consent banner. Avoid decorative glow, glass effects, or heavy gradients that compete with evidence.

## Shapes

Use 9px control corners, 12–14px card corners, and pill shapes only for compact categories or evidence labels. Keep button, input, and navigation hit areas at least 40px high, ideally 44px.

## Components

- Primary button: lime surface, dark text, bold label, clear hover and visible keyboard-focus states.
- Secondary button: transparent surface with a strong border; use for navigation alongside one primary action.
- Directory card: repository identity and description first, category and comparison control second, evidence states and freshness clearly grouped below.
- Search and filters: persistent labels, visible focus ring, immediate results, and a clear path to recover from an empty result.
- Evidence state: short text label, consistent tone, and explicit distinction between partial, unknown, not evaluated, and verified.
- Comparison tray: announce selected count, explain the four-item limit, and make clear/reset actions easy to reach.
- Consent banner: separate analytics choice from product tasks; provide equally visible decline and allow actions.

## Do's and Don'ts

- Do state what was observed, tested, and left unknown.
- Do make keyboard focus and small-screen navigation visible.
- Do keep real evidence and user tasks ahead of decorative effects.
- Do not present repository popularity as trust or task fitness.
- Do not turn partial evidence into a universal score or imply security verification that did not occur.
- Do not hide navigation or important actions on mobile.
