import { Car } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-black border-t border-brand-gold/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <img
              src="/CAR logo 2B TRANSPARENT (1).png"
              alt="Cross Automotive Royale Logo"
              className="h-10 w-auto"
            />
          </div>
          
          <div className="text-center md:text-right">
            <p className="text-gray-400 text-sm">
              © 2025 Cross Automotive Royale. All rights reserved.
            </p>
            <p className="text-gray-500 text-xs mt-1">
              Build Your Adventure
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}