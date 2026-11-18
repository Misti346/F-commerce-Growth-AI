import { useMemo } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const salesData = [
  { month: 'Jan', sales: 1200 },
  { month: 'Feb', sales: 1400 },
  { month: 'Mar', sales: 1320 },
  { month: 'Apr', sales: 1800 },
  { month: 'May', sales: 2100 },
  { month: 'Jun', sales: 2600 }
];

const statusData = [
  { name: 'Pending', value: 18 },
  { name: 'Processing', value: 24 },
  { name: 'Delivered', value: 52 },
  { name: 'Cancelled', value: 6 }
];

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f97316'];

export default function AnalyticsPage() {
  const performance = useMemo(() => [
    { product: 'Shirt', revenue: 4300 },
    { product: 'Jeans', revenue: 3600 },
    { product: 'Bag', revenue: 2900 },
    { product: 'Shoe', revenue: 2500 }
  ], []);

  return (
    <div className="space-y-6">
      <div className="grid gap-5 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <p className="text-sm text-slate-500">Monthly sales</p>
          <h3 className="mt-2 text-3xl font-bold text-slate-900">৳14.8K</h3>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <p className="text-sm text-slate-500">Orders trend</p>
          <h3 className="mt-2 text-3xl font-bold text-slate-900">+24%</h3>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <p className="text-sm text-slate-500">Customer growth</p>
          <h3 className="mt-2 text-3xl font-bold text-slate-900">+17%</h3>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <h2 className="text-lg font-semibold text-slate-900">Sales overview</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={salesData}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip formatter={(value) => [`৳${Number(value).toLocaleString()}`, 'Sales']} />
                <Bar dataKey="sales" radius={[8, 8, 0, 0]} fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <h2 className="text-lg font-semibold text-slate-900">Order status distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie dataKey="value" data={statusData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5}>
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${entry.name}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h2 className="text-lg font-semibold text-slate-900">Top product performance</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Product</th>
                <th className="px-4 py-3 font-medium">Revenue</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {performance.map((item) => (
                <tr key={item.product}>
                  <td className="px-4 py-3 text-sm text-slate-700">{item.product}</td>
                  <td className="px-4 py-3 text-sm font-medium text-slate-700">৳{item.revenue.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
