import { useState } from "react";
import { apiFetch } from "../lib/api";

export default function SubmitPage() {
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [desc, setDesc] = useState("");
  const [tags, setTags] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] || null;
    setFile(f);
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setErr(null);
    if (!file) {
      setErr("ファイルを選択してください");
      return;
    }
    const isImage = file.type.startsWith("image/");
    const isVideo = file.type === "video/mp4" || file.type === "video/webm";
    if (!isImage && !isVideo) {
      setErr("対応していないファイル形式です");
      return;
    }
    if (isImage && file.size > 10 * 1024 * 1024) {
      setErr("画像サイズは最大10MBです");
      return;
    }
    if (isVideo && file.size > 50 * 1024 * 1024) {
      setErr("動画サイズは最大50MBです");
      return;
    }
    const fd = new FormData();
    fd.append("title", title);
    fd.append("author_name", author);
    fd.append("description", desc);
    fd.append("tags", tags);
    fd.append("file", file);
    setLoading(true);
    try {
      await apiFetch("/api/submissions", { method: "POST", body: fd, headers: {} });
      setMsg("投稿が受け付けられました。審査後に公開されます。");
      setTitle("");
      setAuthor("");
      setDesc("");
      setTags("");
      setFile(null);
    } catch (e) {
      const errObj = e as Error;
      setErr(errObj.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-xl font-semibold mb-4">作品を投稿</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <input className="w-full border rounded px-3 py-2" placeholder="タイトル" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <input className="w-full border rounded px-3 py-2" placeholder="作者名" value={author} onChange={(e) => setAuthor(e.target.value)} required />
        <textarea className="w-full border rounded px-3 py-2" placeholder="説明" value={desc} onChange={(e) => setDesc(e.target.value)} />
        <input className="w-full border rounded px-3 py-2" placeholder="タグ（カンマ区切り）" value={tags} onChange={(e) => setTags(e.target.value)} />
        <input type="file" accept="image/*,video/mp4,video/webm" onChange={onFileChange} />
        <button disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50">
          {loading ? "アップロード中..." : "投稿"}
        </button>
      </form>
      {msg && <div className="mt-3 text-green-600">{msg}</div>}
      {err && <div className="mt-3 text-red-600">{err}</div>}
    </div>
  );
}
