'use client';

import { useState } from 'react';

export default function MePage() {
  const [user, setUser] = useState<any>(null);
  const [error, setError] = useState('');

  const handleGetMe = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setUser(null);

    const token = localStorage.getItem('token');
    if (!token) {
      setError('No token found in localStorage.');
      return;
    }

    const res = await fetch('http://127.0.0.1:8000/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      const data = await res.json();
      setUser(data);
    } else {
      const errorMsg = await res.text();
      setError(`Failed to fetch user: ${errorMsg}`);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20 p-6 border rounded-xl shadow">
      <h2 className="text-2xl font-bold mb-4">Current User</h2>
      <form onSubmit={handleGetMe} className="flex flex-col gap-4">
        <button
          className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          type="submit"
        >
          Get Current User
        </button>
        {user && (
          <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
            {JSON.stringify(user, null, 2)}
          </pre>
        )}
        {error && <div className="text-red-600 text-sm">{error}</div>}
      </form>
    </div>
  );
}
