"use client";

import React, { useEffect } from 'react';
import { usePathname, useSearchParams, useRouter } from 'next/navigation'; 

export default function MasterComponent() {
  const router = useRouter(); 

  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');

    // Check if the token is available
    if (accessToken) {
      // Redirect to the home page
      router.push('/home');
    } else {
      // Redirect to the login page
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <p className="text-gray-700 text-lg">Checking authentication...</p>
    </div>
  );
}
