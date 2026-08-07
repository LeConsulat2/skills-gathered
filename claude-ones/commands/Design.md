---
name: antigravity-frontend-design
description: Build, audit, and refine frontend UI for this project using the existing Antigravity glassmorphism design system. Use this when creating or improving React/Next.js components, pages, dashboards, forms, cards, navigation, landing sections, or SaaS-style application interfaces.
license: Project-specific internal design skill
---

This skill guides frontend design for this project.

The project already has a defined visual system called **Antigravity**.  
Do not invent a new theme unless explicitly asked.

The goal is to create polished, production-grade interfaces that feel modern, focused, calm, premium, and functional — without generic AI-generated aesthetics.

## Core Design Direction

Use the existing **Antigravity glassmorphism system** as the default visual language.

The UI should feel like:

- premium SaaS
- calm AI workspace
- dark glass interface
- technical but approachable
- clean, structured, slightly futuristic
- refined rather than flashy
- spacious but not empty
- visually distinctive without becoming decorative noise

The interface should never feel like:

- random startup template
- purple-gradient AI landing page
- generic shadcn dashboard
- overly playful toy UI
- plain white admin panel
- chaotic cyberpunk interface
- theme demo
- Dribbble-only concept with poor usability

## Non-Negotiable Design System Rules

### 1. Preserve the Antigravity visual identity

Use the project’s existing design system:

- dark background
- glassmorphism panels
- subtle borders
- sky-blue and emerald accents
- soft glow effects
- layered depth
- restrained gradients
- clean typography
- structured spacing
- Tailwind v4-compatible styling
- reusable classes such as `.glass-panel` where available

Do not replace the project look with Hallmark’s built-in themes.

Do not introduce unrelated palettes such as purple/pink AI gradients, orange cyberpunk, pastel candy colors, or brutalist black/yellow unless explicitly requested.

### 2. Use glass panels intentionally

Glass panels should be used for:

- main cards
- dashboards
- metric containers
- input sections
- modal surfaces
- navigation shells
- feature blocks

A good glass panel should usually include:

- translucent dark background
- subtle border
- backdrop blur
- soft shadow
- optional inner highlight
- enough contrast for readability

Avoid stacking too many glass layers until the UI becomes muddy.

### 3. Color hierarchy

Use color with discipline.

Recommended hierarchy:

- Background: dark neutral / blue-black
- Primary accent: sky blue
- Secondary accent: emerald
- Support accents: cyan, teal, soft slate, muted white
- Danger/error: controlled red only when needed
- Warning: amber only when semantically needed

Accent colors should guide attention, not decorate everything.

Do not make every icon, heading, border, and button glow at the same intensity.

### 4. Typography

Use clean, modern typography.

Default preference:

- body text should be highly readable
- headings should feel crisp and confident
- avoid overly quirky display fonts
- avoid default-looking typography that makes the UI feel unfinished

Do not use random novelty fonts.

The project’s typography should feel like a serious product, not a design experiment.

### 5. Layout principles

Prefer:

- clear hierarchy
- strong alignment
- generous but controlled spacing
- dashboard-like structure where appropriate
- cards with meaningful grouping
- clear primary action
- obvious reading flow
- responsive layouts from mobile to desktop

Avoid:

- random asymmetry
- decorative overlap that hurts scanning
- too many equal-weight cards
- unclear button hierarchy
- generic three-card sections with no product-specific purpose

## Implementation Rules

When building UI, produce real working code.

Default stack assumptions:

- Next.js / React
- TypeScript
- Tailwind CSS v4
- shadcn/ui if already installed
- existing project components where available
- no unnecessary dependencies
- no inline chaos unless justified
- no one-off design hacks that cannot be reused

Use semantic HTML and accessible patterns.

Buttons, inputs, tabs, dialogs, and navigation should be keyboard-friendly and readable.

## Tailwind v4 Compatibility

Respect Tailwind v4 conventions.

When defining theme values, prefer `@theme` blocks if editing global CSS.

Do not assume old Tailwind config patterns unless the project already uses them.

Use existing CSS variables where available.

Avoid creating a separate theme system that conflicts with the project’s current one.

## Component Quality Standard

Every component should pass these checks:

### Visual quality

- Does it look intentionally designed?
- Does it follow the Antigravity identity?
- Does it avoid generic AI/startup aesthetics?
- Does it have a clear visual hierarchy?
- Are spacing, alignment, and proportions refined?
- Are colors used with restraint?

### Functional quality

- Does it solve the actual user need?
- Is the information easy to scan?
- Are actions obvious?
- Does it behave well on mobile?
- Does it avoid unnecessary complexity?

### Code quality

- Is the component cleanly structured?
- Are repeated patterns extracted where sensible?
- Are class names understandable?
- Is state handled clearly?
- Is the code maintainable?
- Does it avoid hardcoded magic everywhere?

## Default UI Patterns for This Project

Use these patterns unless there is a strong reason not to.

### Page shell

A page should usually include:

- dark atmospheric background
- subtle gradient or glow layer
- constrained content width
- clear page heading
- short explanatory subtext
- main glass content area
- secondary panels/cards where needed

### Cards

Cards should feel layered and tactile.

Use:

- glass background
- thin border
- rounded corners
- soft shadow
- subtle hover lift only when interactive
- clear title
- concise supporting text
- meaningful icon or status indicator only when useful

### Buttons

Use clear hierarchy:

- primary: sky-blue / emerald gradient or solid accent
- secondary: glass / outline
- tertiary: text or ghost button

Avoid having multiple buttons competing visually.

### Forms

Forms should feel calm and precise.

Use:

- clear labels
- helpful descriptions
- strong focus states
- visible validation
- enough spacing between fields
- glass container only where it improves grouping

### Dashboards

Dashboards should prioritize clarity over decoration.

Use:

- metrics with clear labels
- trend/context text
- meaningful grouping
- charts that match the dark glass style
- restrained accent color
- no random rainbow chart palette

## Motion Rules

Motion should be subtle and premium.

Use motion for:

- page entrance
- card reveal
- hover states
- active navigation changes
- modal open/close
- progress or loading states

Avoid:

- excessive bouncing
- constant pulsing
- flashy animations
- animation that distracts from task completion

Good Antigravity motion feels like smooth depth, not entertainment.

## Copywriting Rules

UI copy should be:

- clear
- calm
- direct
- product-specific
- not hype-heavy

Avoid phrases like:

- “Unlock your potential”
- “Supercharge your workflow”
- “Revolutionize your experience”
- “Seamless and intuitive”
- “AI-powered magic”

Prefer concrete language that explains what the user can do.

## Audit Mode

When auditing an existing component, check for:

1. Visual drift from Antigravity
2. Weak hierarchy
3. Generic shadcn/default-card appearance
4. Too many accent colors
5. Poor contrast
6. Overuse of blur/glow
7. Unclear primary action
8. Repetitive layout patterns
9. Mobile weakness
10. Code duplication or messy structure

Return:

- what is working
- what feels off
- exact fixes
- improved code only if requested

## Redesign Mode

When redesigning, preserve:

- existing Antigravity palette
- glass-panel system
- product tone
- existing content meaning
- user flow

Improve:

- layout structure
- spacing
- hierarchy
- responsiveness
- interaction clarity
- visual polish
- component reuse

Do not randomly switch the theme.

Do not redesign into one of Hallmark’s default theme styles.

## Build Mode

When building a new component/page:

1. Identify the purpose of the UI
2. Choose the right structure for the task
3. Apply Antigravity styling
4. Make the component responsive
5. Add subtle polish
6. Keep the code clean and reusable
7. Self-audit before final output

Before final output, ask:

- Does this look like it belongs in the existing project?
- Is the design premium but usable?
- Is the glass effect controlled?
- Is the color system consistent?
- Is the component actually useful?
- Would this still look good after 20 more pages are built in the same style?

## Forbidden Defaults

Do not use:

- random Hallmark themes
- purple-blue AI gradients
- generic white SaaS cards
- default shadcn styling with no custom identity
- excessive glass blur
- fake metrics unless clearly marked as placeholder
- meaningless icons everywhere
- generic marketing copy
- overly complex animation libraries for simple effects
- visual effects that hurt readability

## Final Standard

The final UI should feel like it belongs to a real product with a coherent design system.

It should be distinctive, calm, polished, and functional.

The highest priority is not novelty.

The highest priority is **consistent, high-quality execution of the Antigravity design system**.

---

## Implementation Reference (this project)

The concrete tokens/classes the Antigravity spec resolves to in this codebase. Never use plain layouts or raw `alert()` calls.

**CSS utility classes** (defined inline in `App.tsx` `<style>` block):

- `.glass-panel` — translucent backdrop with `backdrop-filter: blur(12px)`
- `.glass-panel-hover` — hover variant
- `.btn-smooth-primary` — sky-blue gradient button
- `.btn-smooth-emerald` — emerald gradient button
- `.glow-text` — sky-to-blue gradient text fill
- `.drag-area` / `.no-drag` — Electron frameless window drag regions

**Color palette:** Sky-blue (`sky-400`, `sky-500`), emerald accents (`emerald-500`), slate text (`slate-700`, `slate-800`). HSL variables defined in `src/index.css`.

**Typography:** Uses `font-sans`. The project targets Google Fonts (Outfit, Inter, Roboto) for headings. Prefer `font-bold` / `font-extrabold` for headings and labels.

**Tailwind v4:** The project uses Tailwind CSS v4 (`@tailwindcss/vite` plugin). There is no `tailwind.config.js` — customizations use CSS-first `@theme` blocks in `src/index.css`.