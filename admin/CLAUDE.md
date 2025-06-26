# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

- **Development**: `npm run dev` (uses Turbopack for faster builds)
- **Build**: `npm run build`
- **Production**: `npm start` 
- **Linting**: `npm run lint`

## Architecture Overview

This is a Next.js 15 admin dashboard application with the following structure:

- **App Router**: Uses Next.js App Router with TypeScript
- **Layout System**: Two-tier layout structure:
  - Root layout (`app/layout.tsx`) - handles fonts and basic HTML structure
  - Dashboard layout (`app/dashboard/layout.tsx`) - provides sidebar navigation and admin interface
- **UI Components**: Uses shadcn/ui components with Radix UI primitives and Tailwind CSS
- **Navigation**: Dashboard has dedicated sections for Dashboard, Booking, Knowledge, and Settings
- **Authentication**: Login flow exists but logout is placeholder (redirects to `/login`)

## Key Technologies

- Next.js 15 with App Router
- React 19
- TypeScript with strict mode
- Tailwind CSS v4 with CSS variables
- shadcn/ui component library (New York style)
- Lucide React for icons
- Radix UI primitives for complex components
- React Hook Form with Zod validation
- Additional libraries: @dnd-kit for drag & drop, date-fns, recharts

## Import Patterns

- Uses `@/*` path alias for all imports (configured in tsconfig.json)
- UI components imported from `@/components/ui/*`
- Utilities imported from `@/lib/utils`
- Component style follows shadcn/ui conventions with `cn()` utility for conditional classes