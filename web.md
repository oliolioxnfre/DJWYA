# 🌐 DJWYA Web Interface Documentation

This document provides a high-level overview of the web portion of the DJWYA project, detailing the tech stack, design philosophy, and core architecture.

## 🛠 Tech Stack

- **Framework**: [Next.js](https://nextjs.org/) (App Router)
  - Leverages Server Components for performance and Client Components for interactivity.
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
  - Uses the new `@theme` engine for design tokens and CSS-native variables.
- **Animations**: [Framer Motion](https://www.framer.com/motion/)
  - Powers the "Sonic DNA" text transitions and premium hover effects.
- **Backend & Auth**: [Supabase](https://supabase.com/)
  - Handles Google SSO OAuth flow and real-time database connections to the Python-processed user data.
- **Icons**: [Lucide React](https://lucide.dev/)

---

## 🎨 Design Philosophy: "The Artist Prism"

The UI is designed to feel **premium, alive, and immersive**.

1.  **Aesthetics**: 
    - **Dark Mode First**: Deep `#0a0a0a` backgrounds to make neon accents pop.
    - **Glassmorphism**: Use of `backdrop-blur` and low-opacity borders to create depth.
    - **Vibrant Gradients**: A consistent palette of Purple (#8b5cf6), Pink (#ec4899), and Neon Pink (#ff00ff).
2.  **Typography**:
    - **Outfit**: A geometric sans-serif used for headings to provide a modern, "tech-forward" brand feel.
    - **Inter**: The gold standard for legible, clean body text.
3.  **Micro-interactivity**:
    - Hover-scale transformations on buttons and images.
    - Blurry background "glows" that provide a sense of atmospheric lighting.

---

## 🏗 Directory Structure (`/web`)

```text
src/
├── app/                  # Next.js App Router (Pages)
│   ├── page.tsx          # Landing Page (Hero + SSO Entry)
│   ├── auth/callback/    # Google SSO Redirect handler
│   └── dashboard/        # Protected User Dashboard
├── components/           # Reusable UI Logic
│   ├── auth/             # LoginButton, etc.
│   └── ui/               # AnimatedText, Charts, etc.
├── lib/                  # Utility initializations
│   └── supabaseClient.ts # Supabase Browser Client
└── globals.css           # Tailwind v4 Theme & Base Layers
```

---

## 🔐 Authentication Flow

1.  **Trigger**: User clicks `LoginButton.tsx` (sign in with Google).
2.  **Handshake**: Supabase redirects user to Google accounts.
3.  **Callback**: Upon success, Google returns user to `/auth/callback`.
4.  **Session**: The callback page verifies the session and redirects the user to the protected `/dashboard`.
5.  **Persistence**: Auth state is managed via Supabase's `onAuthStateChange` listener.

---

## 🚀 Ongoing Development

- **Sonic DNA Visualization**: Porting the geometric "StarChart" logic from Python to a React-friendly SVG implementation using Framer Motion.
- **Data Integration**: Wiring the Dashboard to fetch the `sonic_dna` JSONB column from the `users` table.
