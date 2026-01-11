export interface Profile {
  id: string;
  role: 'customer' | 'admin';
  full_name: string | null;
  phone: string | null;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: string;
  user_id: string | null;
  email: string;
  phone: string | null;
  full_name: string | null;
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state: string | null;
  zip: string | null;
  stripe_customer_id: string | null;
  ghl_contact_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Vehicle {
  id: string;
  owner_customer_id: string | null;
  source: 'inventory' | 'external';
  make: string;
  model: string;
  year: number;
  trim: string | null;
  vin: string | null;
  color: string | null;
  mileage: number | null;
  price_cents: number | null;
  media: any[];
  options: Record<string, any>;
  specs: Record<string, any>;
  available: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConciergeContract {
  id: string;
  customer_id: string;
  location: string;
  plan: 'standard' | 'pro';
  vehicles_count: number;
  membership_active: boolean;
  agreement_url: string | null;
  status: 'intake' | 'active' | 'suspended' | 'canceled';
  stripe_subscription_id: string | null;
  setup_fee_payment_intent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ServiceJob {
  id: string;
  contract_id: string;
  vehicle_id: string;
  type: string;
  price_cents: number;
  scheduled_at: string | null;
  status: 'scheduled' | 'in_progress' | 'complete' | 'billed';
  notes: string | null;
  stripe_payment_intent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface BuildOrder {
  id: string;
  customer_id: string;
  vehicle_id: string;
  config: Record<string, any>;
  deposit_amount_cents: number;
  deposit_payment_intent_id: string | null;
  status: 'intake' | 'sourcing' | 'build' | 'qa' | 'ready' | 'delivered' | 'canceled';
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AISourcingRequest {
  id: string;
  customer_id: string;
  spec: Record<string, any>;
  budget_cents: number;
  deposit_payment_intent_id: string | null;
  status: 'intake' | 'researching' | 'candidates_ready' | 'negotiation' | 'purchased' | 'canceled';
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AICandidate {
  id: string;
  request_id: string;
  source_url: string | null;
  attrs: Record<string, any>;
  score: number;
  rationale: string | null;
  internal_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: string;
  customer_id: string;
  object_type: string;
  object_id: string | null;
  stripe_object: string;
  amount_cents: number;
  currency: string;
  status: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}