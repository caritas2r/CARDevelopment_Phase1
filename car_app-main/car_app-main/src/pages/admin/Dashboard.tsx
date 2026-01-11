import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { supabase } from '../../lib/supabase';
import { Table } from '../../components/Table';
import { StatusBadge } from '../../components/StatusBadge';
import { formatPrice } from '../../lib/stripe';
import { format } from 'date-fns';
import { 
  Users, 
  Shield, 
  Wrench, 
  Search, 
  CreditCard, 
  FileText,
  Car,
  Calendar
} from 'lucide-react';

export function AdminDashboard() {
  const location = useLocation();
  
  const navigation = [
    { name: 'Customers', href: '/admin', icon: Users },
    { name: 'Concierge', href: '/admin/concierge', icon: Shield },
    { name: 'Build Orders', href: '/admin/builds', icon: Wrench },
    { name: 'Sourcing', href: '/admin/sourcing', icon: Search },
    { name: 'Vehicles', href: '/admin/vehicles', icon: Car },
    { name: 'Services', href: '/admin/services', icon: Calendar },
    { name: 'Payments', href: '/admin/payments', icon: CreditCard },
  ];

  return (
    <div className="min-h-screen bg-black">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-gray-900 border-r border-gray-700">
          <div className="p-6">
            <h1 className="text-xl font-bold text-brand-gold">Admin Dashboard</h1>
          </div>
          <nav className="mt-6">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                  location.pathname === item.href
                    ? 'bg-brand-gold/10 text-brand-gold border-r-2 border-brand-gold'
                    : 'text-gray-300 hover:text-brand-gold hover:bg-gray-800'
                }`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<CustomersView />} />
            <Route path="/concierge" element={<ConciergeView />} />
            <Route path="/builds" element={<BuildOrdersView />} />
            <Route path="/sourcing" element={<SourcingView />} />
            <Route path="/vehicles" element={<VehiclesView />} />
            <Route path="/services" element={<ServicesView />} />
            <Route path="/payments" element={<PaymentsView />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

function CustomersView() {
  const { data: customers, isLoading } = useQuery({
    queryKey: ['admin-customers'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('customers')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const columns = [
    { key: 'full_name', header: 'Name' },
    { key: 'email', header: 'Email' },
    { key: 'phone', header: 'Phone' },
    { 
      key: 'created_at', 
      header: 'Joined',
      cell: (value: string) => value ? format(new Date(value), 'MMM d, yyyy') : 'N/A'
    },
    {
      key: 'stripe_customer_id',
      header: 'Stripe Status',
      cell: (value: string) => value ? 'Connected' : 'Not Connected'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Customers</h2>
      <div className="bg-gray-900 border border-gray-700 rounded-lg">
        <Table columns={columns} data={customers || []} loading={isLoading} />
      </div>
    </div>
  );
}

function ConciergeView() {
  const { data: contracts, isLoading } = useQuery({
    queryKey: ['admin-concierge'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('concierge_contracts')
        .select(`
          *,
          customers(full_name, email)
        `)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const columns = [
    { 
      key: 'customers', 
      header: 'Customer',
      cell: (value: any) => value?.full_name || value?.email || 'N/A'
    },
    { key: 'location', header: 'Location' },
    { key: 'plan', header: 'Plan' },
    { key: 'vehicles_count', header: 'Vehicles' },
    { 
      key: 'status', 
      header: 'Status',
      cell: (value: string) => value ? <StatusBadge status={value} /> : 'N/A'
    },
    { 
      key: 'created_at', 
      header: 'Created',
      cell: (value: string) => value ? format(new Date(value), 'MMM d, yyyy') : 'N/A'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Concierge Contracts</h2>
      <div className="bg-gray-900 border border-gray-700 rounded-lg">
        <Table columns={columns} data={contracts || []} loading={isLoading} />
      </div>
    </div>
  );
}

function BuildOrdersView() {
  const { data: orders, isLoading } = useQuery({
    queryKey: ['admin-build-orders'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('build_orders')
        .select(`
          *,
          customers(full_name, email),
          vehicles(year, make, model)
        `)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const columns = [
    { 
      key: 'customers', 
      header: 'Customer',
      cell: (value: any) => value?.full_name || value?.email || 'N/A'
    },
    { 
      key: 'vehicles', 
      header: 'Vehicle',
      cell: (value: any) => value ? `${value.year} ${value.make} ${value.model}` : 'N/A'
    },
    { 
      key: 'status', 
      header: 'Status',
      cell: (value: string) => value ? <StatusBadge status={value} /> : 'N/A'
    },
    { 
      key: 'created_at', 
      header: 'Created',
      cell: (value: string) => value ? format(new Date(value), 'MMM d, yyyy') : 'N/A'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Build Orders</h2>
      <div className="bg-gray-900 border border-gray-700 rounded-lg">
        <Table columns={columns} data={orders || []} loading={isLoading} />
      </div>
    </div>
  );
}

function SourcingView() {
  const { data: requests, isLoading } = useQuery({
    queryKey: ['admin-sourcing-requests'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('ai_sourcing_requests')
        .select(`
          *,
          customers(full_name, email)
        `)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const columns = [
    { 
      key: 'customers', 
      header: 'Customer',
      cell: (value: any) => value?.full_name || value?.email || 'N/A'
    },
    { 
      key: 'spec', 
      header: 'Target Vehicle',
      cell: (value: any) => value ? `${value.make} ${value.model}` : 'N/A'
    },
    { 
      key: 'budget_cents', 
      header: 'Budget',
      cell: (value: number) => value ? formatPrice(value) : 'N/A'
    },
    { 
      key: 'status', 
      header: 'Status',
      cell: (value: string) => value ? <StatusBadge status={value} /> : 'N/A'
    },
    { 
      key: 'created_at', 
      header: 'Created',
      cell: (value: string) => value ? format(new Date(value), 'MMM d, yyyy') : 'N/A'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Sourcing Requests</h2>
      <div className="bg-gray-900 border border-gray-700 rounded-lg">
        <Table columns={columns} data={requests || []} loading={isLoading} />
      </div>
    </div>
  );
}

function VehiclesView() {
  const { data: vehicles, isLoading } = useQuery({
    queryKey: ['admin-vehicles'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('vehicles')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const columns = [
    { 
      key: 'vehicle', 
      header: 'Vehicle',
      cell: (_: any, row: any) => `${row.year} ${row.make} ${row.model}`
    },
    { key: 'source', header: 'Source' },
    { key: 'color', header: 'Color' },
    { 
      key: 'mileage', 
      header: 'Mileage',
      cell: (value: number) => value ? value.toLocaleString() : 'New'
    },
    { 
      key: 'price_cents', 
      header: 'Price',
      cell: (value: number) => value ? formatPrice(value) : 'N/A'
    },
    { 
      key: 'available', 
      header: 'Available',
      cell: (value: boolean) => value ? 'Yes' : 'No'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Vehicles</h2>
      <div className="bg-gray-900 border border-gray-700 rounded-lg">
        <Table columns={columns} data={vehicles || []} loading={isLoading} />
      </div>
    </div>
  );
}

function ServicesView() {
  const { data: services, isLoading } = useQuery({
    queryKey: ['admin-services'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('service_jobs')
        .select(`
          *,
          concierge_contracts(customers(full_name, email)),
          vehicles(year, make, model)
        `)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const columns = [
    { 
      key: 'concierge_contracts', 
      header: 'Customer',
      cell: (value: any) => value?.customers?.full_name || value?.customers?.email || 'N/A'
    },
    { 
      key: 'vehicles', 
      header: 'Vehicle',
      cell: (value: any) => value ? `${value.year} ${value.make} ${value.model}` : 'N/A'
    },
    { key: 'type', header: 'Service' },
    { 
      key: 'price_cents', 
      header: 'Price',
      cell: (value: number) => value ? formatPrice(value) : 'N/A'
    },
    { 
      key: 'status', 
      header: 'Status',
      cell: (value: string) => value ? <StatusBadge status={value} /> : 'N/A'
    },
    { 
      key: 'scheduled_at', 
      header: 'Scheduled',
      cell: (value: string) => value ? format(new Date(value), 'MMM d, yyyy') : 'Not scheduled'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Service Jobs</h2>
      <div className="bg-gray-900 border border-gray-700 rounded-lg">
        <Table columns={columns} data={services || []} loading={isLoading} />
      </div>
    </div>
  );
}

function PaymentsView() {
  const { data: payments, isLoading } = useQuery({
    queryKey: ['admin-payments'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('payments')
        .select(`
          *,
          customers(full_name, email)
        `)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    },
  });

  const columns = [
    { 
      key: 'customers', 
      header: 'Customer',
      cell: (value: any) => value?.full_name || value?.email || 'N/A'
    },
    { key: 'object_type', header: 'Type' },
    { 
      key: 'amount_cents', 
      header: 'Amount',
      cell: (value: number) => value ? formatPrice(value) : 'N/A'
    },
    { 
      key: 'status', 
      header: 'Status',
      cell: (value: string) => value ? <StatusBadge status={value} /> : 'N/A'
    },
    { 
      key: 'created_at', 
      header: 'Date',
      cell: (value: string) => value ? format(new Date(value), 'MMM d, yyyy') : 'N/A'
    }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-6">Payments</h2>
      <div className="bg-gray-900 border border-gray-700 rounded-lg">
        <Table columns={columns} data={payments || []} loading={isLoading} />
      </div>
    </div>
  );
}
