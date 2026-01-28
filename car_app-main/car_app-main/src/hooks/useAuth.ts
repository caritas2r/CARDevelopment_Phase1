// Simplified authentication - Flask backend has no auth, so we return mock user
import { useEffect, useState } from 'react';

// Mock user type (simplified, no Supabase)
export interface User {
  id: string;
  email?: string;
}

export interface Profile {
  id: string;
  role: 'customer' | 'admin';
  full_name: string | null;
  phone: string | null;
  created_at: string;
  updated_at: string;
}

// Mock user (no authentication needed for Flask backend)
const MOCK_USER: User = {
  id: 'mock-user-id',
  email: 'user@example.com',
};

const MOCK_PROFILE: Profile = {
  id: MOCK_USER.id,
  role: 'customer',
  full_name: null,
  phone: null,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export function useAuth() {
  const [user, setUser] = useState<User | null>(MOCK_USER);
  const [profile, setProfile] = useState<Profile | null>(MOCK_PROFILE);
  const [loading, setLoading] = useState(false); // No loading needed

  useEffect(() => {
    // No authentication needed - just set mock user immediately
    setUser(MOCK_USER);
    setProfile(MOCK_PROFILE);
    setLoading(false);
  }, []);

  const signOut = async () => {
    // No-op - no auth to sign out of
    setUser(null);
    setProfile(null);
  };

  return {
    user,
    profile,
    loading,
    signOut,
    isAdmin: profile?.role === 'admin',
  };
}
