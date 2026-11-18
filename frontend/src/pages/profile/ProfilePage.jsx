import { useEffect, useState } from 'react';
import { UserRound } from 'lucide-react';
import api from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/api/auth/profile');
        setProfile(response.data.user);
      } catch (error) {
        console.error('Profile fetch failed:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Loading profile" />;
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-50 text-brand-600">
          <UserRound className="h-8 w-8" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{profile?.name || 'Seller profile'}</h2>
          <p className="text-slate-500">{profile?.email || 'No email available'}</p>
        </div>
      </div>

      <div className="mt-8 grid gap-5 md:grid-cols-2">
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">User ID</p>
          <p className="mt-2 font-semibold text-slate-800">#{profile?.user_id || '—'}</p>
        </div>
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Created</p>
          <p className="mt-2 font-semibold text-slate-800">{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : '—'}</p>
        </div>
      </div>
    </div>
  );
}
