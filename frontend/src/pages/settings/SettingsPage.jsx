export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h2 className="text-xl font-semibold text-slate-900">Account settings</h2>
        <div className="mt-5 space-y-4 text-sm text-slate-600">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-slate-800">Business profile</p>
            <p className="mt-2">Manage seller identity and account preferences.</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-slate-800">Notifications</p>
            <p className="mt-2">Email alerts for new orders, duplicate warnings, and updates.</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-medium text-slate-800">Security</p>
            <p className="mt-2">Use a strong password and review your session security settings.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
