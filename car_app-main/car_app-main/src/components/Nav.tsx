import { Link, useLocation } from 'react-router-dom';
import { Menu, User, X, ChevronDown } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

export function Nav() {
  const [isOpen, setIsOpen] = useState(false);
  const [sourcingOpen, setSourcingOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const location = useLocation();
  const { user, profile, signOut, isAdmin } = useAuth();
  const sourcingRef = useRef<HTMLDivElement>(null);
  const userDropdownRef = useRef<HTMLDivElement>(null);

  // Close sourcing dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (sourcingRef.current && !sourcingRef.current.contains(event.target as Node)) {
        setSourcingOpen(false);
      }
      if (userDropdownRef.current && !userDropdownRef.current.contains(event.target as Node)) {
        setUserDropdownOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navigation = [
    { name: 'Dashboard', href: '/' },
    { name: 'Concierge', href: '/concierge' },
    { name: 'Build Orders', href: '/build' },
    { name: 'Billing', href: '/billing' },
    ...(isAdmin ? [{ name: 'Admin', href: '/admin' }] : []),
  ];

  const sourcingItems = [
    { name: 'New Search', href: '/sourcing' },
    { name: 'Search Results', href: '/sourcing/candidates' },
  ];

  return (
    <nav className="bg-black/95 backdrop-blur-sm border-b border-brand-gold/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <img
                src="/CAR logo 2B TRANSPARENT (1).png"
                alt="Cross Automotive Royale Logo"
                className="h-12 w-auto"
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
          <div className="hidden md:flex items-center md:space-x-4 lg:space-x-6 xl:space-x-8">
            {user && navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-2 text-sm font-medium tracking-wide transition-colors ${
                  location.pathname === item.href
                    ? 'text-brand-gold border-b-2 border-brand-gold'
                    : 'text-white hover:text-brand-gold'
                }`}
              >
                {item.name}
              </Link>
            ))}
            
            {/* Sourcing Dropdown */}
            {user && (
              <div ref={sourcingRef} className="relative">
                <button
                  onClick={() => setSourcingOpen(!sourcingOpen)}
                  className={`flex items-center space-x-1 px-3 py-2 text-sm font-medium tracking-wide transition-colors ${
                    location.pathname.startsWith('/sourcing')
                      ? 'text-brand-gold border-b-2 border-brand-gold'
                      : 'text-white hover:text-brand-gold'
                  }`}
                >
                  <span>Sourcing</span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${sourcingOpen ? 'rotate-180' : ''}`} />
                </button>
                
                {sourcingOpen && (
                  <div className="absolute top-full left-0 mt-1 w-48 bg-gray-900 border border-gray-700 rounded-md shadow-lg z-50">
                    {sourcingItems.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        onClick={() => setSourcingOpen(false)}
                        className={`block px-4 py-2 text-sm text-white hover:bg-brand-gold/10 hover:text-brand-gold transition-colors ${
                          location.pathname === item.href ? 'bg-brand-gold/10 text-brand-gold' : ''
                        }`}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )}

            {user && (
              <div ref={userDropdownRef} className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="text-gray-300 hover:text-white transition-colors p-2"
                >
                  <User className="h-5 w-5" />
                </button>
                
                {userDropdownOpen && (
                  <div className="absolute top-full right-0 mt-1 w-48 bg-gray-900 border border-gray-700 rounded-md shadow-lg z-50">
                    <div className="px-4 py-3 border-b border-gray-700">
                      <p className="text-sm text-gray-300 truncate">
                        {profile?.full_name || user.email}
                      </p>
                    </div>
                    <button
                      onClick={() => {
                        signOut();
                        setUserDropdownOpen(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-white hover:bg-brand-gold/10 hover:text-brand-gold transition-colors"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-white hover:text-yellow-400 transition-colors"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden bg-black/98 border-t border-brand-gold/20">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {user && navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`block px-3 py-2 text-base font-medium tracking-wide transition-colors ${
                  location.pathname === item.href
                    ? 'text-brand-gold bg-brand-gold/10'
                    : 'text-white hover:text-brand-gold hover:bg-brand-gold/5'
                }`}
                onClick={() => setIsOpen(false)}
              >
                {item.name}
              </Link>
            ))}
            
            {/* Mobile Sourcing Items */}
            {user && sourcingItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`block px-3 py-2 text-base font-medium tracking-wide transition-colors ${
                  location.pathname === item.href
                    ? 'text-brand-gold bg-brand-gold/10'
                    : 'text-white hover:text-brand-gold hover:bg-brand-gold/5'
                }`}
                onClick={() => setIsOpen(false)}
              >
                {item.name}
              </Link>
            ))}

            {user && (
              <div className="px-3 py-2 border-t border-gray-700 mt-2">
                <div className="text-gray-300 text-sm mb-2">
                  {profile?.full_name || user.email}
                </div>
                <button
                  onClick={() => {
                    signOut();
                    setIsOpen(false);
                  }}
                  className="text-gray-300 hover:text-white transition-colors text-sm"
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}