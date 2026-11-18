import { useEffect, useMemo, useState } from 'react';
import { Search, Trash2 } from 'lucide-react';
import api from '../../services/api';
import DataTable from '../../components/DataTable';
import LoadingSpinner from '../../components/LoadingSpinner';
import StatusBadge from '../../components/StatusBadge';

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [form, setForm] = useState({
    customer_id: '',
    product_id: '',
    quantity: 1,
    payment_method: 'COD',
    order_status: 'Pending',
    delivery_status: 'Pending'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ordersRes, customersRes, productsRes] = await Promise.all([
        api.get('/api/orders'),
        api.get('/api/customers'),
        api.get('/api/products')
      ]);

      setOrders(ordersRes.data.orders || []);
      setCustomers(customersRes.data.customers || []);
      setProducts(productsRes.data.products || []);
    } catch (error) {
      console.error('Order fetch failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredOrders = useMemo(() => {
    return orders.filter((order) => {
      const matchesSearch =
        !search ||
        `${order.customer_name} ${order.phone || ''} ${order.order_id}`.toLowerCase().includes(search.toLowerCase());
      const matchesStatus = statusFilter === 'All' || (order.order_status || '').toLowerCase() === statusFilter.toLowerCase();
      return matchesSearch && matchesStatus;
    });
  }, [orders, search, statusFilter]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleCreateOrder = async (event) => {
    event.preventDefault();

    try {
      await api.post('/api/orders', {
        seller_id: Number(localStorage.getItem('seller_id') || 1),
        customer_id: Number(form.customer_id),
        items: [
          {
            product_id: Number(form.product_id),
            quantity: Number(form.quantity || 1)
          }
        ],
        payment_method: form.payment_method,
        order_status: form.order_status,
        delivery_status: form.delivery_status
      });

      setForm({
        customer_id: '',
        product_id: '',
        quantity: 1,
        payment_method: 'COD',
        order_status: 'Pending',
        delivery_status: 'Pending'
      });
      await fetchData();
    } catch (error) {
      console.error('Create order failed:', error);
      alert(error.response?.data?.message || 'Could not create the order.');
    }
  };

  const handleDeleteOrder = async (orderId) => {
    if (!window.confirm('Delete this order?')) return;

    try {
      await api.delete(`/api/orders/${orderId}`);
      await fetchData();
    } catch (error) {
      console.error('Delete order failed:', error);
      alert(error.response?.data?.message || 'Could not delete the order.');
    }
  };

  const columns = [
    { key: 'order_id', label: 'Order' },
    { key: 'customer_name', label: 'Customer' },
    { key: 'phone', label: 'Phone' },
    { key: 'total_amount', label: 'Amount', render: (value) => `৳${Number(value || 0).toLocaleString()}` },
    {
      key: 'order_status',
      label: 'Status',
      render: (value) => <StatusBadge status={value} />
    },
    {
      key: 'action',
      label: 'Action',
      render: (_, row) => (
        <button
          type="button"
          onClick={() => handleDeleteOrder(row.order_id)}
          className="inline-flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-2.5 py-1.5 text-xs font-medium text-rose-700 hover:bg-rose-100"
        >
          <Trash2 className="h-3.5 w-3.5" />
          Delete
        </button>
      )
    }
  ];

  if (loading) {
    return <LoadingSpinner label="Loading orders" />;
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h2 className="text-xl font-semibold text-slate-900">Create order</h2>
        <form onSubmit={handleCreateOrder} className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <label className="space-y-2 text-sm font-medium text-slate-700 xl:col-span-2">
            <span>Customer</span>
            <select name="customer_id" value={form.customer_id} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" required>
              <option value="">Select customer</option>
              {customers.map((customer) => (
                <option key={customer.customer_id} value={customer.customer_id}>
                  {customer.customer_name}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-2 text-sm font-medium text-slate-700 xl:col-span-2">
            <span>Product</span>
            <select name="product_id" value={form.product_id} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" required>
              <option value="">Select product</option>
              {products.map((product) => (
                <option key={product.product_id} value={product.product_id}>
                  {product.product_name}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Quantity</span>
            <input name="quantity" type="number" min="1" value={form.quantity} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" required />
          </label>

          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Payment</span>
            <select name="payment_method" value={form.payment_method} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100">
              <option value="COD">COD</option>
              <option value="Bkash">Bkash</option>
              <option value="Nagad">Nagad</option>
            </select>
          </label>

          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Order status</span>
            <select name="order_status" value={form.order_status} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100">
              <option value="Pending">Pending</option>
              <option value="Processing">Processing</option>
              <option value="Shipped">Shipped</option>
              <option value="Delivered">Delivered</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </label>

          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Delivery</span>
            <select name="delivery_status" value={form.delivery_status} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100">
              <option value="Pending">Pending</option>
              <option value="In Transit">In Transit</option>
              <option value="Delivered">Delivered</option>
            </select>
          </label>

          <div className="flex items-end xl:col-span-2">
            <button type="submit" className="w-full rounded-xl bg-brand-600 px-4 py-2.5 font-semibold text-white hover:bg-brand-700">
              Save order
            </button>
          </div>
        </form>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <h2 className="text-xl font-semibold text-slate-900">Order list</h2>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search orders"
                className="rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-9 pr-3 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
              />
            </div>
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100">
              <option value="All">All statuses</option>
              <option value="Pending">Pending</option>
              <option value="Processing">Processing</option>
              <option value="Shipped">Shipped</option>
              <option value="Delivered">Delivered</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <DataTable
          rows={filteredOrders}
          columns={columns}
          emptyTitle="No orders found"
          emptyDescription="Try a different search or create a new order."
        />
      </div>
    </div>
  );
}
