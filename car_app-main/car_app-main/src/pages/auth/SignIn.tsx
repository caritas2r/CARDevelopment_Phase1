// Simplified SignIn - Flask backend has no auth, so just redirect to home
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Car } from 'lucide-react';

export function SignIn() {
  const navigate = useNavigate();

  useEffect(() => {
    // Flask backend has no authentication, so just redirect to home
    navigate('/');
  }, [navigate]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="text-center">
        <Car className="h-16 w-16 text-brand-gold mx-auto mb-4 animate-pulse" />
        <p className="text-white">Redirecting...</p>
      </div>
    </div>
  );
}
