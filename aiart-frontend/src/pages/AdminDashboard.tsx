import { useEffect, useState } from "react";
import { apiFetch, authHeaders } from "../lib/api";

type AdminItem = {
  id: string;
  title: string;
  author_name: string;
  description: string;
  tags: string[];
  media_type: "image" | "video";
  file_path: string;
  thumb_path?: string | null;
  duration_seconds?: number | null;
  created_at: string;
  status: "pending" | "approved" | "rejected";
  rejected_reason?: string | null;
};

export default function AdminDashboard() {
  const [items, setItems] = useState<AdminItem[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"pending" | "approved" | "rejected" | "">("pending");

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const qs = filter ? `?status=${filter}` : "";
      const data = await apiFetch(`/api/admin/submissions${qs}`, { headers: { ...authHeaders() } });
      setItems(data as AdminItem[]);
    } catch (e) {
      const errObj = e as Error;
      setErr(errObj.message);
      if (errObj.message.includes("401")) {
        window.location.href = "/admin-login";
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [filter]);

  async function approve(id: string) {
    try {
      await apiFetch(`/api/admin/submissions/${id}/approve`, { method: "POST", headers: { ...authHeaders() } });
      load();
    } catch (e) {
      const errObj = e as Error;
      alert(errObj.message);
    }
  }

  async function reject(id: string) {
    const reason = window.prompt("Reject reason (optional)") || "";
    const fd = new FormData();
    fd.append("reason", reason);
    try {
      await apiFetch(`/api/admin/submissions/${id}/reject`, { method: "POST", headers: { ...authHeaders() }, body: fd });
      load();
    } catch (e) {
      const errObj = e as Error;
      alert(errObj.message);
    }
  }

  const apiBase = import.meta.env.VITE_API_URL as string;

  function toMediaUrl(p?: string | null) {
    if (!p) return "";
    const idx = p.indexOf("/media/");
    if (idx >= 0) {
      const rel = p.slice(idx + "/media/".length);
      return `${apiBase}/media/${rel}`;
    }
    const last = p.lastIndexOf("/media/");
    if (last >= 0) {
      const rel = p.slice(last + "/media/".length);
      return `${apiBase}/media/${rel}`;
    }
    const baseIdx = p.lastIndexOf("/uploads/");
    if (baseIdx >= 0) {
      const rel = p.slice(baseIdx + 1);
      return `${apiBase}/${rel}`;
    }
    return `${apiBase}/media/${p.split("/").slice(-2).join("/")}`;
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">Admin Dashboard</h1>
        <div className="flex gap-2">
          <button onClick={() => setFilter("pending")} className={`px-3 py-1 rounded ${filter === "pending" ? "bg-blue-600 text-white" : "bg-gray-100"}`}>Pending</button>
          <button onClick={() => setFilter("approved")} className={`px-3 py-1 rounded ${filter === "approved" ? "bg-blue-600 text-white" : "bg-gray-100"}`}>Approved</button>
          <button onClick={() => setFilter("rejected")} className={`px-3 py-1 rounded ${filter === "rejected" ? "bg-blue-600 text-white" : "bg-gray-100"}`}>Rejected</button>
          <button onClick={() => setFilter("")} className={`px-3 py-1 rounded ${filter === "" ? "bg-blue-600 text-white" : "bg-gray-100"}`}>All</button>
        </div>
      </div>
      {loading && <div>Loading...</div>}
      {err && <div className="text-red-500">{err}</div>}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {items.map((it) => {
          const thumbUrl = toMediaUrl(it.thumb_path || it.file_path);
          const fileUrl = toMediaUrl(it.file_path);
          return (
            <div key={it.id} className="bg-white rounded shadow">
              <img src={thumbUrl} className="w-full h-36 object-cover rounded-t" />
              <div className="p-2">
                <div className="font-medium text-sm line-clamp-1">{it.title}</div>
                <div className="text-xs text-gray-500">{it.author_name}</div>
                <div className="text-xs mt-1">{it.media_type}</div>
                <div className="flex gap-2 mt-2">
                  <a href={fileUrl} target="_blank" className="text-xs underline">Open</a>
                  {it.status === "pending" && (
                    <>
                      <button onClick={() => approve(it.id)} className="text-xs bg-green-600 text-white px-2 py-1 rounded">Approve</button>
                      <button onClick={() => reject(it.id)} className="text-xs bg-red-600 text-white px-2 py-1 rounded">Reject</button>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
