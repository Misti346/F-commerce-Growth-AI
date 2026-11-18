import { useState } from 'react';
import { CheckCircle2, Sparkles, Wand2 } from 'lucide-react';
import api from '../../services/api';
import StatusBadge from '../../components/StatusBadge';

const defaultDraft = {
  customer_name: '',
  phone: '',
  address: '',
  product_name: '',
  quantity: 1,
  price: '',
  notes: ''
};

export default function AIOrderExtractionPage() {
  const [message, setMessage] = useState('');
  const [sellerId, setSellerId] = useState(Number(localStorage.getItem('seller_id') || 1));
  const [draft, setDraft] = useState(defaultDraft);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await api.post('/api/ai/extract-order', {
        seller_id: Number(sellerId),
        message
      });

      const orderDraft = response.data.order_draft || {};
      setDraft({
        customer_name: orderDraft.customer_name || '',
        phone: orderDraft.phone || '',
        address: orderDraft.address || '',
        product_name: orderDraft.product_name || '',
        quantity: orderDraft.quantity || 1,
        price: orderDraft.price || '',
        notes: orderDraft.notes || ''
      });
      setResult(response.data);
    } catch (error) {
      console.error('AI extraction failed:', error);
      alert(error.response?.data?.message || 'AI extraction failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (field, value) => {
    setDraft((current) => ({ ...current, [field]: value }));
  };

  const handleSave = async () => {
    try {
      const [productsRes] = await Promise.all([api.get('/api/products')]);
      const products = productsRes.data.products || [];
      const match =
        products.find((product) => product.product_name.toLowerCase().includes((draft.product_name || '').toLowerCase())) ||
        products[0];

      if (!match) {
        alert('Create at least one product before saving an extracted order.');
        return;
      }

      const customerRes = await api.post('/api/customers', {
        seller_id: Number(sellerId),
        customer_name: draft.customer_name || 'Customer',
        phone: draft.phone || '',
        address: draft.address || ''
      });

      await api.post('/api/orders', {
        seller_id: Number(sellerId),
        customer_id: Number(customerRes.data.customer_id),
        items: [{ product_id: Number(match.product_id), quantity: Number(draft.quantity || 1) }],
        payment_method: 'COD',
        order_status: 'Pending',
        delivery_status: 'Pending'
      });

      alert('Order saved successfully.');
    } catch (error) {
      console.error('Save extracted order failed:', error);
      alert(error.response?.data?.message || 'Could not save the order.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <div className="mb-4 flex items-center gap-3">
          <div className="rounded-xl bg-violet-50 p-2 text-violet-600">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-slate-900">AI order extraction</h2>
            <p className="text-sm text-slate-500">Use the existing backend classifier to parse customer messages.</p>
          </div>
        </div>

        <form onSubmit={handleAnalyze} className="space-y-4">
          <label className="block text-sm font-medium text-slate-700">
            <span>Seller ID</span>
            <input
              type="number"
              min="1"
              value={sellerId}
              onChange={(event) => setSellerId(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            />
          </label>

          <label className="block text-sm font-medium text-slate-700">
            <span>Customer message</span>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              rows="6"
              className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
              placeholder="Example: Hi, I want 2 red T-shirts. My name is Rahim. Phone 01712345678. My address is 12 Dhaka..."
              required
            />
          </label>

          <button type="submit" disabled={loading} className="rounded-xl bg-violet-600 px-4 py-2.5 font-semibold text-white hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60">
            {loading ? 'Extracting...' : 'Extract order'}
          </button>
        </form>
      </div>

      {result && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <h2 className="text-xl font-semibold text-slate-900">Review extracted result</h2>
            <StatusBadge status={result.is_complete ? 'Delivered' : 'Pending'} />
            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">Confidence: {Number(result.confidence || 0) * 100}%</span>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Object.entries(draft).map(([field, value]) => (
              <label key={field} className="block space-y-2 text-sm font-medium text-slate-700">
                <span className="capitalize">{field.replace('_', ' ')}</span>
                <input
                  value={value}
                  onChange={(event) => handleFieldChange(field, event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
                />
              </label>
            ))}
          </div>

          {result.missing_fields?.length > 0 && (
            <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="font-semibold text-amber-800">Missing fields</p>
              <p className="mt-2 text-sm text-amber-700">{result.missing_fields.join(', ')}</p>
            </div>
          )}

          {result.invalid_fields?.length > 0 && (
            <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-4">
              <p className="font-semibold text-rose-800">Invalid fields</p>
              <p className="mt-2 text-sm text-rose-700">{result.invalid_fields.join(', ')}</p>
            </div>
          )}

          {result.duplicate_warning && (
            <div className="mt-4 rounded-xl border border-violet-200 bg-violet-50 p-4">
              <p className="font-semibold text-violet-800">Duplicate warning</p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-violet-700">
                {result.duplicate_candidates?.map((candidate) => (
                  <li key={candidate.existing_order_id}>
                    Order #{candidate.existing_order_id} contains {candidate.product_name} in the last 24 hours.
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-6 flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              Ready to save through the existing order API
            </div>
            <button onClick={handleSave} className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 font-semibold text-white hover:bg-emerald-700">
              <Wand2 className="h-4 w-4" />
              Save extracted order
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
