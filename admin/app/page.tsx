"use client";

import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    // For now, redirect to login page
    // In a real app, check authentication status here
    window.location.href = '/login';
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
        <p className="text-muted-foreground">Redirecting to login...</p>
      </div>
    </div>
  );
}
