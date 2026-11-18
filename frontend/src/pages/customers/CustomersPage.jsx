import { useEffect, useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import api from '../../services/api';
import DataTable from '../../components/DataTable';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ customer_name: '', phone: '', address: '' });

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/customers');
      setCustomers(response.data.customers || []);
    } catch (error) {
      console.error('Customers fetch failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  const filteredCustomers = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return customers;

    return customers.filter((customer) =>
      `${customer.customer_name || ''} ${customer.phone || ''} ${customer.address || ''}`.toLowerCase().includes(query)
    );
  }, [customers, search]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleCreateCustomer = async (event) => {
    event.preventDefault();

    try {
      await api.post('/api/customers', {
        seller_id: Number(localStorage.getItem('seller_id') || 1),
        ...form
      });
      setForm({ customer_name: '', phone: '', address: '' });
      await fetchCustomers();
    } catch (error) {
      console.error('Create customer failed:', error);
      alert(error.response?.data?.message || 'Could not create customer.');
    }
  };

  const columns = [
    { key: 'customer_id', label: 'ID' },
    { key: 'customer_name', label: 'Customer' },
    { key: 'phone', label: 'Phone' },
    { key: 'address', label: 'Address' },
    { key: 'created_at', label: 'Created', render: (value) => new Date(value).toLocaleDateString() }
  ];

  if (loading) {
    return <LoadingSpinner label="Loading customers" />;
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h2 className="text-xl font-semibold text-slate-900">Add customer</h2>
        <form onSubmit={handleCreateCustomer} className="mt-4 grid gap-4 md:grid-cols-3">
          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Name</span>
            <input name="customer_name" value={form.customer_name} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" placeholder="Customer name" required />
          </label>
          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Phone</span>
            <input name="phone" value={form.phone} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" placeholder="01800000000" />
          </label>
          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Address</span>
            <input name="address" value={form.address} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" placeholder="Dhaka, Bangladesh" />
          </label>
          <div className="flex items-end md:col-span-3">
            <button type="submit" className="rounded-xl bg-brand-600 px-4 py-2.5 font-semibold text-white hover:bg-brand-700">
              Save customer
            </button>
          </div>
        </form>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold text-slate-900">Customer list</h2>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search"
              className="rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-9 pr-3 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            />
          </div>
        </div>

        <DataTable rows={filteredCustomers} columns={columns} emptyTitle="No customers found" emptyDescription="Add a new customer to get started." />
      </div>
    </div>
  );
}
