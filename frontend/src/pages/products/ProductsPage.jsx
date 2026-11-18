import { useEffect, useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import api from '../../services/api';
import DataTable from '../../components/DataTable';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ product_name: '', description: '', price: '', stock_quantity: 0 });

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/products');
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('Products fetch failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const filteredProducts = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return products;

    return products.filter((product) =>
      `${product.product_name || ''} ${product.description || ''}`.toLowerCase().includes(query)
    );
  }, [products, search]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleCreateProduct = async (event) => {
    event.preventDefault();

    try {
      await api.post('/api/products', {
        seller_id: Number(localStorage.getItem('seller_id') || 1),
        ...form,
        price: Number(form.price),
        stock_quantity: Number(form.stock_quantity || 0)
      });
      setForm({ product_name: '', description: '', price: '', stock_quantity: 0 });
      await fetchProducts();
    } catch (error) {
      console.error('Create product failed:', error);
      alert(error.response?.data?.message || 'Could not create product.');
    }
  };

  const columns = [
    { key: 'product_id', label: 'ID' },
    { key: 'product_name', label: 'Product' },
    { key: 'description', label: 'Description' },
    { key: 'price', label: 'Price', render: (value) => `৳${Number(value || 0).toLocaleString()}` },
    { key: 'stock_quantity', label: 'Stock' },
    { key: 'created_at', label: 'Created', render: (value) => new Date(value).toLocaleDateString() }
  ];

  if (loading) {
    return <LoadingSpinner label="Loading products" />;
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h2 className="text-xl font-semibold text-slate-900">Add product</h2>
        <form onSubmit={handleCreateProduct} className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="space-y-2 text-sm font-medium text-slate-700 xl:col-span-2">
            <span>Name</span>
            <input name="product_name" value={form.product_name} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" placeholder="Product name" required />
          </label>
          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Price</span>
            <input name="price" type="number" min="0" step="0.01" value={form.price} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" placeholder="0.00" required />
          </label>
          <label className="space-y-2 text-sm font-medium text-slate-700">
            <span>Stock</span>
            <input name="stock_quantity" type="number" min="0" value={form.stock_quantity} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" placeholder="0" />
          </label>
          <label className="space-y-2 text-sm font-medium text-slate-700 xl:col-span-4">
            <span>Description</span>
            <textarea name="description" value={form.description} onChange={handleChange} rows="3" className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100" placeholder="Short product description" />
          </label>
          <div className="flex items-end xl:col-span-4">
            <button type="submit" className="rounded-xl bg-brand-600 px-4 py-2.5 font-semibold text-white hover:bg-brand-700">
              Save product
            </button>
          </div>
        </form>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold text-slate-900">Product catalog</h2>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search products"
              className="rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-9 pr-3 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
            />
          </div>
        </div>

        <DataTable rows={filteredProducts} columns={columns} emptyTitle="No products found" emptyDescription="Create your first product entry." />
      </div>
    </div>
  );
}
