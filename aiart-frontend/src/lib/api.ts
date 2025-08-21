const API_URL = import.meta.env.VITE_API_URL as string;

export const apiFetch = async (path: string, opts: RequestInit = {}) => {
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      ...(opts.headers || {}),
    },
    ...opts,
  });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      if ((data as any)?.detail) message = (data as any).detail;
    } catch {}
    throw new Error(message);
  }
  if ((opts as any).raw) return res as any;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    return res.json();
  }
  return res.text();
};

export const authHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export default { apiFetch, authHeaders };
