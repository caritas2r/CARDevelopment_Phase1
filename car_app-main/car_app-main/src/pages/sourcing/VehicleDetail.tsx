import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Handshake } from 'lucide-react';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { EmptyState } from '../../components/EmptyState';
import { QueryResponse, VehicleResult } from '../../lib/api';
import { formatPrice } from '../../lib/stripe';
import toast from 'react-hot-toast';

function formatMileage(mileage?: number): string {
  if (!mileage) return 'Mileage not specified';
  return `${mileage.toLocaleString()} mi`;
}

export function VehicleDetail() {
  const navigate = useNavigate();
  const { index } = useParams<{ index: string }>();
  const [vehicle, setVehicle] = useState<VehicleResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load results from sessionStorage
    const stored = sessionStorage.getItem('queryResults');
    if (stored) {
      try {
        const data: QueryResponse = JSON.parse(stored);
        const vehicleIndex = index ? parseInt(index, 10) : -1;
        const results = data.results || [];
        
        if (vehicleIndex >= 0 && vehicleIndex < results.length) {
          setVehicle(results[vehicleIndex]);
        } else {
          toast.error('Vehicle not found');
          navigate('/sourcing/candidates');
        }
      } catch (e) {
        console.error('Failed to parse stored results:', e);
        toast.error('Failed to load vehicle details');
        navigate('/sourcing/candidates');
      }
    } else {
      toast.error('No search results found');
      navigate('/sourcing/candidates');
    }
    setLoading(false);
  }, [index, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <LoadingSpinner size="md" />
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div className="min-h-screen bg-black py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <EmptyState
            icon={<ArrowLeft className="h-8 w-8" />}
            title="Vehicle not found"
            description="The requested vehicle could not be found."
            action={
              <button
                onClick={() => navigate('/sourcing/candidates')}
                className="bg-brand-gold text-black px-6 py-3 font-semibold rounded-lg hover:bg-brand-gold-light transition-colors"
              >
                Back to Results
              </button>
            }
          />
        </div>
      </div>
    );
  }

  const priceCents = vehicle.price_cents as number | undefined;
  const priceDollars = vehicle.price as number | undefined;
  
  const formatVehiclePrice = () => {
    if (priceCents !== undefined && priceCents !== null) {
      return formatPrice(priceCents);
    }
    if (priceDollars !== undefined && priceDollars !== null) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(priceDollars);
    }
    return 'Price not available';
  };

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/sourcing/candidates')}
          className="flex items-center space-x-2 text-brand-gold hover:opacity-80 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Results</span>
        </button>

        {/* Vehicle Header */}
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h1>
          {vehicle.trim && (
            <p className="text-gray-400 text-lg mb-4">{vehicle.trim}</p>
          )}
          <div className="flex items-center justify-between">
            <div className="text-3xl font-bold text-brand-gold">
              {formatVehiclePrice()}
            </div>
            <button
              onClick={() => {
                // TODO: Implement haggle functionality
                toast.success('Vehicle sent to sales team to negotiate on your behalf!');
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-brand-gold text-black font-semibold rounded-lg hover:opacity-80 transition-all"
            >
              <Handshake className="h-5 w-5" />
              <span>Haggle for me!</span>
            </button>
          </div>
        </div>

        {/* Vehicle Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Key Information */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Key Information</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Mileage:</span>
                <span className="text-white font-medium">{formatMileage(vehicle.mileage)}</span>
              </div>
              {vehicle.color && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Color:</span>
                  <span className="text-white font-medium capitalize">{vehicle.color}</span>
                </div>
              )}
              {vehicle.condition && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Condition:</span>
                  <span className="text-white font-medium capitalize">{vehicle.condition}</span>
                </div>
              )}
              {vehicle.drivetrain && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Drivetrain:</span>
                  <span className="text-white font-medium">{vehicle.drivetrain}</span>
                </div>
              )}
              {vehicle.body_style && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Body Style:</span>
                  <span className="text-white font-medium capitalize">{vehicle.body_style}</span>
                </div>
              )}
              {vehicle.fuel_type && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Fuel Type:</span>
                  <span className="text-white font-medium capitalize">{vehicle.fuel_type}</span>
                </div>
              )}
              {vehicle.number_of_owners !== undefined && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Number of Owners:</span>
                  <span className="text-white font-medium">{vehicle.number_of_owners}</span>
                </div>
              )}
            </div>
          </div>

          {/* Location & Contact */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Location</h2>
            <div className="space-y-3">
              {vehicle.city && (
                <div>
                  <span className="text-gray-400">Location:</span>
                  <p className="text-white font-medium">
                    {vehicle.city}
                    {vehicle.state_region ? `, ${vehicle.state_region}` : ''}
                    {vehicle.zip_code ? ` ${vehicle.zip_code}` : ''}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Features */}
          {vehicle.features && vehicle.features.length > 0 && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Features</h2>
              <div className="flex flex-wrap gap-2">
                {vehicle.features.map((feature, idx) => (
                  <span 
                    key={idx} 
                    className="px-3 py-1 bg-gray-800 text-gray-300 text-sm rounded capitalize"
                  >
                    {feature.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Use Cases */}
          {vehicle.use_case_tags && vehicle.use_case_tags.length > 0 && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Use Cases</h2>
              <div className="flex flex-wrap gap-2">
                {vehicle.use_case_tags.map((tag, idx) => (
                  <span 
                    key={idx} 
                    className="px-3 py-1 bg-blue-900/30 text-blue-300 text-sm rounded capitalize"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* VIN */}
          {vehicle.vin && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 md:col-span-2">
              <h2 className="text-xl font-semibold text-white mb-4">VIN</h2>
              <p className="text-white font-mono text-lg break-all">{vehicle.vin}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
