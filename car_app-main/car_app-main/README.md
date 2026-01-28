# CAR Frontend

React/TypeScript frontend application for the CAR vehicle selection system.

## Technology Stack

- **React** 18.3+ with TypeScript
- **Vite** for build tooling and development server
- **React Router** 7.8+ for client-side routing
- **TanStack Query** 5.85+ for data fetching and caching
- **React Hook Form** 7.62+ with Zod 4.1+ for form validation
- **Tailwind CSS** 3.4+ for styling
- **Lucide React** for icons
- **React Hot Toast** for notifications

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── EmptyState.tsx
│   │   ├── Footer.tsx
│   │   ├── FormField.tsx
│   │   ├── FormStepper.tsx
│   │   ├── Layout.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── Nav.tsx
│   │   ├── SearchableDropdown.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── Table.tsx
│   │   └── Toast.tsx
│   │
│   ├── pages/               # Page components
│   │   ├── Landing.tsx      # Landing page
│   │   ├── auth/            # Authentication pages
│   │   ├── sourcing/        # Vehicle sourcing pages
│   │   ├── concierge/       # Concierge services
│   │   ├── build/           # Build orders
│   │   ├── billing/         # Billing portal
│   │   └── admin/           # Admin dashboard
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Authentication hook
│   │   └── useStripePortal.ts
│   │
│   ├── lib/                 # API clients and utilities
│   │   ├── api.ts           # Flask backend API client
│   │   ├── stripe.ts        # Stripe integration
│   │   └── supabase.ts      # Legacy (redirects to api.ts)
│   │
│   ├── store/               # State management
│   │   └── query.tsx        # Query state store
│   │
│   ├── types.ts             # TypeScript type definitions
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles
│
├── public/                  # Static assets
│   ├── *.png                # Vehicle images
│   └── *.woff               # Font files
│
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Setup

### Install Dependencies

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` (or the next available port).

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Configuration

### API Base URL

The frontend connects to the Flask backend API. Configure the API base URL via environment variable:

```bash
# .env file
VITE_API_BASE_URL=http://localhost:5000
```

If not set, defaults to `http://localhost:5000`.

### Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL (default: `http://localhost:5000`)

## Features

### Vehicle Sourcing

- **Natural Language Queries**: Submit queries in natural language
- **Query Results**: View vehicle search results with detailed information
- **Query Feedback**: Submit feedback for unsatisfactory results

### Pages

- **Landing Page** (`/`): Application landing page
- **Sourcing** (`/sourcing`): Submit vehicle queries
- **Candidates** (`/sourcing/candidates`): View query results
- **Concierge Services**: Stub page (not yet implemented)
- **Build Orders**: Stub page (not yet implemented)
- **Billing Portal**: Stub page (not yet implemented)
- **Admin Dashboard**: Stub page (not yet implemented)

## API Integration

The frontend uses the Flask backend API. See `src/lib/api.ts` for API client implementation.

### Main Endpoints

- `POST /api/query/v1` - Submit natural language vehicle query
- `POST /api/query/feedback` - Submit query feedback
- `POST /api/payment/process` - Process payment (Stripe)

## Development Notes

- Authentication is currently simplified (mock user)
- Results are stored in sessionStorage between pages
- The application uses React Router for client-side routing
- TanStack Query handles API calls and caching
- Form validation uses React Hook Form with Zod schemas

## Deployment

### Vercel

This frontend is configured for Vercel deployment. See root `vercel.json` for configuration.

**Deployment Steps:**

1. Connect repository to Vercel
2. Set root directory: `car_app-main/car_app-main` (or update vercel.json if restructured)
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Add environment variable: `VITE_API_BASE_URL` (your backend API URL)

The `vercel.json` file handles SPA routing with rewrites.

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
