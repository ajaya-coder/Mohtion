# Frontend Design Rules: The "Powerhouse" Standard

This document defines the aesthetic and technical standards for the Mohtion landing page. All generated UI components must adhere strictly to these rules to avoid "AI Slop" and ensure a high-fidelity, professional result.

## 1. Core Aesthetic: "Abyssal Engineering"

We are building a tool for engineers, not a marketing brochure for a generic SaaS. The vibe should be technical, precise, and deep.

-   **Backgrounds**: Avoid pure black (`#000`). Use rich, deep grays with subtle cool undertones (e.g., Slate-950, Zinc-900).
    -   *Good*: `bg-slate-950`, `bg-[#0B0F19]`
    -   *Bad*: `bg-black`, `bg-white`, `bg-gray-100`
-   **Lighting**: Use subtle "glows" and gradients to define space, rather than hard borders.
    -   *Technique*: `radial-gradient` backgrounds for sections.
    -   *Technique*: 1px borders with low opacity (`border-white/10`) for cards.
-   **Glassmorphism**: Use backdrop blurs sparingly but effectively for floating elements (navbars, toasts).
    -   *Class*: `backdrop-blur-md bg-slate-900/70`

## 2. Typography & Layout

Typography is the primary interface. It must be bold and readable.

-   **Font Stack**: Inter (sans) for UI, JetBrains Mono or Fira Code for code/technical terms.
-   **Hierarchy**:
    -   **H1**: Massive, tight tracking (`-tracking-tighter`), high contrast.
        -   *Example*: `text-5xl md:text-7xl font-bold tracking-tighter text-white`
    -   **H2**: Strong, distinct.
    -   **Body**: Readable, slightly muted (`text-slate-400`), strict line-height relaxation (`leading-relaxed`).
-   **Spacing**:
    -   **Avoid Tightness**: Give components room to breathe. Use `gap-8`, `gap-12`, `py-24` freely.
    -   **Grid**: Use CSS Grid for complex layouts, Flexbox for alignment.

## 3. Component Guidelines

### Buttons
-   **Primary**: No generic solid colors. Use subtle gradients or "shining" borders.
    -   *Style*: Dark background, light border/text, subtle hover glow.
    -   *Interactive*: `hover:scale-105 active:scale-95 transition-all duration-200`.
-   **Secondary**: Ghost buttons with `text-slate-400 hover:text-white`.

### Cards (Features/Bounties)
-   **Surface**: Dark, slightly lighter than background (`bg-white/5`).
-   **Border**: 1px solid `border-white/10`.
-   **Highlight**: On hover, lighten the border or add a subtle inner glow.

### Visualizations
-   **Code Blocks**: Must look like a real terminal.
    -   *Header*: MacOS style window controls (red/yellow/green dots).
    -   *Font*: Monospace, colored syntax highlighting (manually styled spans).
-   **Diagrams**: Use simple geometric primitives with glowing edges to represent the "Agent Loop".

## 4. "Forbidden" Patterns (Anti-Patterns)

-   ❌ **NO** generic Bootstrap-style drop shadows (`shadow-lg`). Use colored shadows or glows instead.
-   ❌ **NO** pure blue primary buttons (`bg-blue-500`).
-   ❌ **NO** "Corporate Memphis" illustrations (flat vector people).
-   ❌ **NO** low-contrast gray text on gray backgrounds that fails accessibility.
-   ❌ **NO** rounded-full buttons unless they are "chips" or tags. Use `rounded-lg` or `rounded-md` for actions.

## 5. Technical Stack

-   **Framework**: Next.js 14+ (App Router)
-   **Styling**: Tailwind CSS
-   **Animation**: Framer Motion (for entrance animations and hover states).
-   **Icons**: Lucide React (stroke-width: 1.5 or 2).

## 6. Implementation Checklist

When generating code:
1.  Does this look like a tool for a Senior Engineer?
2.  Is the contrast sufficient?
3.  Is the spacing intentional (not accidental)?
4.  Are we using semantic HTML?
