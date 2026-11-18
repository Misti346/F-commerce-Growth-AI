import { useEffect, useMemo, useState } from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { ArrowUpRight, Boxes, CircleDollarSign, ShoppingCart, Users } from 'lucide-react';
import api from '../../services/api';
import StatCard from '../../components/StatCard';
import StatusBadge from '../../components/StatusBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function DashboardPage() {
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ordersRes, customerRes, productsRes] = await Promise.all([
          api.get('/api/orders'),
          api.get('/api/customers'),
          api.get('/api/products')
        ]);

        setOrders(ordersRes.data.orders || []);
        setCustomers(customerRes.data.customers || []);
        setProducts(productsRes.data.products || []);
      } catch (error) {
        console.error('Dashboard data fetch failed:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const summary = useMemo(() => {
    const revenue = orders.reduce((sum, order) => sum + Number(order.total_amount || 0), 0);
    const pending = orders.filter((order) => (order.order_status || '').toLowerCase() === 'pending').length;
    const completed = orders.filter((order) => (order.order_status || '').toLowerCase() === 'delivered').length;
    const cancelled = orders.filter((order) => (order.order_status || '').toLowerCase() === 'cancelled').length;

    return {
      totalOrders: orders.length,
      totalCustomers: customers.length,
      totalProducts: products.length,
      revenue,
      pending,
      completed,
      cancelled
    };
  }, [orders, customers, products]);

  const chartData = useMemo(() => {
    const map = {};

    orders.forEach((order) => {
      const date = new Date(order.order_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      map[date] = (map[date] || 0) + Number(order.total_amount || 0);
    });

    return Object.entries(map).map(([day, revenue]) => ({ day, revenue }));
  }, [orders]);

  const recentOrders = [...orders].slice(0, 5);

  if (loading) {
    return <LoadingSpinner label="Loading dashboard data" />;
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Orders" value={summary.totalOrders} subtitle="Across all active orders" icon={ShoppingCart} accent="brand" />
        <StatCard title="Total Customers" value={summary.totalCustomers} subtitle="Registered customer base" icon={Users} accent="violet" />
        <StatCard title="Total Products" value={summary.totalProducts} subtitle="Catalog listings" icon={Boxes} accent="emerald" />
        <StatCard title="Revenue" value={`৳${summary.revenue.toLocaleString()}`} subtitle="Gross order value" icon={CircleDollarSign} accent="amber" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.8fr_1fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Revenue overview</h2>
              <p className="text-sm text-slate-500">Daily sales by order date</p>
            </div>
            <div className="inline-flex items-center gap-2 rounded-xl bg-emerald-50 px-2.5 py-1 text-sm font-medium text-emerald-700">
              <ArrowUpRight className="h-4 w-4" />
              +12.4% vs prior day
            </div>
          </div>

          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="revenueFill" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="day" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip formatter={(value) => [`৳${Number(value).toLocaleString()}`, 'Revenue']} />
                <Area type="monotone" dataKey="revenue" stroke="#2563eb" fill="url(#revenueFill)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
            <h2 className="text-lg font-semibold text-slate-900">Order health</h2>
            <div className="mt-5 space-y-4">
              <div>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-600">
                  <span>Pending</span>
                  <span>{summary.pending}</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-slate-200">
                  <div className="h-full rounded-full bg-amber-500" style={{ width: `${Math.min(summary.pending * 20 || 10, 100)}%` }} />
                </div>
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-600">
                  <span>Delivered</span>
                  <span>{summary.completed}</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-slate-200">
                  <div className="h-full rounded-full bg-emerald-500" style={{ width: `${Math.min(summary.completed * 20 || 15, 100)}%` }} />
                </div>
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-sm text-slate-600">
                  <span>Cancelled</span>
                  <span>{summary.cancelled}</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-slate-200">
                  <div className="h-full rounded-full bg-rose-500" style={{ width: `${Math.min(summary.cancelled * 20 || 5, 100)}%` }} />
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
            <h2 className="text-lg font-semibold text-slate-900">Quick actions</h2>
            <div className="mt-4 grid grid-cols-1 gap-3">
              <button className="rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700">Create order</button>
              <button className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100">Add product</button>
              <button className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100">View analytics</button>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Recent orders</h2>
          <span className="text-sm text-slate-500">{recentOrders.length} latest records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Order</th>
                <th className="px-4 py-3 font-medium">Customer</th>
                <th className="px-4 py-3 font-medium">Amount</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {recentOrders.map((order) => (
                <tr key={order.order_id}>
                  <td className="px-4 py-3 text-sm text-slate-700">#{order.order_id}</td>
                  <td className="px-4 py-3 text-sm text-slate-700">{order.customer_name}</td>
                  <td className="px-4 py-3 text-sm font-medium text-slate-700">৳{Number(order.total_amount || 0).toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm"><StatusBadge status={order.order_status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
