import { useState } from 'react';
import { getStripePortalUrl } from '../lib/api';
import toast from 'react-hot-toast';

export function useStripePortal() {
  const [loading, setLoading] = useState(false);

  const openPortal = async (customerId: string) => {
    try {
      setLoading(true);
      const { url } = await getStripePortalUrl(customerId);
      if (url && url !== '#') {
        window.open(url, '_blank');
      } else {
        toast.error('Billing portal is not yet configured');
      }
    } catch (error) {
      toast.error('Failed to open billing portal');
      console.error('Portal error:', error);
    } finally {
      setLoading(false);
    }
  };

  return { openPortal, loading };
}