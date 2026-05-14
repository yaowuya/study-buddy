---
name: Bright Path
colors:
  surface: '#f8f9ff'
  surface-dim: '#cfdbee'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dee9fd'
  surface-container-highest: '#d8e3f7'
  on-surface: '#111c2a'
  on-surface-variant: '#414754'
  inverse-surface: '#263140'
  inverse-on-surface: '#eaf1ff'
  outline: '#727785'
  outline-variant: '#c2c6d6'
  surface-tint: '#005ac2'
  primary: '#0058bd'
  on-primary: '#ffffff'
  primary-container: '#1470e8'
  on-primary-container: '#fefcff'
  inverse-primary: '#adc6ff'
  secondary: '#785a00'
  on-secondary: '#ffffff'
  secondary-container: '#ffd167'
  on-secondary-container: '#765900'
  tertiary: '#00685f'
  on-tertiary: '#ffffff'
  tertiary-container: '#008379'
  on-tertiary-container: '#f4fffc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a41'
  on-primary-fixed-variant: '#004494'
  secondary-fixed: '#ffdf9b'
  secondary-fixed-dim: '#edc157'
  on-secondary-fixed: '#251a00'
  on-secondary-fixed-variant: '#5b4300'
  tertiary-fixed: '#70f8e8'
  tertiary-fixed-dim: '#4fdbcc'
  on-tertiary-fixed: '#00201d'
  on-tertiary-fixed-variant: '#005049'
  background: '#f8f9ff'
  on-background: '#111c2a'
  surface-variant: '#d8e3f7'
typography:
  headline-xl:
    fontFamily: Lexend
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg:
    fontFamily: Lexend
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Lexend
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-sm:
    fontFamily: Lexend
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 20px
  lg: 32px
  xl: 48px
  gutter: 16px
  margin: 24px
---

## Brand & Style

The design system is crafted to evoke a sense of energetic companionship and academic confidence. It targets Chinese primary school students, balancing a playful, childlike aesthetic with the functional clarity required for educational tasks. The brand personality is that of a "wise but fun older sibling"—encouraging, organized, and vibrantly alive.

The visual style follows a **Modern-Tactile** approach. It avoids the coldness of pure minimalism by incorporating "squishy" interactive elements and soft, layered depths. The interface mimics physical learning materials through the use of generous white space, chunky interactive zones, and a color-coded modular system that helps children navigate cognitively distinct tasks (like math versus language arts) without overwhelming them.

## Colors

The color palette of this design system is strategically functional. **Vibrant Bright Blue** serves as the primary anchor, used for core navigational elements and active task states. **Bright Yellow** is reserved for focus-heavy activities like dictation or memorization, stimulating mental alertness. **Emerald Green** signals accomplishment and positive feedback, while **Warm Orange** highlights reminders and urgent notifications.

Neutral tones are kept soft but high-contrast; a deep slate grey is used for text instead of pure black to reduce eye strain during prolonged study sessions. Backgrounds use a very light cool grey to allow the vibrant card components to pop visually.

## Typography

Typography in the design system prioritizes legibility and a friendly tone. **Lexend** is utilized for headings and numerical data due to its proven track record in reading proficiency and its open, friendly letterforms. For Chinese body text, a rounded sans-serif (like Alibaba PuHui Round) is required to maintain the soft-edged visual language. 

Font sizes are intentionally scaled larger than standard productivity apps to accommodate younger users' developing motor skills and visual processing. High line-heights are maintained to prevent "crowding" of text, making instructions easier to digest.

## Layout & Spacing

This design system employs a **Fluid Grid** model optimized for mobile and tablet devices. The spacing rhythm is based on an 8px scale, but with increased padding (20px+) inside containers to ensure that touch targets are generous and "miss-clicks" are minimized. 

Layouts should prioritize a single-column stack for primary tasks to maintain focus. Side-by-side elements are permitted only for small informational chips or secondary actions. Margins are kept wide (24px) to create a protective "frame" around the content, making the app feel like a digital workbook.

## Elevation & Depth

Visual hierarchy is established using **Tonal Layers** and **Soft Ambient Shadows**. Instead of harsh drop shadows, this design system utilizes low-opacity shadows tinted with the primary or functional color of the component (e.g., a blue card casts a soft blue shadow). 

Interactive elements like buttons should feel "pressable" using a subtle 2px vertical offset to simulate a physical button height. When an item is active or "in progress," its elevation increases slightly to draw the eye. Background surfaces remain flat and matte to keep the focus on the active "cards" floating above them.

## Shapes

The shape language is defined by extreme roundedness to ensure the UI feels safe and approachable. The base corner radius is set to **16px (1rem)** for standard cards and inputs, while primary action containers and buttons use **24px (1.5rem)** or full pill shapes. 

Sharp corners are strictly avoided. This "bubble" aesthetic reduces the perceived complexity of the software, making the educational tools feel more like toys or familiar physical stationery.

## Components

**Buttons:** Buttons are chunky and high-contrast. The primary action button features a "3D" effect with a darker bottom border (2-4px) that disappears when pressed, providing tactile feedback.

**Cards:** Cards are the primary container for tasks. Each card should have a 16px radius and a subtle colored border or shadow that corresponds to its functional module (Blue for tasks, Green for finished items).

**Progress Indicators:** Use thick, rounded bars. Progress should be celebrated with vibrant Emerald Green transitions and playful icons (e.g., a climbing character or a growing sprout).

**Input Fields:** Text fields feature a 16px radius and a thick 2px border. On focus, the border color changes to the Primary Blue, and the background subtly shifts to a very light blue tint.

**Icons:** Icons must be "friendly" and monolinear with rounded caps and joins. Avoid complex metaphors; use literal representations of school objects (pencils, books, clocks) to ensure immediate comprehension for younger students.