import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryProvider } from './store/query';
import { Layout } from './components/Layout';
import { RequireAuth } from './pages/auth/RequireAuth';
import { Landing } from './pages/Landing';
import { SignIn } from './pages/auth/SignIn';
import { ConciergeEnroll } from './pages/concierge/Enroll';
import { ConciergeServices } from './pages/concierge/Services';
import { NewBuildOrder } from './pages/build/NewOrder';
import { NewSourcingRequest } from './pages/sourcing/NewRequest';
import { SourcingCandidates } from './pages/sourcing/Candidates';
import { SourcingPayment } from './pages/sourcing/Payment';
import { VehicleDetail } from './pages/sourcing/VehicleDetail';
import { BillingPortal } from './pages/billing/Portal';
import { AdminDashboard } from './pages/admin/Dashboard';
import { Toast } from './components/Toast';

function App() {
  return (
    <QueryProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-black text-white">
          <Routes>
            <Route path="/auth/signin" element={<SignIn />} />
            <Route
              path="/*"
              element={
                <RequireAuth>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Landing />} />
                      <Route path="/concierge" element={<ConciergeEnroll />} />
                      <Route path="/concierge/services" element={<ConciergeServices />} />
                      <Route path="/build" element={<NewBuildOrder />} />
                      <Route path="/sourcing" element={<NewSourcingRequest />} />
                      <Route path="/sourcing/candidates" element={<SourcingCandidates />} />
                      <Route path="/sourcing/payment" element={<SourcingPayment />} />
                      <Route path="/sourcing/vehicle/:index" element={<VehicleDetail />} />
                      <Route path="/billing" element={<BillingPortal />} />
                      <Route
                        path="/admin/*"
                        element={
                          <RequireAuth adminOnly>
                            <AdminDashboard />
                          </RequireAuth>
                        }
                      />
                    </Routes>
                  </Layout>
                </RequireAuth>
              }
            />
          </Routes>
        </div>
        <Toast />
      </BrowserRouter>
    </QueryProvider>
  );
}

export default App;