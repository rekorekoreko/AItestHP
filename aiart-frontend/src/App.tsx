import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Gallery from "./pages/Gallery";
import SubmitPage from "./pages/Submit";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import DetailPage from "./pages/Detail";

export default function App() {
  useEffect(() => {
    document.title = "AIArt";
  }, []);
  return (
    <BrowserRouter>
      <nav className="border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
          <Link to="/" className="font-semibold">AIArt</Link>
          <Link to="/" className="text-sm text-gray-700">Gallery</Link>
          <Link to="/submit" className="text-sm text-gray-700">Submit</Link>
          <Link to="/admin" className="ml-auto text-sm text-gray-700">Admin</Link>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<Gallery />} />
        <Route path="/submit" element={<SubmitPage />} />
        <Route path="/detail/:id" element={<DetailPage />} />
        <Route path="/admin-login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
