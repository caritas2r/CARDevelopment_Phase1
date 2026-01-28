import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { FormField } from '../../components/FormField';
import { FormStepper } from '../../components/FormStepper';
import { createCheckoutSession } from '../../lib/api';
import { STRIPE_PRICES, calculateConciergeTotal, formatPrice } from '../../lib/stripe';
import { Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

const vehicleSchema = z.object({
  make: z.string().min(1, 'Make is required'),
  model: z.string().min(1, 'Model is required'),
  year: z.number().min(1900).max(new Date().getFullYear() + 2),
  trim: z.string().optional(),
  color: z.string().optional(),
  vin: z.string().optional(),
  storage_tier: z.enum(['storage_standard_350', 'storage_pro_450', 'storage_pro_600']),
});

const conciergeSchema = z.object({
  // Contact Info
  full_name: z.string().min(1, 'Full name is required'),
  email: z.string().email('Valid email is required'),
  phone: z.string().min(1, 'Phone number is required'),
  address_line1: z.string().min(1, 'Address is required'),
  address_line2: z.string().optional(),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(1, 'State is required'),
  zip: z.string().min(1, 'ZIP code is required'),
  
  // Service Details
  location: z.string().min(1, 'Storage location is required'),
  plan: z.enum(['standard', 'pro']),
  vehicles: z.array(vehicleSchema).min(1, 'At least one vehicle is required'),
  
  // Add-ons
  addons: z.object({
    wash: z.boolean().default(false),
    detail: z.boolean().default(false),
    battery: z.boolean().default(false),
    lift_rental: z.boolean().default(false),
  }).optional(),
  
  // Agreement
  agreement: z.boolean().refine((val) => val === true, 'You must agree to the terms'),
});

type ConciergeForm = z.infer<typeof conciergeSchema>;

const steps = [
  { id: 'contact', name: 'Contact', description: 'Personal information' },
  { id: 'vehicles', name: 'Vehicles', description: 'Vehicle details' },
  { id: 'services', name: 'Services', description: 'Plans & add-ons' },
  { id: 'review', name: 'Review', description: 'Confirm & pay' },
];

const storageLocations = [
  'Beverly Hills, CA',
  'Newport Beach, CA',
  'Scottsdale, AZ',
  'Austin, TX',
  'Miami, FL',
];

export function ConciergeEnroll() {
  const [currentStep, setCurrentStep] = useState('contact');
  const [loading, setLoading] = useState(false);

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ConciergeForm>({
    resolver: zodResolver(conciergeSchema),
    defaultValues: {
      plan: 'pro',
      vehicles: [{ 
        make: '', 
        model: '', 
        year: new Date().getFullYear(), 
        storage_tier: 'storage_pro_450' 
      }],
      addons: {
        wash: false,
        detail: false,
        battery: false,
        lift_rental: false,
      },
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'vehicles',
  });

  const watchedData = watch();

  const nextStep = () => {
    const stepOrder = ['contact', 'vehicles', 'services', 'review'];
    const currentIndex = stepOrder.indexOf(currentStep);
    if (currentIndex < stepOrder.length - 1) {
      setCurrentStep(stepOrder[currentIndex + 1]);
    }
  };

  const prevStep = () => {
    const stepOrder = ['contact', 'vehicles', 'services', 'review'];
    const currentIndex = stepOrder.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(stepOrder[currentIndex - 1]);
    }
  };

  const onSubmit = async (data: ConciergeForm) => {
    try {
      setLoading(true);
      const { url } = await createCheckoutSession({
        flow: 'concierge',
        data,
      });
      window.location.href = url;
    } catch (error) {
      toast.error('Failed to process enrollment');
    } finally {
      setLoading(false);
    }
  };

  const totalAmount = calculateConciergeTotal({
    plan: watchedData.plan,
    vehicles: watchedData.vehicles || [],
    addons: watchedData.addons,
  });

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-white">Royale Concierge Enrollment</h1>
          <p className="mt-2 text-gray-400">
            Join our exclusive white-glove storage and maintenance program
          </p>
        </div>

        <FormStepper steps={steps} currentStep={currentStep} />

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-6">
            {currentStep === 'contact' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-yellow-400">Contact Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    label="Full Name"
                    required
                    error={errors.full_name?.message}
                  >
                    <input
                      {...register('full_name')}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="John Smith"
                    />
                  </FormField>

                  <FormField
                    label="Email"
                    required
                    error={errors.email?.message}
                  >
                    <input
                      {...register('email')}
                      type="email"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="john@example.com"
                    />
                  </FormField>

                  <FormField
                    label="Phone"
                    required
                    error={errors.phone?.message}
                  >
                    <input
                      {...register('phone')}
                      type="tel"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="(555) 123-4567"
                    />
                  </FormField>

                  <FormField
                    label="Storage Location"
                    required
                    error={errors.location?.message}
                  >
                    <select
                      {...register('location')}
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                    >
                      <option value="">Select location</option>
                      {storageLocations.map((location) => (
                        <option key={location} value={location}>
                          {location}
                        </option>
                      ))}
                    </select>
                  </FormField>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    label="Address Line 1"
                    required
                    error={errors.address_line1?.message}
                  >
                    <input
                      {...register('address_line1')}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="123 Main Street"
                    />
                  </FormField>

                  <FormField
                    label="Address Line 2"
                    error={errors.address_line2?.message}
                  >
                    <input
                      {...register('address_line2')}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="Apt, Suite, etc."
                    />
                  </FormField>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <FormField
                    label="City"
                    required
                    error={errors.city?.message}
                  >
                    <input
                      {...register('city')}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="Los Angeles"
                    />
                  </FormField>

                  <FormField
                    label="State"
                    required
                    error={errors.state?.message}
                  >
                    <input
                      {...register('state')}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="CA"
                    />
                  </FormField>

                  <FormField
                    label="ZIP Code"
                    required
                    error={errors.zip?.message}
                  >
                    <input
                      {...register('zip')}
                      type="text"
                      className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      placeholder="90210"
                    />
                  </FormField>
                </div>
              </div>
            )}

            {currentStep === 'vehicles' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-brand-gold">Vehicle Information</h3>
                  <button
                    type="button"
                    onClick={() => append({ 
                      make: '', 
                      model: '', 
                      year: new Date().getFullYear(), 
                      storage_tier: 'storage_pro_450' 
                    })}
                    className="flex items-center space-x-2 text-brand-gold hover:opacity-80 transition-all"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add Vehicle</span>
                  </button>
                </div>

                {fields.map((field, index) => (
                  <div key={field.id} className="border border-gray-700 rounded-lg p-4 space-y-4">
                    <div className="flex justify-between items-center">
                      <h4 className="font-medium text-white">Vehicle {index + 1}</h4>
                      {fields.length > 1 && (
                        <button
                          type="button"
                          onClick={() => remove(index)}
                          className="text-red-400 hover:text-red-300 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <FormField
                        label="Make"
                        required
                        error={errors.vehicles?.[index]?.make?.message}
                      >
                        <input
                          {...register(`vehicles.${index}.make` as const)}
                          type="text"
                          className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                          placeholder="Porsche"
                        />
                      </FormField>

                      <FormField
                        label="Model"
                        required
                        error={errors.vehicles?.[index]?.model?.message}
                      >
                        <input
                          {...register(`vehicles.${index}.model` as const)}
                          type="text"
                          className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                          placeholder="911"
                        />
                      </FormField>

                      <FormField
                        label="Year"
                        required
                        error={errors.vehicles?.[index]?.year?.message}
                      >
                        <input
                          {...register(`vehicles.${index}.year` as const, { valueAsNumber: true })}
                          type="number"
                          className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                          placeholder="2024"
                        />
                      </FormField>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <FormField
                        label="Trim"
                        error={errors.vehicles?.[index]?.trim?.message}
                      >
                        <input
                          {...register(`vehicles.${index}.trim` as const)}
                          type="text"
                          className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                          placeholder="Carrera S"
                        />
                      </FormField>

                      <FormField
                        label="Color"
                        error={errors.vehicles?.[index]?.color?.message}
                      >
                        <input
                          {...register(`vehicles.${index}.color` as const)}
                          type="text"
                          className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                          placeholder="Guards Red"
                        />
                      </FormField>

                      <FormField
                        label="VIN (Optional)"
                        error={errors.vehicles?.[index]?.vin?.message}
                      >
                        <input
                          {...register(`vehicles.${index}.vin` as const)}
                          type="text"
                          className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                          placeholder="WP0AB2A99NS101234"
                        />
                      </FormField>
                    </div>

                    <FormField
                      label="Storage Tier"
                      required
                      error={errors.vehicles?.[index]?.storage_tier?.message}
                    >
                      <select
                        {...register(`vehicles.${index}.storage_tier` as const)}
                        className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                      >
                        <option value="storage_standard_350">
                          Standard - {formatPrice(STRIPE_PRICES.storage_standard_350.amount)}/month
                        </option>
                        <option value="storage_pro_450">
                          Pro - {formatPrice(STRIPE_PRICES.storage_pro_450.amount)}/month
                        </option>
                        <option value="storage_pro_600">
                          Pro Premium - {formatPrice(STRIPE_PRICES.storage_pro_600.amount)}/month
                        </option>
                      </select>
                    </FormField>
                  </div>
                ))}
              </div>
            )}

            {currentStep === 'services' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-brand-gold">Service Plan & Add-ons</h3>
                
                <FormField
                  label="Membership Plan"
                  required
                >
                  <div className="space-y-3">
                    <label className="flex items-center space-x-3 cursor-pointer">
                      <input
                        {...register('plan')}
                        type="radio"
                        value="standard"
                        className="text-brand-gold focus:ring-brand-gold focus:ring-2"
                      />
                      <div>
                        <span className="text-white font-medium">Standard Plan</span>
                        <p className="text-gray-400 text-sm">Essential storage and basic maintenance</p>
                      </div>
                    </label>
                    
                    <label className="flex items-center space-x-3 cursor-pointer">
                      <input
                        {...register('plan')}
                        type="radio"
                        value="pro"
                        className="text-brand-gold focus:ring-brand-gold focus:ring-2"
                      />
                      <div>
                        <span className="text-white font-medium">Pro Plan</span>
                        <p className="text-gray-400 text-sm">Premium storage with comprehensive maintenance and concierge services</p>
                      </div>
                    </label>
                  </div>
                </FormField>

                <div className="border-t border-gray-700 pt-6">
                  <h4 className="text-md font-semibold text-white mb-4">Optional Add-on Services</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <label className="flex items-center justify-between p-3 border border-gray-600 rounded-lg cursor-pointer hover:border-brand-gold transition-colors">
                      <div>
                        <span className="text-white font-medium">Monthly Wash</span>
                        <p className="text-gray-400 text-sm">{formatPrice(STRIPE_PRICES.wash.amount)}</p>
                      </div>
                      <input
                        {...register('addons.wash')}
                        type="checkbox"
                        className="text-brand-gold focus:ring-brand-gold rounded"
                      />
                    </label>

                    <label className="flex items-center justify-between p-3 border border-gray-600 rounded-lg cursor-pointer hover:border-brand-gold transition-colors">
                      <div>
                        <span className="text-white font-medium">Full Detail</span>
                        <p className="text-gray-400 text-sm">{formatPrice(STRIPE_PRICES.detail.amount)}</p>
                      </div>
                      <input
                        {...register('addons.detail')}
                        type="checkbox"
                        className="text-brand-gold focus:ring-brand-gold rounded"
                      />
                    </label>

                    <label className="flex items-center justify-between p-3 border border-gray-600 rounded-lg cursor-pointer hover:border-brand-gold transition-colors">
                      <div>
                        <span className="text-white font-medium">Battery Maintenance</span>
                        <p className="text-gray-400 text-sm">{formatPrice(STRIPE_PRICES.battery.amount)}</p>
                      </div>
                      <input
                        {...register('addons.battery')}
                        type="checkbox"
                        className="text-brand-gold focus:ring-brand-gold rounded"
                      />
                    </label>

                    <label className="flex items-center justify-between p-3 border border-gray-600 rounded-lg cursor-pointer hover:border-brand-gold transition-colors">
                      <div>
                        <span className="text-white font-medium">Lift Rental Access</span>
                        <p className="text-gray-400 text-sm">{formatPrice(STRIPE_PRICES.lift_rental.amount)}</p>
                      </div>
                      <input
                        {...register('addons.lift_rental')}
                        type="checkbox"
                        className="text-brand-gold focus:ring-brand-gold rounded"
                      />
                    </label>
                  </div>
                </div>
              </div>
            )}

            {currentStep === 'review' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-brand-gold">Review & Payment</h3>
                
                <div className="bg-gray-800 rounded-lg p-6 space-y-4">
                  <h4 className="font-semibold text-white">Order Summary</h4>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Setup Fee</span>
                      <span className="text-white">{formatPrice(STRIPE_PRICES.membership_setup.amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Monthly Membership</span>
                      <span className="text-white">{formatPrice(STRIPE_PRICES.membership_monthly.amount)}/month</span>
                    </div>
                    
                    {watchedData.vehicles?.map((vehicle, index) => (
                      <div key={index} className="flex justify-between">
                        <span className="text-gray-400">
                          {vehicle.year} {vehicle.make} {vehicle.model} Storage
                        </span>
                        <span className="text-white">
                          {formatPrice(STRIPE_PRICES[vehicle.storage_tier].amount)}/month
                        </span>
                      </div>
                    ))}

                    {watchedData.addons && Object.entries(watchedData.addons).map(([addon, selected]) => {
                      if (selected && addon in STRIPE_PRICES) {
                        return (
                          <div key={addon} className="flex justify-between">
                            <span className="text-gray-400">
                              {addon.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className="text-white">
                              {formatPrice(STRIPE_PRICES[addon as keyof typeof STRIPE_PRICES].amount)}
                            </span>
                          </div>
                        );
                      }
                      return null;
                    })}

                    <div className="border-t border-gray-600 pt-2 flex justify-between font-semibold">
                      <span className="text-white">Total (First Payment)</span>
                      <span className="text-brand-gold">{formatPrice(totalAmount)}</span>
                    </div>
                  </div>
                </div>

                <FormField
                  label="Terms & Agreement"
                  required
                  error={errors.agreement?.message}
                >
                  <label className="flex items-start space-x-3 cursor-pointer">
                    <input
                      {...register('agreement')}
                      type="checkbox"
                      className="mt-1 text-brand-gold focus:ring-brand-gold rounded"
                    />
                    <span className="text-gray-300 text-sm">
                      I agree to the{' '}
                      <a href="#" className="text-brand-gold hover:opacity-80">
                        Concierge Service Agreement
                      </a>{' '}
                      and{' '}
                      <a href="#" className="text-brand-gold hover:opacity-80">
                        Terms of Service
                      </a>
                    </span>
                  </label>
                </FormField>
              </div>
            )}
          </div>

          {/* Pricing Summary (sticky on mobile) */}
          <div className="lg:fixed lg:top-20 lg:right-6 lg:w-80 bg-gray-900 border border-gray-700 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-brand-gold mb-4">Pricing Summary</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Monthly Recurring</span>
                <span className="text-white">
                  {formatPrice(
                    STRIPE_PRICES.membership_monthly.amount +
                    (watchedData.vehicles?.reduce((sum, vehicle) => 
                      sum + STRIPE_PRICES[vehicle.storage_tier].amount, 0) || 0)
                  )}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">First Payment</span>
                <span className="text-brand-gold font-semibold">
                  {formatPrice(totalAmount)}
                </span>
              </div>
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <button
              type="button"
              onClick={prevStep}
              disabled={currentStep === 'contact'}
              className="px-6 py-2 border border-gray-600 text-gray-300 rounded-lg hover:border-brand-gold hover:text-brand-gold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            {currentStep === 'review' ? (
              <button
                type="submit"
                disabled={loading}
                className="px-8 py-2 bg-brand-gold text-white font-semibold rounded-lg hover:opacity-80 transition-all disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Complete Enrollment'}
              </button>
            ) : (
              <button
                type="button"
                onClick={nextStep}
                className="px-6 py-2 bg-brand-gold text-white font-semibold rounded-lg hover:opacity-80 transition-all"
              >
                Next
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
