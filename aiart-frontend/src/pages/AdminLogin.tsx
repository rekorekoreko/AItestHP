import { useState } from "react";
import { apiFetch } from "../lib/api";

export default function AdminLogin() {
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setMsg(null);
    setLoading(true);
    try {
      const res = await apiFetch("/api/admin/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ password: pw }),
      });
      localStorage.setItem("token", (res as any).token);
      setMsg("ログイン成功");
      window.location.href = "/admin";
    } catch (e) {
      const errObj = e as Error;
      setErr(errObj.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-sm mx-auto">
      <h1 className="text-xl font-semibold mb-4">Admin Login</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <input type="password" className="w-full border rounded px-3 py-2" placeholder="パスワード" value={pw} onChange={(e) => setPw(e.target.value)} />
        <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">
          {loading ? "ログイン中..." : "ログイン"}
        </button>
      </form>
      {msg && <div className="mt-3 text-green-600">{msg}</div>}
      {err && <div className="mt-3 text-red-600">{err}</div>}
    </div>
  );
}
