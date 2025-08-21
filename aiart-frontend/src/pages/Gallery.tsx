import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

type Item = {
  id: string;
  title: string;
  author_name: string;
  tags: string[];
  media_type: "image" | "video";
  thumb_url: string;
  detail_url: string;
};

export default function Gallery() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    apiFetch("/api/gallery")
      .then((data: Item[]) => setItems(data))
      .catch((e: Error) => setErr(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6">Loading...</div>;
  if (err) return <div className="p-6 text-red-500">{err}</div>;

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-4">Gallery</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {items.map((it) => (
          <a
            key={it.id}
            href={`/detail/${it.id}`}
            className="block bg-white rounded shadow hover:shadow-md transition"
          >
            <img src={it.thumb_url} className="w-full h-40 object-cover rounded-t" />
            <div className="p-2">
              <div className="text-sm font-medium line-clamp-1">{it.title}</div>
              <div className="text-xs text-gray-500">{it.author_name}</div>
              <div className="flex flex-wrap gap-1 mt-1">
                {it.tags.map((t) => (
                  <span key={t} className="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
