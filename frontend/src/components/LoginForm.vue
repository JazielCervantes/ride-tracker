<template>
  <form class="rt-login-form" @submit.prevent="handleLogin">
    <div class="rt-field">
      <label for="username">Usuario</label>
      <input
        id="username"
        v-model="username"
        type="text"
        placeholder="Nombre de usuario"
        autocomplete="username"
        required
        :disabled="loading"
      />
    </div>

    <div class="rt-field">
      <label for="password">Contraseña</label>
      <input
        id="password"
        v-model="password"
        type="password"
        placeholder="Contraseña"
        autocomplete="current-password"
        required
        :disabled="loading"
      />
    </div>

    <p v-if="error" class="rt-error">{{ error }}</p>

    <button type="submit" :disabled="loading" class="rt-btn-primary">
      {{ loading ? 'Iniciando sesión...' : 'Iniciar sesión' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import { api } from '../lib/api.js';

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

async function handleLogin() {
  error.value = '';
  loading.value = true;
  try {
    await api.auth.login(username.value, password.value);
    localStorage.setItem('rt_username', username.value);
    window.location.href = '/';
  } catch (e) {
    console.error('[Login error]', e);
    if (e.message === 'Failed to fetch' || e.name === 'TypeError') {
      error.value = 'No se pudo conectar con el servidor. Verificá tu conexión o que el backend esté activo.';
    } else {
      error.value = e.message || 'Error al iniciar sesión';
    }
  } finally {
    loading.value = false;
  }
}
</script>
