import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

axios.defaults.baseURL = 'http://127.0.0.1:8000';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Assumes you have a registration endpoint at /api/auth/register/
      await axios.post('/api/auth/register/', { username, email, password });
      router.push('/login');
    } catch (err) {
      console.error(err);
      setError('Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center text-gray-800">Register</h1>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <form onSubmit={handleSubmit}>
          <label className="block mb-2 text-gray-700">
            Username:
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 p-2 w-full border rounded"
              required
            />
          </label>
          <label className="block mb-2 text-gray-700">
            Email:
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 p-2 w-full border rounded"
              required
            />
          </label>
          <label className="block mb-4 text-gray-700">
            Password:
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 p-2 w-full border rounded"
              required
            />
          </label>
          <button type="submit" className="w-full bg-green-600 text-white p-2 rounded">
            Register
          </button>
        </form>
        {/* Link to login page */}
        <p className="text-sm text-gray-700 mt-4 text-center">
          Already have an account?{' '}
          <a
            href="/login"
            className="text-blue-600 hover:underline"
          >
            Login here
          </a>
        </p>
      </div>
    </div>
  );
}
