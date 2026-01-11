// Flask Backend API Client
const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000').trim();

export interface QueryRequest {
  query: string;
}

export interface QueryResponse {
  success: boolean;
  query?: string;
  extracted_fields?: Record<string, any>;
  sql_query?: string;
  sql_params?: any[];
  results?: VehicleResult[];
  result_count?: number;
  total_result_count?: number;
  results_truncated?: boolean;
  quality_warnings?: string[];
  quality_acceptable?: boolean;
  error?: string;
  error_type?: string;
}

export interface VehicleResult {
  make?: string;
  model?: string;
  year?: number;
  trim?: string;
  price_cents?: number;
  mileage?: number;
  color?: string;
  condition?: string;
  vin?: string;
  features?: string[];
  use_case_tags?: string[];
  [key: string]: any; // Allow additional fields
}

/**
 * Submit a natural language query to the Flask backend
 */
export async function submitQuery(query: string): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/api/query/v1`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Submit feedback about query results
 */
export async function submitQueryFeedback(data: {
  query: string;
  extracted_fields?: Record<string, any>;
  sql_query?: string;
  sql_params?: any[];
  reason?: string;
  success?: boolean;
  result_count?: number;
}): Promise<{ success: boolean; message?: string; error?: string }> {
  const response = await fetch(`${API_BASE}/api/query/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Create Stripe checkout session (stubbed - to be replaced with Flask backend)
 */
export async function createCheckoutSession(data: {
  flow: 'concierge' | 'build' | 'sourcing' | 'service';
  customer_id?: string;
  data: any;
}): Promise<{ url: string }> {
  // Stub - will be replaced with Flask backend call
  console.warn('createCheckoutSession: Stub implementation - to be replaced with Flask backend');
  return {
    url: '#', // Placeholder - actual implementation will redirect to Stripe
  };
}

/**
 * Get Stripe portal URL (stubbed - to be replaced with Flask backend)
 */
export async function getStripePortalUrl(customerId: string): Promise<{ url: string }> {
  // Stub - will be replaced with Flask backend call
  console.warn('getStripePortalUrl: Stub implementation - to be replaced with Flask backend');
  return {
    url: '#', // Placeholder - actual implementation will redirect to Stripe portal
  };
}
