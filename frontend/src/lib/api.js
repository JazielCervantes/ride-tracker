const API_URL = (import.meta.env.PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

async function request(path, options = {}) {
  const { skipAuthRedirect, ...fetchOptions } = options;
  const res = await fetch(`${API_URL}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...fetchOptions.headers },
    ...fetchOptions,
  });

  if (res.status === 401) {
    if (!skipAuthRedirect && typeof window !== 'undefined') {
      localStorage.removeItem('rt_username');
      window.location.href = '/login';
    }
    const err = await res.json().catch(() => ({ detail: 'No autenticado' }));
    throw new Error(err.detail || 'No autenticado');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error del servidor' }));
    throw new Error(err.detail || 'Error del servidor');
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  auth: {
    login: (username, password) =>
      request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }), skipAuthRedirect: true }),
    logout: () => request('/auth/logout', { method: 'POST' }),
    me: () => request('/auth/me'),
  },
  trips: {
    list: (weekStart) =>
      request(`/trips${weekStart ? `?week_start=${weekStart}` : ''}`),
    create: (data) =>
      request('/trips', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) =>
      request(`/trips/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) =>
      request(`/trips/${id}`, { method: 'DELETE' }),
  },
  weeks: {
    list: () => request('/weeks'),
    current: () => request('/weeks/current'),
    get: (weekStart) => request(`/weeks/${weekStart}`),
  },
};
