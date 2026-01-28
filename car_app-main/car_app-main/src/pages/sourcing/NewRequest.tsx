import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import toast from 'react-hot-toast';
import { submitQuery, QueryResponse } from '../../lib/api';

export function NewSourcingRequest() {
  const [loading, setLoading] = useState(false);
  const [queryText, setQueryText] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!queryText.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      toast.loading('Searching for vehicles...', { id: 'query-search' });
      
      const result: QueryResponse = await submitQuery(queryText);
      
      if (result.success && result.results) {
        toast.success(`Found ${result.result_count || 0} vehicles!`, { id: 'query-search' });
        // Store results in sessionStorage for the results page
        sessionStorage.setItem('queryResults', JSON.stringify(result));
        navigate('/sourcing/candidates');
      } else {
        toast.error(result.error || 'No results found', { id: 'query-search' });
      }
    } catch (error: any) {
      console.error('Query error:', error);
      toast.error(`Failed to search: ${error.message}`, { id: 'query-search' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <Search className="h-12 w-12 text-brand-gold mx-auto mb-4" />
          <h1 className="text-3xl font-extrabold text-white">Vehicle Sourcing</h1>
          <p className="mt-2 text-gray-400">
            Describe the vehicle you're looking for in natural language
          </p>
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-white mb-2">
                What are you looking for?
              </label>
              <textarea
                id="query"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-600 rounded-md bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-gold focus:border-transparent"
                placeholder="e.g., AWD, Diesel-powered Audi, any year, under 150k USD"
                disabled={loading}
              />
              <p className="mt-2 text-sm text-gray-400">
                Describe the make, model, year range, price range, mileage, and any other preferences
              </p>
            </div>

            <button
              type="submit"
              disabled={loading || !queryText.trim()}
              className="w-full py-3 bg-brand-gold text-white font-semibold rounded-lg hover:opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search Vehicles'}
            </button>
          </form>
        </div>

        <div className="mt-6 bg-gray-900 border border-gray-700 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-brand-gold mb-4">Example Queries</h3>
          <div className="space-y-2 text-sm text-gray-400">
            <p>• "manual transmission chevrolet corvette under 60k miles"</p>
            <p>• "Family-friendly SUV with less than 40k miles"</p>
            <p>• "BMW or other fast european car under 50k USD"</p>
            <p>• "2020-2023 Ford F-150 with tow package"</p>
          </div>
        </div>
      </div>
    </div>
  );
}
