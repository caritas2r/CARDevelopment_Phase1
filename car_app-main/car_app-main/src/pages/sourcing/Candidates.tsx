import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { StatusBadge } from '../../components/StatusBadge';
import { EmptyState } from '../../components/EmptyState';
import { Search, Star, Plus, Handshake } from 'lucide-react';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import toast from 'react-hot-toast';
import { QueryResponse, VehicleResult } from '../../lib/api';
import { submitQueryFeedback } from '../../lib/api';
import { formatPrice } from '../../lib/stripe';

function formatMileage(mileage?: number): string {
  if (!mileage) return 'Mileage not specified';
  return `${mileage.toLocaleString()} mi`;
}

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPaymentSelect: (type: 'single' | 'all') => void;
  vehicleIndex: number;
  totalResults: number;
}

function PaymentModal({ isOpen, onClose, onPaymentSelect, vehicleIndex, totalResults }: PaymentModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md w-full" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-xl font-bold text-white mb-4">Unlock Vehicle Details</h2>
        <p className="text-gray-400 mb-6">
          Choose how you'd like to unlock the vehicle information:
        </p>
        <div className="space-y-3">
          <button
            onClick={() => onPaymentSelect('single')}
            className="w-full p-4 bg-gray-800 border border-gray-600 rounded-lg hover:border-brand-gold hover:bg-gray-700 transition-all text-left"
          >
            <div className="flex justify-between items-center">
              <div>
                <div className="text-white font-semibold">Unlock This Vehicle</div>
                <div className="text-gray-400 text-sm">View details for vehicle #{vehicleIndex + 1}</div>
              </div>
              <div className="text-brand-gold text-lg font-bold">$1.99</div>
            </div>
          </button>
          <button
            onClick={() => onPaymentSelect('all')}
            className="w-full p-4 bg-gray-800 border border-gray-600 rounded-lg hover:border-brand-gold hover:bg-gray-700 transition-all text-left"
          >
            <div className="flex justify-between items-center">
              <div>
                <div className="text-white font-semibold">Unlock All Vehicles</div>
                <div className="text-gray-400 text-sm">View details for all {totalResults} results</div>
              </div>
              <div className="text-brand-gold text-lg font-bold">$9.99</div>
            </div>
          </button>
        </div>
        <button
          onClick={onClose}
          className="w-full mt-4 px-4 py-2 text-sm border border-gray-600 text-gray-300 rounded-lg hover:border-gray-500 hover:text-white transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

export function SourcingCandidates() {
  const navigate = useNavigate();
  const [results, setResults] = useState<VehicleResult[]>([]);
  const [queryData, setQueryData] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [paidVehicles, setPaidVehicles] = useState<Set<number>>(new Set());
  const [allVehiclesPaid, setAllVehiclesPaid] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [paymentModal, setPaymentModal] = useState<{ isOpen: boolean; vehicleIndex: number }>({ isOpen: false, vehicleIndex: 0 });

  useEffect(() => {
    // Load results from sessionStorage (set by NewRequest)
    const stored = sessionStorage.getItem('queryResults');
    if (stored) {
      try {
        const data: QueryResponse = JSON.parse(stored);
        setQueryData(data);
        setResults(data.results || []);
        // Load payment state from sessionStorage
        const paidState = sessionStorage.getItem('paidVehicles');
        if (paidState) {
          const parsed = JSON.parse(paidState);
          if (parsed.all) {
            setAllVehiclesPaid(true);
          } else if (parsed.vehicles && Array.isArray(parsed.vehicles)) {
            setPaidVehicles(new Set(parsed.vehicles));
          }
        }
      } catch (e) {
        console.error('Failed to parse stored results:', e);
        toast.error('Failed to load results');
      }
    }
    setLoading(false);
  }, []);

  const handleVehicleClick = (index: number) => {
    // If already paid, navigate to detail page
    if (allVehiclesPaid || paidVehicles.has(index)) {
      navigate(`/sourcing/vehicle/${index}`);
      return;
    }
    // Otherwise open payment modal
    setPaymentModal({ isOpen: true, vehicleIndex: index });
  };

  const handlePaymentSelect = async (type: 'single' | 'all') => {
    setPaymentModal({ isOpen: false, vehicleIndex: 0 });
    // Navigate to payment page with selection
    sessionStorage.setItem('paymentType', type);
    sessionStorage.setItem('paymentVehicleIndex', paymentModal.vehicleIndex.toString());
    navigate('/sourcing/payment');
  };

  const handleNewSearch = () => {
    sessionStorage.removeItem('queryResults');
    navigate('/sourcing');
  };

  const handleOpenFeedbackModal = () => {
    setShowFeedbackModal(true);
    setFeedbackText('');
  };

  const handleCloseFeedbackModal = () => {
    setShowFeedbackModal(false);
    setFeedbackText('');
  };

  const handleSubmitFeedback = async () => {
    if (!queryData) return;

    try {
      await submitQueryFeedback({
        query: queryData.query || '',
        extracted_fields: queryData.extracted_fields,
        sql_query: queryData.sql_query,
        sql_params: queryData.sql_params,
        reason: feedbackText.trim() || '',
        success: queryData.success,
        result_count: queryData.result_count,
      });
      toast.success('Feedback submitted successfully');
      handleCloseFeedbackModal();
    } catch (error: any) {
      console.error('Feedback error:', error);
      toast.error(`Failed to submit feedback: ${error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <LoadingSpinner size="md" />
      </div>
    );
  }

  if (!queryData || !results || results.length === 0) {
    return (
      <div className="min-h-screen bg-black py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <EmptyState
            icon={<Search className="h-8 w-8" />}
            title="No search results"
            description="Start by submitting a vehicle search query."
            action={
              <button
                onClick={handleNewSearch}
                className="bg-brand-gold text-black px-6 py-3 font-semibold rounded-lg hover:bg-brand-gold-light transition-colors"
              >
                New Search
              </button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-extrabold text-white mb-2">Search Results</h1>
              <p className="text-gray-400">
                Query: <span className="text-white">"{queryData.query}"</span>
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleOpenFeedbackModal}
                className="px-4 py-2 text-sm border border-gray-600 text-gray-300 rounded-lg hover:border-brand-gold hover:text-brand-gold transition-colors"
              >
                Results Not Satisfactory
              </button>
              <button
                onClick={handleNewSearch}
                className="flex items-center space-x-2 px-4 py-2 bg-brand-gold text-black font-semibold rounded-lg hover:opacity-80 transition-all"
              >
                <Plus className="h-4 w-4" />
                <span>New Search</span>
              </button>
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Results Found:</span>
              <span className="text-white font-semibold">{queryData.result_count || 0}</span>
            </div>
            {queryData.total_result_count !== undefined && queryData.total_result_count > (queryData.result_count || 0) && (
              <div className="mt-2 pt-2 border-t border-gray-700 flex items-center justify-between">
                <span className="text-gray-400">Total Matches:</span>
                <span className="text-brand-gold font-semibold">{queryData.total_result_count}</span>
                <span className="text-gray-500 text-xs">(showing first {queryData.result_count})</span>
              </div>
            )}
          </div>
        </div>

        {/* Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((vehicle, index) => {
            // Check if this specific vehicle has been paid for
            const isPaid = allVehiclesPaid || paidVehicles.has(index);
            const isLocationBlurred = !isPaid;
            // Extract price - handle both price_cents (in cents) and price (in dollars)
            const priceCents = vehicle.price_cents as number | undefined;
            const priceDollars = vehicle.price as number | undefined;
            
            // Format price: if price_cents exists, it's in cents; otherwise if price exists, it's in dollars
            const formatVehiclePrice = () => {
              if (priceCents !== undefined && priceCents !== null) {
                return formatPrice(priceCents); // formatPrice divides by 100 for cents
              }
              if (priceDollars !== undefined && priceDollars !== null) {
                // Price is already in dollars, format directly
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
              <div 
                key={index} 
                onClick={() => handleVehicleClick(index)}
                className={`bg-gray-900 border border-gray-700 rounded-lg overflow-hidden transition-all group relative cursor-pointer hover:border-brand-gold`}
              >
                {/* Card Header */}
                <div className="p-5 border-b border-gray-700">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Star className="h-4 w-4 text-brand-gold fill-current" />
                      <span className="text-brand-gold font-semibold text-sm">#{index + 1}</span>
                    </div>
                    {vehicle.condition && (
                      <StatusBadge status={vehicle.condition} />
                    )}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">
                    {vehicle.year} {vehicle.make} {vehicle.model}
                  </h3>
                  {vehicle.trim && (
                    <p className="text-gray-400 text-sm">{vehicle.trim}</p>
                  )}
                </div>

                {/* Price - Prominent */}
                <div className="px-5 py-4 bg-gray-800/50">
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold text-brand-gold">
                      {formatVehiclePrice()}
                    </div>
                    {isPaid && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // TODO: Implement haggle functionality
                          toast.success('Vehicle sent to sales team to negotiate on your behalf!');
                        }}
                        className="flex items-center space-x-2 px-3 py-1.5 bg-brand-gold text-black text-sm font-semibold rounded-lg hover:opacity-80 transition-all"
                      >
                        <Handshake className="h-4 w-4" />
                        <span>Haggle for me!</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Key Details */}
                <div className="p-5 space-y-3">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-gray-400">Mileage:</span>
                      <p className="text-white font-medium">{formatMileage(vehicle.mileage)}</p>
                    </div>
                    {vehicle.color && (
                      <div>
                        <span className="text-gray-400">Color:</span>
                        <p className="text-white font-medium capitalize">{vehicle.color}</p>
                      </div>
                    )}
                  </div>

                  {/* Additional Specs - Compact */}
                  <div className="pt-3 border-t border-gray-700 space-y-2">
                    {vehicle.drivetrain && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Drivetrain:</span>
                        <span className="text-white">{vehicle.drivetrain}</span>
                      </div>
                    )}
                    {vehicle.body_style && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Body Style:</span>
                        <span className="text-white capitalize">{vehicle.body_style}</span>
                      </div>
                    )}
                    {vehicle.fuel_type && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Fuel Type:</span>
                        <span className="text-white capitalize">{vehicle.fuel_type}</span>
                      </div>
                    )}
                    {vehicle.number_of_owners !== undefined && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Owners:</span>
                        <span className="text-white">{vehicle.number_of_owners}</span>
                      </div>
                    )}
                    {vehicle.city && (
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Location:</span>
                        <span 
                          className={`text-white ${isLocationBlurred ? 'blur-sm select-none' : ''}`}
                          style={isLocationBlurred ? { filter: 'blur(4px)' } : {}}
                        >
                          {vehicle.city}{vehicle.state_region ? `, ${vehicle.state_region}` : ''}
                          {vehicle.zip_code ? ` ${vehicle.zip_code}` : ''}
                        </span>
                      </div>
                    )}
                    {/* Vehicle Link */}
                    <div className="flex justify-between text-sm pt-2 border-t border-gray-700">
                      <span className="text-gray-400">Vehicle Link:</span>
                      {isPaid ? (
                        <a
                          href={`/sourcing/vehicle/${index}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/sourcing/vehicle/${index}`);
                          }}
                          className="text-brand-gold hover:underline"
                        >
                          See This Vehicle
                        </a>
                      ) : (
                        <span className="text-gray-500">See This Vehicle</span>
                      )}
                    </div>
                  </div>

                  {/* Features - Compact Tags */}
                  {vehicle.features && vehicle.features.length > 0 && (
                    <div className="pt-3 border-t border-gray-700">
                      <p className="text-xs text-gray-400 mb-2">Features</p>
                      <div className="flex flex-wrap gap-1.5">
                        {vehicle.features.slice(0, 4).map((feature, idx) => (
                          <span 
                            key={idx} 
                            className="px-2 py-0.5 bg-gray-800 text-gray-300 text-xs rounded capitalize"
                            title={feature}
                          >
                            {feature.replace(/_/g, ' ')}
                          </span>
                        ))}
                        {vehicle.features.length > 4 && (
                          <span className="px-2 py-0.5 bg-gray-800 text-gray-400 text-xs rounded">
                            +{vehicle.features.length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Use Cases - Compact */}
                  {vehicle.use_case_tags && vehicle.use_case_tags.length > 0 && (
                    <div className="pt-2">
                      <div className="flex flex-wrap gap-1.5">
                        {vehicle.use_case_tags.map((tag, idx) => (
                          <span 
                            key={idx} 
                            className="px-2 py-0.5 bg-blue-900/30 text-blue-300 text-xs rounded capitalize"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* VIN - Compact */}
                  {vehicle.vin && (
                    <div className="pt-2 border-t border-gray-700">
                      <p className="text-xs text-gray-400 mb-1">VIN</p>
                      <p className="text-white font-mono text-xs break-all">{vehicle.vin}</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Payment Modal */}
      <PaymentModal
        isOpen={paymentModal.isOpen}
        onClose={() => setPaymentModal({ isOpen: false, vehicleIndex: 0 })}
        onPaymentSelect={handlePaymentSelect}
        vehicleIndex={paymentModal.vehicleIndex}
        totalResults={results.length}
      />

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold text-white mb-4">Feedback</h2>
            <p className="text-gray-400 mb-4">
              Why were the results not satisfactory? (Optional)
            </p>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent resize-none"
              placeholder="Enter your feedback here..."
              autoFocus
            />
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={handleCloseFeedbackModal}
                className="px-4 py-2 text-sm border border-gray-600 text-gray-300 rounded-lg hover:border-gray-500 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitFeedback}
                className="px-4 py-2 text-sm bg-brand-gold text-black font-semibold rounded-lg hover:opacity-80 transition-all"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
