import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import { supabase } from '../../lib/supabase';
import { FormField } from '../../components/FormField';
import { createCheckoutSession } from '../../lib/api';
import { STRIPE_PRICES, formatPrice } from '../../lib/stripe';
import { Calendar, Car } from 'lucide-react';
import toast from 'react-hot-toast';

const serviceSchema = z.object({
  vehicle_id: z.string().min(1, 'Please select a vehicle'),
  service_type: z.enum(['wash', 'detail', 'battery', 'lift_rental']),
  service_name: z.string().min(1, 'Service name is required'),
  scheduled_at: z.string().optional(),
  notes: z.string().optional(),
});

type ServiceForm = z.infer<typeof serviceSchema>;

const serviceTypes = [
  { 
    key: 'wash', 
    name: 'Premium Wash', 
    description: 'Complete exterior and interior cleaning',
    price: STRIPE_PRICES.wash.amount 
  },
  { 
    key: 'detail', 
    name: 'Full Detail', 
    description: 'Comprehensive detailing inside and out',
    price: STRIPE_PRICES.detail.amount 
  },
  { 
    key: 'battery', 
    name: 'Battery Maintenance', 
    description: 'Battery health check and conditioning',
    price: STRIPE_PRICES.battery.amount 
  },
  { 
    key: 'lift_rental', 
    name: 'Lift Rental', 
    description: 'Access to service lift for maintenance',
    price: STRIPE_PRICES.lift_rental.amount 
  },
];

export function ConciergeServices() {
  const [loading, setLoading] = useState(false);

  const { data: vehicles } = useQuery({
    queryKey: ['customer-vehicles'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('vehicles')
        .select('*')
        .eq('source', 'external')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ServiceForm>({
    resolver: zodResolver(serviceSchema),
  });

  const selectedServiceType = watch('service_type');
  const selectedService = serviceTypes.find(s => s.key === selectedServiceType);

  const onSubmit = async (data: ServiceForm) => {
    try {
      setLoading(true);
      const { url } = await createCheckoutSession({
        flow: 'service',
        data: {
          ...data,
          price_cents: selectedService?.price || 0,
          service_description: selectedService?.description,
        },
      });
      window.location.href = url;
    } catch (error) {
      toast.error('Failed to process service booking');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <Calendar className="h-12 w-12 text-brand-gold mx-auto mb-4" />
          <h1 className="text-3xl font-extrabold text-white">Schedule Service</h1>
          <p className="mt-2 text-gray-400">
            Book premium services for your vehicles
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="bg-gray-900 border border-gray-700 rounded-lg p-6 space-y-6">
          <FormField
            label="Select Vehicle"
            required
            error={errors.vehicle_id?.message}
          >
            <select
              {...register('vehicle_id')}
              className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
            >
              <option value="">Choose a vehicle</option>
              {vehicles?.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.year} {vehicle.make} {vehicle.model} {vehicle.trim}
                </option>
              ))}
            </select>
          </FormField>

          <FormField
            label="Service Type"
            required
            error={errors.service_type?.message}
          >
            <div className="grid grid-cols-1 gap-3">
              {serviceTypes.map((service) => (
                <label
                  key={service.key}
                  className="flex items-center justify-between p-4 border border-gray-600 rounded-lg cursor-pointer hover:border-brand-gold transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <input
                      {...register('service_type')}
                      type="radio"
                      value={service.key}
                      className="text-brand-gold focus:ring-brand-gold"
                    />
                    <div>
                      <span className="text-white font-medium">{service.name}</span>
                      <p className="text-gray-400 text-sm">{service.description}</p>
                    </div>
                  </div>
                  <span className="text-brand-gold font-semibold">
                    {formatPrice(service.price)}
                  </span>
                </label>
              ))}
            </div>
          </FormField>

          <FormField
            label="Preferred Date & Time"
            error={errors.scheduled_at?.message}
          >
            <input
              {...register('scheduled_at')}
              type="datetime-local"
              className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
            />
          </FormField>

          <FormField
            label="Special Instructions"
            error={errors.notes?.message}
          >
            <textarea
              {...register('notes')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
              placeholder="Any special requests or notes for our team..."
            />
          </FormField>

          {selectedService && (
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-white font-medium">Total</span>
                <span className="text-brand-gold text-xl font-bold">
                  {formatPrice(selectedService.price)}
                </span>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !selectedService}
            className="w-full py-3 bg-brand-gold text-white font-semibold rounded-lg hover:opacity-80 transition-all disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Book Service'}
          </button>
        </form>
      </div>
    </div>
  );
}
