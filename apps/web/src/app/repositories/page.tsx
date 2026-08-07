'use client';

import { useEffect, useState } from 'react';

interface Repository {
  id: string;
  name: string;
  url: string;
  default_branch: string;
  created_at: string;
}

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({
    name: '',
    url: '',
    default_branch: 'main',
  });

  const [error, setError] = useState<string | null>(null);

  const API_BASE =
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const getErrorMessage = (err: unknown) =>
    err instanceof Error ? err.message : String(err);

  // Fetch repositories when the page loads
  useEffect(() => {
    const loadRepositories = async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await fetch(
          `${API_BASE}/api/v1/repositories`
        );

        if (!res.ok) {
          throw new Error('Failed to load repositories');
        }

        const data = await res.json();

        setRepositories(data);
      } catch (err: unknown) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    loadRepositories();
  }, []);

  // Handle repository creation
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setError(null);

    try {
      const res = await fetch(
        `${API_BASE}/api/v1/repositories`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(form),
        }
      );

      if (!res.ok) {
        const errData = await res.json();

        throw new Error(
          errData.detail || 'Failed to create repository'
        );
      }

      // Reset form
      setForm({
        name: '',
        url: '',
        default_branch: 'main',
      });

      // Refresh repository list
      const refreshRes = await fetch(
        `${API_BASE}/api/v1/repositories`
      );

      if (!refreshRes.ok) {
        throw new Error('Repository created, but failed to refresh list');
      }

      const data = await refreshRes.json();

      setRepositories(data);
    } catch (err: unknown) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">
          Repository Management
        </h1>

        <p className="text-slate-400 mt-2">
          Register repositories that CodeAtlas will analyze.
        </p>
      </div>

      {/* Creation Form */}
      <form
        onSubmit={handleSubmit}
        className="p-6 bg-slate-900 border border-slate-800 rounded-lg space-y-4"
      >
        <h2 className="text-xl font-semibold text-slate-100">
          Add New Repository
        </h2>

        {error && (
          <div className="p-3 bg-red-950 border border-red-800 text-red-200 rounded text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          {/* Repository Name */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">
              Repository Name
            </label>

            <input
              type="text"
              required
              value={form.name}
              onChange={(e) =>
                setForm({
                  ...form,
                  name: e.target.value,
                })
              }
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white"
              placeholder="e.g. My Express App"
            />
          </div>

          {/* Default Branch */}
          <div>
            <label className="block text-sm text-slate-400 mb-1">
              Default Branch
            </label>

            <input
              type="text"
              required
              value={form.default_branch}
              onChange={(e) =>
                setForm({
                  ...form,
                  default_branch: e.target.value,
                })
              }
              className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white"
            />
          </div>
        </div>

        {/* Repository URL */}
        <div>
          <label className="block text-sm text-slate-400 mb-1">
            Git Repository URL
          </label>

          <input
            type="text"
            required
            value={form.url}
            onChange={(e) =>
              setForm({
                ...form,
                url: e.target.value,
              })
            }
            className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white"
            placeholder="https://github.com/user/repository.git"
          />
        </div>

        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-2 rounded transition"
        >
          Register Repository
        </button>
      </form>

      {/* Repository List */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-slate-100">
          Registered Repositories
        </h2>

        {loading ? (
          <p className="text-slate-400">
            Loading repositories...
          </p>
        ) : repositories.length === 0 ? (
          <p className="text-slate-500">
            No repositories registered yet.
          </p>
        ) : (
          <div className="divide-y divide-slate-800 border border-slate-800 rounded-lg bg-slate-900">
            {repositories.map((repo) => (
              <div
                key={repo.id}
                className="p-4 flex justify-between items-center"
              >
                <div>
                  <h3 className="font-medium text-white">
                    {repo.name}
                  </h3>

                  <p className="text-sm text-slate-400 font-mono">
                    {repo.url}
                  </p>
                </div>

                <span className="text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded">
                  Branch: {repo.default_branch}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}