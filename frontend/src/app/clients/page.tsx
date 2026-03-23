"use client";
import { useEffect, useState } from "react";
import Header from "@/components/Header";
import ClientForm from "@/components/ClientForm";
import { getClients, deleteClient, Client } from "@/lib/api";

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);

  function loadClients() {
    getClients().then(setClients).catch(console.error);
  }

  useEffect(() => { loadClients(); }, []);

  async function handleDelete(id: string) {
    if (!confirm("Delete this client and all their campaigns?")) return;
    await deleteClient(id);
    loadClients();
  }

  return (
    <div>
      <Header title="Clients" />
      <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="px-5 py-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">All Clients ({clients.length})</h2>
            </div>
            <div className="divide-y divide-gray-100">
              {clients.map((client) => (
                <div key={client.id} className="px-5 py-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{client.name}</p>
                    <p className="text-sm text-gray-500">
                      Profile Group: {client.multilogin_profile_group || "None"}
                    </p>
                    <p className="text-xs text-gray-400">
                      Created: {new Date(client.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(client.id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Delete
                  </button>
                </div>
              ))}
              {clients.length === 0 && (
                <p className="px-5 py-8 text-center text-gray-400">No clients yet</p>
              )}
            </div>
          </div>
        </div>
        <div>
          <ClientForm onCreated={loadClients} />
        </div>
      </div>
    </div>
  );
}
