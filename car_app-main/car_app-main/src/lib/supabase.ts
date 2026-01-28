// Stub for Supabase - replaced with local database connection (to be implemented)
// For now, returns mock/empty data to keep UI functional

export const supabase = {
  auth: {
    getSession: async () => {
      return {
        data: {
          session: {
            access_token: 'mock-token',
            user: {
              id: 'mock-user-id',
              email: 'user@example.com',
            },
          },
        },
        error: null,
      };
    },
  },
  from: (table: string) => ({
    select: (columns: string) => ({
      eq: (column: string, value: any) => ({
        order: (column: string, options?: any) => ({
          then: async (callback: any) => {
            // Return empty array for now - will be replaced with actual database queries
            return { data: [], error: null };
          },
        }),
        single: async () => {
          return { data: null, error: null };
        },
        then: async (callback: any) => {
          return { data: [], error: null };
        },
      }),
      order: (column: string, options?: any) => ({
        then: async (callback: any) => {
          return { data: [], error: null };
        },
      }),
      then: async (callback: any) => {
        return { data: [], error: null };
      },
    }),
  }),
};

export type Database = {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          role: 'customer' | 'admin';
          full_name: string | null;
          phone: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id: string;
          role?: 'customer' | 'admin';
          full_name?: string | null;
          phone?: string | null;
        };
        Update: {
          role?: 'customer' | 'admin';
          full_name?: string | null;
          phone?: string | null;
        };
      };
      customers: {
        Row: {
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
        };
        Insert: {
          id?: string;
          user_id?: string | null;
          email: string;
          phone?: string | null;
          full_name?: string | null;
          address_line1?: string | null;
          address_line2?: string | null;
          city?: string | null;
          state?: string | null;
          zip?: string | null;
          stripe_customer_id?: string | null;
          ghl_contact_id?: string | null;
        };
        Update: {
          email?: string;
          phone?: string | null;
          full_name?: string | null;
          address_line1?: string | null;
          address_line2?: string | null;
          city?: string | null;
          state?: string | null;
          zip?: string | null;
          stripe_customer_id?: string | null;
          ghl_contact_id?: string | null;
        };
      };
    };
  };
};

