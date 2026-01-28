import { Link } from 'react-router-dom';
import { Car, Shield, Wrench, Search, CreditCard, Calendar } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export function Landing() {
  const { user, profile } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen bg-black">
        <div className="relative overflow-hidden">
          {/* Hero Section */}
          <div className="relative z-10 pb-8 bg-black sm:pb-16 md:pb-20 lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="text-center">
                <h1 className="text-4xl tracking-tight font-extrabold text-white sm:text-5xl md:text-6xl font-race-sport">
                  <span className="block">CROSS AUTOMOTIVE</span>
                  <span className="block text-brand-gold">ROYALE</span>
                </h1>
                <p className="mt-3 max-w-md mx-auto text-base text-gray-300 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
                  Build Your Adventure
                </p>
                <p className="mt-6 max-w-2xl mx-auto text-gray-400">
                  Premium automotive concierge services, custom builds, and vehicle sourcing for discerning enthusiasts.
                </p>
                <div className="mt-8 flex justify-center">
                  <Link
                    to="/auth/signin"
                    className="bg-brand-gold text-white px-8 py-3 font-semibold rounded-lg hover:opacity-80 transition-all tracking-wide"
                  >
                    Access Portal
                  </Link>
                </div>
              </div>
            </main>
          </div>
        </div>

        {/* Features Section */}
        <div className="py-16 bg-gray-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-extrabold text-white">
                BUILD. BUY. CONCIERGE
              </h2>
              <p className="mt-4 text-lg text-gray-400">
                There are three ways to engage with C.A.R. on your next adventure.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-brand-gold/10 border-2 border-brand-gold">
                  <Wrench className="h-8 w-8 text-brand-gold" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">BUILD WITH US</h3>
                <p className="mt-4 text-gray-400">
                  Custom builds from our curated inventory with expert craftsmanship and attention to detail.
                </p>
              </div>

              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-brand-gold/10 border-2 border-brand-gold">
                  <Search className="h-8 w-8 text-brand-gold" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">INVEST WITH US</h3>
                <p className="mt-4 text-gray-400">
                  AI-powered vehicle sourcing to find the perfect match for your specifications and budget.
                </p>
              </div>

              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-brand-gold/10 border-2 border-brand-gold">
                  <Shield className="h-8 w-8 text-brand-gold" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">ROYALE CONCIERGE</h3>
                <p className="mt-4 text-gray-400">
                  White-glove storage and maintenance services to protect and preserve your investment.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-white mb-4">
            Welcome Back, {profile?.full_name || 'Demo User'}
          </h1>
          <p className="text-gray-400 text-lg">
            Manage your orders, concierge services, and vehicle portfolio
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            to="/concierge"
            className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-brand-gold transition-colors group"
          >
            <Shield className="h-10 w-10 text-brand-gold mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Royale Concierge</h3>
            <p className="text-gray-400 text-sm">
              Premium storage and maintenance services for your vehicles
            </p>
          </Link>

          <Link
            to="/build"
            className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-brand-gold transition-colors group"
          >
            <Wrench className="h-10 w-10 text-brand-gold mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Custom Builds</h3>
            <p className="text-gray-400 text-sm">
              Commission a custom build from our curated inventory
            </p>
          </Link>

          <Link
            to="/sourcing"
            className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-brand-gold transition-colors group"
          >
            <Search className="h-10 w-10 text-brand-gold mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Vehicle Sourcing</h3>
            <p className="text-gray-400 text-sm">
              AI-powered search for your perfect vehicle worldwide
            </p>
          </Link>

          <Link
            to="/billing"
            className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-brand-gold transition-colors group"
          >
            <CreditCard className="h-10 w-10 text-brand-gold mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Billing & Payments</h3>
            <p className="text-gray-400 text-sm">
              Manage subscriptions, view invoices, and update payment methods
            </p>
          </Link>

          <Link
            to="/concierge/services"
            className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-brand-gold transition-colors group"
          >
            <Calendar className="h-10 w-10 text-brand-gold mb-4 group-hover:scale-110 transition-transform" />
            <h3 className="text-lg font-semibold text-white mb-2">Schedule Services</h3>
            <p className="text-gray-400 text-sm">
              Book detailing, maintenance, and other concierge services
            </p>
          </Link>

          {profile?.role === 'admin' && (
            <Link
              to="/admin"
              className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-brand-gold transition-colors group"
            >
              <Car className="h-10 w-10 text-brand-gold mb-4 group-hover:scale-110 transition-transform" />
              <h3 className="text-lg font-semibold text-white mb-2">Admin Dashboard</h3>
              <p className="text-gray-400 text-sm">
                Manage customers, orders, and operations
              </p>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
