import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { useParams } from "react-router-dom";

type Detail = {
  id: string;
  title: string;
  author_name: string;
  description: string;
  tags: string[];
  media_type: "image" | "video";
  thumb_url: string;
  media_url: string;
  duration_seconds?: number | null;
  created_at: string;
};

export default function DetailPage() {
  const { id } = useParams();
  const [item, setItem] = useState<Detail | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch(`/api/items/${id}`)
      .then((d: Detail) => setItem(d))
      .catch((e: Error) => setErr(e.message));
  }, [id]);

  if (err) return <div className="p-6 text-red-500">{err}</div>;
  if (!item) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold mb-2">{item.title}</h1>
      <div className="text-sm text-gray-600 mb-4">{item.author_name}</div>
      <div className="mb-4">
        {item.media_type === "image" ? (
          <img src={item.media_url} className="w-full rounded" />
        ) : (
          <video src={item.media_url} className="w-full rounded" controls poster={item.thumb_url} />
        )}
      </div>
      <div className="text-sm whitespace-pre-wrap">{item.description}</div>
      <div className="flex gap-2 mt-3">
        {item.tags.map((t) => (
          <span key={t} className="text-xs bg-gray-100 px-2 py-0.5 rounded">
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}
