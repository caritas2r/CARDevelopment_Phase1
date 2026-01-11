import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { supabase } from '../../lib/supabase';
import { useAuth } from '../../hooks/useAuth';
import { useStripePortal } from '../../hooks/useStripePortal';
import { StatusBadge } from '../../components/StatusBadge';
import { formatPrice } from '../../lib/stripe';
import { CreditCard, Download, ExternalLink, Calendar } from 'lucide-react';
import { format } from 'date-fns';

export function BillingPortal() {
  const { user } = useAuth();
  const { openPortal, loading: portalLoading } = useStripePortal();

  const { data: customer } = useQuery({
    queryKey: ['customer', user?.id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('customers')
        .select('*')
        .eq('user_id', user?.id)
        .single();
      
      if (error) throw error;
      return data;
    },
    enabled: !!user,
  });

  const { data: contracts } = useQuery({
    queryKey: ['customer-contracts', customer?.id],
    queryFn: async () => {
      if (!customer?.id) return [];
      
      const { data, error } = await supabase
        .from('concierge_contracts')
        .select(`
          *,
          concierge_contract_vehicles(
            id,
            price_tier,
            vehicles(year, make, model, trim)
          )
        `)
        .eq('customer_id', customer.id)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
    enabled: !!customer?.id,
  });

  const { data: payments } = useQuery({
    queryKey: ['customer-payments', customer?.id],
    queryFn: async () => {
      if (!customer?.id) return [];
      
      const { data, error } = await supabase
        .from('payments')
        .select('*')
        .eq('customer_id', customer.id)
        .order('created_at', { ascending: false })
        .limit(10);
      
      if (error) throw error;
      return data;
    },
    enabled: !!customer?.id,
  });

  const handleOpenPortal = () => {
    if (customer?.stripe_customer_id) {
      openPortal(customer.stripe_customer_id);
    }
  };

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <CreditCard className="h-12 w-12 text-brand-gold mx-auto mb-4" />
          <h1 className="text-3xl font-extrabold text-white">Billing & Subscriptions</h1>
          <p className="mt-2 text-gray-400">
            Manage your payments, subscriptions, and download receipts
          </p>
        </div>

        <div className="space-y-8">
          {/* Stripe Customer Portal */}
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-brand-gold">Customer Portal</h2>
                <p className="text-gray-400 text-sm mt-1">
                  Manage payment methods, view invoices, and update billing information
                </p>
              </div>
              <button
                onClick={handleOpenPortal}
                disabled={portalLoading || !customer?.stripe_customer_id}
                className="flex items-center space-x-2 px-4 py-2 bg-brand-gold text-white font-semibold rounded-lg hover:opacity-80 transition-all disabled:opacity-50"
              >
                <ExternalLink className="h-4 w-4" />
                <span>{portalLoading ? 'Opening...' : 'Open Portal'}</span>
              </button>
            </div>
          </div>

          {/* Active Subscriptions */}
          {contracts && contracts.length > 0 && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-brand-gold mb-4">Active Subscriptions</h2>
              <div className="space-y-4">
                {contracts.map((contract: any) => (
                  <div key={contract.id} className="border border-gray-600 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-white font-medium">
                        Royale Concierge - {contract.plan.toUpperCase()}
                      </h3>
                      <StatusBadge status={contract.status} />
                    </div>
                    <div className="text-sm text-gray-400 space-y-1">
                      <p>Location: {contract.location}</p>
                      <p>Vehicles: {contract.vehicles_count}</p>
                      <p>Started: {contract.created_at ? format(new Date(contract.created_at), 'MMM d, yyyy') : 'N/A'}</p>
                    </div>
                    {contract.concierge_contract_vehicles && (
                      <div className="mt-3">
                        <p className="text-sm text-gray-400 mb-2">Vehicle Storage Plans:</p>
                        <div className="space-y-1">
                          {contract.concierge_contract_vehicles.map((cv: any) => (
                            <div key={cv.id} className="flex justify-between text-sm">
                              <span className="text-white">
                                {cv.vehicles?.year} {cv.vehicles?.make} {cv.vehicles?.model}
                              </span>
                              <span className="text-brand-gold">
                                {cv.price_tier?.replace('_', ' ').toUpperCase()}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Payments */}
          {payments && payments.length > 0 && (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-brand-gold mb-4">Recent Payments</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-700">
                  <thead>
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-brand-gold uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-brand-gold uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-brand-gold uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-brand-gold uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {payments.map((payment: any) => (
                      <tr key={payment.id} className="hover:bg-gray-800 transition-colors">
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white">
                          {payment.created_at ? format(new Date(payment.created_at), 'MMM d, yyyy') : 'N/A'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white">
                          {payment.object_type ? payment.object_type.replace('_', ' ').toUpperCase() : 'N/A'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-white">
                          {payment.amount_cents ? formatPrice(payment.amount_cents) : 'N/A'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {payment.status ? <StatusBadge status={payment.status} /> : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
