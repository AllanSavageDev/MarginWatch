'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Margin {
  id: number;
  inserted_at: string;
  exchange?: string;
  underlying?: string;
  product_description?: string;
  trading_class?: string;
  intraday_initial1?: number;
  intraday_maintenance1?: number;
  overnight_initial?: number;
  overnight_maintenance?: number;
  currency?: string;
  has_options?: string;
  short_overnight_initial?: number;
  short_overnight_maintenance?: number;
}

export default function Page() {
  const [margins, setMargins] = useState<Margin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    if (!token) {
      router.push('/login');
      return;
    }

    fetch('http://127.0.0.1:8000/margins_secure', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error('Unauthorized or fetch failed');
        return res.json();
      })
      .then((data) => setMargins(data))
      .catch((err) => {
        console.error('Error fetching secure margins:', err);
        setError('Failed to fetch data');
        router.push('/login'); // fallback in case token is bad
      })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8 bg-white text-black">
      <h1 className="text-2xl font-bold mb-4">Margin Requirements (Secure)</h1>
      {error && <p className="text-red-600 mb-4">{error}</p>}
      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-400 text-sm">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2 border border-gray-400">Exchange</th>
              <th className="px-4 py-2 border border-gray-400">Underlying</th>
              <th className="px-4 py-2 border border-gray-400">Product</th>
              <th className="px-4 py-2 border border-gray-400">Initial</th>
              <th className="px-4 py-2 border border-gray-400">Maint.</th>
              <th className="px-4 py-2 border border-gray-400">Inserted At</th>
            </tr>
          </thead>
          <tbody>
            {margins.map((m) => (
              <tr key={m.id} className="hover:bg-gray-100">
                <td className="px-4 py-2 border border-gray-400">{m.exchange}</td>
                <td className="px-4 py-2 border border-gray-400">{m.underlying}</td>
                <td className="px-4 py-2 border border-gray-400">{m.product_description}</td>
                <td className="px-4 py-2 border border-gray-400">{m.overnight_initial}</td>
                <td className="px-4 py-2 border border-gray-400">{m.overnight_maintenance}</td>
                <td className="px-4 py-2 border border-gray-400">{new Date(m.inserted_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
