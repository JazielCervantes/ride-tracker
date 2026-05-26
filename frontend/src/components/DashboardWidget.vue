<template>
  <div class="rt-dashboard">
    <!-- Estado de carga -->
    <div v-if="loading" class="rt-loading">
      <p>Cargando...</p>
    </div>

    <template v-else>
      <!-- Semana actual -->
      <section class="rt-week-header">
        <h2 class="rt-week-title">Semana actual</h2>
        <p class="rt-week-range">{{ weekRange }}</p>
      </section>

      <!-- Tarjeta principal: Total a cobrar -->
      <div class="rt-income-card">
        <div class="rt-income-label">A cobrar el {{ paymentDateFormatted }}</div>
        <div class="rt-income-amount">${{ grandTotal.toFixed(2) }}</div>
        <div v-if="totalTips > 0" class="rt-income-tips">
          ${{ totalIncome.toFixed(2) }} tarifas + ${{ totalTips.toFixed(2) }} propinas
        </div>
        <div class="rt-income-meta">{{ totalTrips }} viaje{{ totalTrips !== 1 ? 's' : '' }} esta semana</div>
      </div>

      <!-- Estadísticas rápidas -->
      <div class="rt-stats-grid">
        <div class="rt-stat-card">
          <div class="rt-stat-value">{{ individualTrips }}</div>
          <div class="rt-stat-label">Individuales</div>
          <div class="rt-stat-sub">${{ (individualTrips * 30).toFixed(0) }}</div>
        </div>
        <div class="rt-stat-card">
          <div class="rt-stat-value">{{ pairTrips }}</div>
          <div class="rt-stat-label">En par</div>
          <div class="rt-stat-sub">${{ (pairTrips * 50).toFixed(0) }}</div>
        </div>
        <div class="rt-stat-card">
          <div class="rt-stat-value">{{ tripleTrips }}</div>
          <div class="rt-stat-label">Triple</div>
          <div class="rt-stat-sub">${{ (tripleTrips * 75).toFixed(0) }}</div>
        </div>
        <div class="rt-stat-card">
          <div class="rt-stat-value">{{ todayTrips.length }}</div>
          <div class="rt-stat-label">Hoy</div>
          <div class="rt-stat-sub">{{ todayDateStr }}</div>
        </div>
      </div>

      <!-- Viajes de hoy -->
      <section class="rt-today-section">
        <div class="rt-section-header">
          <h3>Viajes de hoy</h3>
          <a href="/viajes" class="rt-link-btn">Ver todos →</a>
        </div>

        <div v-if="todayTrips.length === 0" class="rt-empty-state">
          <p>Sin viajes registrados hoy</p>
          <a href="/viajes" class="rt-btn-primary rt-btn-sm">+ Agregar viaje</a>
        </div>

        <ul v-else class="rt-trip-list">
          <li v-for="trip in todayTrips" :key="trip.id" class="rt-trip-item">
            <div class="rt-trip-info">
              <span class="rt-trip-type-badge" :class="trip.trip_type">
                {{ trip.trip_type === 'individual' ? '👤' : trip.trip_type === 'triple' ? '👥👤' : '👥' }}
                {{ trip.trip_type === 'individual' ? 'Individual' : trip.trip_type === 'triple' ? 'Triple' : 'Par' }}
              </span>
              <span class="rt-trip-clients">
                {{ trip.client1_name }}{{ trip.client2_name ? ` & ${trip.client2_name}` : '' }}
              </span>
            </div>
            <span class="rt-trip-amount">${{ Number(trip.total_amount).toFixed(2) }}</span>
          </li>
        </ul>
      </section>

      <!-- Acceso rápido -->
      <div class="rt-quick-actions">
        <a href="/viajes" class="rt-btn-primary">+ Registrar viaje</a>
        <a href="/semanas" class="rt-btn-secondary">Ver historial</a>
      </div>
    </template>

    <p v-if="error" class="rt-error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../lib/api.js';
import { formatWeekRange, formatDate, today } from '../lib/dates.js';

const loading = ref(true);
const error = ref('');
const weekData = ref(null);

const todayStr = today();
const todayDateStr = formatDate(todayStr);

const weekRange = computed(() => {
  if (!weekData.value) return '';
  return formatWeekRange(weekData.value.week_start, weekData.value.week_end);
});

const paymentDateFormatted = computed(() => {
  if (!weekData.value) return '';
  return formatDate(weekData.value.payment_date);
});

const totalIncome = computed(() => Number(weekData.value?.total_income ?? 0));
const totalTips = computed(() => Number(weekData.value?.total_tips ?? 0));
const grandTotal = computed(() => totalIncome.value + totalTips.value);
const totalTrips = computed(() => weekData.value?.total_trips ?? 0);

const todayTrips = computed(() => {
  if (!weekData.value?.trips) return [];
  return weekData.value.trips.filter(t => t.date === todayStr);
});

const individualTrips = computed(() => {
  if (!weekData.value?.trips) return 0;
  return weekData.value.trips.filter(t => t.trip_type === 'individual').length;
});

const pairTrips = computed(() => {
  if (!weekData.value?.trips) return 0;
  return weekData.value.trips.filter(t => t.trip_type === 'pair').length;
});

const tripleTrips = computed(() => {
  if (!weekData.value?.trips) return 0;
  return weekData.value.trips.filter(t => t.trip_type === 'triple').length;
});

onMounted(async () => {
  try {
    weekData.value = await api.weeks.current();
  } catch (e) {
    if (e.message !== 'No autenticado') {
      error.value = e.message;
    }
  } finally {
    loading.value = false;
  }
});
</script>
