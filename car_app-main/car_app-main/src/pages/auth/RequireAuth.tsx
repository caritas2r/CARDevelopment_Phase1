// Simplified authentication wrapper - Flask backend has no auth, so just render children
import { ReactNode } from 'react';

interface RequireAuthProps {
  children: ReactNode;
  adminOnly?: boolean;
}

export function RequireAuth({ children, adminOnly = false }: RequireAuthProps) {
  // Flask backend has no authentication, so just render children
  // If adminOnly is true, we could still check, but for now just render
  return <>{children}</>;
}
