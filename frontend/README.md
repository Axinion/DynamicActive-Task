# K12 LMS Frontend

A modern Next.js frontend for the K12 Learning Management System.

## Prerequisites

- Node.js 20+ (see `.nvmrc`)
- npm or yarn

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Other Scripts

```bash
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
npm run typecheck # Run TypeScript checks
```

## Demo Credentials

- **Teacher**: `teacher@example.com` / `pass`
- **Student**: `student@example.com` / `pass`

## Project Structure

```
frontend/
├── app/                 # Next.js App Router pages
│   ├── teacher/        # Teacher dashboard and pages
│   ├── student/        # Student dashboard and pages
│   ├── login/          # Authentication pages
│   └── layout.tsx      # Root layout
├── components/         # Reusable UI components
│   ├── ui/            # Basic UI components (Button, Card, etc.)
│   ├── Header.tsx     # Navigation header
│   ├── Sidebar.tsx    # Navigation sidebar
│   └── EmptyState.tsx # Empty state component
├── lib/               # Utilities and stores
│   ├── auth.ts        # Authentication store (Zustand)
│   └── utils.ts       # Utility functions
└── public/            # Static assets
```

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: Zustand
- **UI Components**: Custom components with TailwindCSS

## API Integration

The frontend is configured to connect to the backend API at `http://localhost:8000/api`. This is set via the `NEXT_PUBLIC_API_BASE` environment variable.

## Features

- **Role-based Authentication**: Separate teacher and student experiences
- **Responsive Design**: Mobile-first design with TailwindCSS
- **Dark Mode**: Built-in dark mode support
- **Type Safety**: Full TypeScript support
- **Modern UI**: Clean, accessible interface with custom design system

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000/api
```

## Development Notes

- Uses Next.js App Router for modern routing
- Implements client-side authentication with Zustand
- Route guards protect teacher/student pages
- Mock authentication for development (no backend required initially)