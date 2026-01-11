import { useEffect } from 'react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import { supabase } from '../../lib/supabase';
import { FormField } from '../../components/FormField';
import { SearchableDropdown } from '../../components/SearchableDropdown';
import { createCheckoutSession } from '../../lib/api';
import { formatPrice } from '../../lib/stripe';
import { EmptyState } from '../../components/EmptyState';
import { Wrench, Car } from 'lucide-react';
import toast from 'react-hot-toast';

const buildOrderSchema = z.object({
  vehicle_id: z.string().min(1, 'Please select a vehicle'),
  config: z.object({
    color: z.string().optional(),
    wheels: z.string().optional(),
    interior: z.string().optional(),
    performance: z.string().optional(),
  }).optional(),
  notes: z.string().optional(),
});

type BuildOrderForm = z.infer<typeof buildOrderSchema>;

export function NewBuildOrder() {
  const [selectedVehicle, setSelectedVehicle] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const { data: inventory, isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('vehicles')
        .select('*')
        .eq('source', 'inventory')
        .eq('available', true)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<BuildOrderForm>({
    resolver: zodResolver(buildOrderSchema),
  });

  const watchedVehicleId = watch('vehicle_id');

  // Update selected vehicle when form changes
  useEffect(() => {
    if (watchedVehicleId && inventory) {
      const vehicle = inventory.find((v: any) => v.id === watchedVehicleId);
      setSelectedVehicle(vehicle);
    } else {
      setSelectedVehicle(null);
    }
  }, [watchedVehicleId, inventory]);

  const onSubmit = async (data: BuildOrderForm) => {
    try {
      setLoading(true);
      const depositAmount = selectedVehicle?.price_cents ? Math.floor(selectedVehicle.price_cents * 0.1) : 500000; // 10% or $5,000 min

      const { url } = await createCheckoutSession({
        flow: 'build',
        data: {
          ...data,
          vehicle: selectedVehicle,
          deposit_amount_cents: depositAmount,
        },
      });
      window.location.href = url;
    } catch (error) {
      toast.error('Failed to process build order');
    } finally {
      setLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <Wrench className="h-12 w-12 text-brand-gold mx-auto mb-4" />
          <h1 className="text-3xl font-extrabold text-white">Custom Build Order</h1>
          <p className="mt-2 text-gray-400">
            Commission a custom build from our curated inventory
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Inventory Selection */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-brand-gold">Select Base Vehicle</h2>
            
            {!inventory || inventory.length === 0 ? (
              <EmptyState
                icon={<Car className="h-8 w-8" />}
                title="No inventory available"
                description="Please check back later for available vehicles."
              />
            ) : (
              <FormField
                label="Search and select a vehicle"
                required
                error={errors.vehicle_id?.message}
              >
                <SearchableDropdown
                  items={inventory}
                  selectedItem={selectedVehicle}
                  placeholder="Search by year, make, model..."
                  displayValue={(vehicle: any) => 
                    `${vehicle.year} ${vehicle.make} ${vehicle.model}${vehicle.trim ? ` ${vehicle.trim}` : ''}`
                  }
                  renderItem={(vehicle: any) => (
                    <div className="p-4 flex items-center space-x-4">
                      {vehicle.media && vehicle.media[0] && (
                        <img
                          src={vehicle.media[0].url}
                          alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                          className="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                        />
                      )}
                      
                      <div className="flex-1 min-w-0">
                        <h3 className="text-white font-semibold truncate">
                          {vehicle.year} {vehicle.make} {vehicle.model}
                        </h3>
                        {vehicle.trim && (
                          <p className="text-gray-400 text-sm truncate">{vehicle.trim}</p>
                        )}
                        <div className="mt-1 flex items-center justify-between">
                          <span className="text-brand-gold font-bold text-sm">
                            {vehicle.price_cents ? formatPrice(vehicle.price_cents) : 'Contact for pricing'}
                          </span>
                          <span className="text-gray-400 text-xs">
                            {vehicle.mileage ? `${vehicle.mileage.toLocaleString()} mi` : 'New'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                  onSelect={(vehicle: any) => {
                    setValue('vehicle_id', vehicle.id);
                    setSelectedVehicle(vehicle);
                  }}
                  error={errors.vehicle_id?.message}
                />
              </FormField>
            )}
          </div>

          {/* Configuration Form */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-brand-gold">Build Configuration</h2>
            
            <form onSubmit={handleSubmit(onSubmit)} className="bg-gray-900 border border-gray-700 rounded-lg p-6 space-y-6">
              {selectedVehicle && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-white font-semibold mb-2">
                    {selectedVehicle.year} {selectedVehicle.make} {selectedVehicle.model}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4">
                    {selectedVehicle.specs?.engine && `Engine: ${selectedVehicle.specs.engine}`}
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Base Price</span>
                    <span className="text-brand-gold font-bold">
                      {selectedVehicle.price_cents ? formatPrice(selectedVehicle.price_cents) : 'TBD'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-gray-400">Required Deposit (10%)</span>
                    <span className="text-white font-semibold">
                      {selectedVehicle.price_cents 
                        ? formatPrice(Math.floor(selectedVehicle.price_cents * 0.1))
                        : formatPrice(500000)
                      }
                    </span>
                  </div>
                </div>
              )}

              <FormField
                label="Custom Color"
                error={errors.config?.color?.message}
              >
                <input
                  {...register('config.color')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                  placeholder="Guards Red, Arctic Silver, etc."
                />
              </FormField>

              <FormField
                label="Wheel Package"
                error={errors.config?.wheels?.message}
              >
                <input
                  {...register('config.wheels')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                  placeholder="20 inch forged, beadlock, etc."
                />
              </FormField>

              <FormField
                label="Interior Package"
                error={errors.config?.interior?.message}
              >
                <input
                  {...register('config.interior')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                  placeholder="Carbon fiber, alcantara, custom stitching"
                />
              </FormField>

              <FormField
                label="Performance Modifications"
                error={errors.config?.performance?.message}
              >
                <input
                  {...register('config.performance')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                  placeholder="Exhaust, suspension, intake, etc."
                />
              </FormField>

              <FormField
                label="Additional Notes"
                error={errors.notes?.message}
              >
                <textarea
                  {...register('notes')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                  placeholder="Describe your vision for this build..."
                />
              </FormField>

              <button
                type="submit"
                disabled={loading || !selectedVehicle}
                className="w-full py-3 bg-brand-gold text-white font-semibold rounded-lg hover:opacity-80 transition-all disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Place Build Order'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
