export interface StripePrice {
  id: string;
  amount: number;
  currency: string;
  interval?: 'month' | 'year' | null;
}

export const STRIPE_PRICES = {
  membership_setup: { amount: 150000, currency: 'usd' }, // $1,500
  membership_monthly: { amount: 15000, currency: 'usd', interval: 'month' }, // $150/month
  storage_standard_350: { amount: 35000, currency: 'usd', interval: 'month' }, // $350/month
  storage_pro_450: { amount: 45000, currency: 'usd', interval: 'month' }, // $450/month
  storage_pro_600: { amount: 60000, currency: 'usd', interval: 'month' }, // $600/month
  wash: { amount: 15000, currency: 'usd' }, // $150
  detail: { amount: 40000, currency: 'usd' }, // $400
  battery: { amount: 15000, currency: 'usd' }, // $150
  lift_rental: { amount: 5000, currency: 'usd' }, // $50
} as const;

export function formatPrice(amountCents: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amountCents / 100);
}

export function calculateConciergeTotal(data: {
  plan: 'standard' | 'pro';
  vehicles: Array<{ storage_tier: keyof typeof STRIPE_PRICES }>;
  addons?: Record<string, boolean>;
}): number {
  let total = STRIPE_PRICES.membership_setup.amount + STRIPE_PRICES.membership_monthly.amount;
  
  // Add vehicle storage costs
  data.vehicles.forEach(vehicle => {
    const tierPrice = STRIPE_PRICES[vehicle.storage_tier];
    if (tierPrice) {
      total += tierPrice.amount;
    }
  });

  // Add selected addons
  if (data.addons) {
    Object.entries(data.addons).forEach(([addon, selected]) => {
      if (selected && addon in STRIPE_PRICES) {
        total += STRIPE_PRICES[addon as keyof typeof STRIPE_PRICES].amount;
      }
    });
  }

  return total;
}