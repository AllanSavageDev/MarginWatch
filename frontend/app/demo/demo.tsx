"use client";
import { useEffect, useState } from "react";

export default function Demo() {
  const [token, setToken] = useState("");
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ id: 0, name: "", description: "" });

  const fetchItems = async () => {
    const res = await fetch("/api/items", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setItems(data);
  };

  const login = async () => {
    const res = await fetch("/api/auth", {
      method: "POST",
      body: JSON.stringify({ email: "demo@demo.com", password: "password" }),
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    setToken(data.access_token);
  };

  const createItem = async () => {
    await fetch("/api/items", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(form),
    });
    fetchItems();
  };

  const deleteItem = async (id: number) => {
    await fetch(`/api/items/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchItems();
  };

  useEffect(() => {
    if (token) fetchItems();
  }, [token]);

  return (
    <div className="p-4">
      <h1 className="text-xl mb-4">Demo Page</h1>
      <button onClick={login} className="border px-4 py-2 mb-4">Login</button>
      <div className="mb-4">
        <input
          className="border p-2 mr-2"
          placeholder="ID"
          onChange={(e) => setForm({ ...form, id: parseInt(e.target.value) })}
        />
        <input
          className="border p-2 mr-2"
          placeholder="Name"
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <input
          className="border p-2 mr-2"
          placeholder="Description"
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        <button onClick={createItem} className="border px-4 py-2">Add</button>
      </div>
      <ul>
        {items.map((item: any) => (
          <li key={item.id} className="mb-2">
            <b>{item.name}</b>: {item.description}
            <button
              onClick={() => deleteItem(item.id)}
              className="ml-2 text-red-500"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
