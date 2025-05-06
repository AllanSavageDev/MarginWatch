'use client';

import { useState } from 'react';

export default function CreateUserPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setStatus('');

    const token = localStorage.getItem('token');
    if (!token) {
      setError('You must be logged in to create a user.');
      return;
    }

    const res = await fetch('http://127.0.0.1:8000/create-user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });

    if (res.ok) {
      setStatus('User created successfully.');
      setEmail('');
      setPassword('');
      setFullName('');
    } else {
      const errorMsg = await res.text();
      setError(`Error: ${errorMsg}`);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20 p-6 border rounded-xl shadow">
      <h2 className="text-2xl font-bold mb-4">Create New User</h2>
      <form onSubmit={handleCreate} className="flex flex-col gap-4">
        <input
          className="border p-2 rounded"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="border p-2 rounded"
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
        />
        <input
          className="border p-2 rounded"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button
          className="bg-green-600 text-white py-2 rounded hover:bg-green-700"
          type="submit"
        >
          Create User
        </button>
        {status && <div className="text-green-600 text-sm">{status}</div>}
        {error && <div className="text-red-600 text-sm">{error}</div>}
      </form>
    </div>
  );
}
