<template>
  <div class="rt-dashboard">
    <!-- Skeleton de carga -->
    <div v-if="loading" class="rt-skel-stack" aria-busy="true" aria-label="Cargando datos de la semana">
      <div>
        <div class="rt-skeleton rt-skel-title"></div>
        <div class="rt-skeleton rt-skel-subtitle"></div>
      </div>
      <div class="rt-skeleton rt-skel-hero"></div>
      <div class="rt-stats-grid">
        <div v-for="i in 4" :key="i" class="rt-skeleton rt-skel-stat"></div>
      </div>
      <div class="rt-skeleton rt-skel-block"></div>
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
        <span v-if="paymentCountdown" class="rt-income-chip">
          <Icon name="clock" :size="14" />
          {{ paymentCountdown }}
        </span>
      </div>

      <!-- Estadísticas rápidas -->
      <div class="rt-stats-grid">
        <div class="rt-stat-card">
          <span class="rt-stat-icon is-individual"><Icon name="user" :size="16" /></span>
          <div class="rt-stat-value">{{ individualTrips.length }}</div>
          <div class="rt-stat-label">Individuales</div>
          <div class="rt-stat-sub">${{ sumAmounts(individualTrips).toFixed(0) }}</div>
        </div>
        <div class="rt-stat-card">
          <span class="rt-stat-icon is-pair"><Icon name="users" :size="16" /></span>
          <div class="rt-stat-value">{{ pairTrips.length }}</div>
          <div class="rt-stat-label">En par</div>
          <div class="rt-stat-sub">${{ sumAmounts(pairTrips).toFixed(0) }}</div>
        </div>
        <div class="rt-stat-card">
          <span class="rt-stat-icon is-triple"><Icon name="users" :size="16" /></span>
          <div class="rt-stat-value">{{ tripleTrips.length }}</div>
          <div class="rt-stat-label">Triple</div>
          <div class="rt-stat-sub">${{ sumAmounts(tripleTrips).toFixed(0) }}</div>
        </div>
        <div class="rt-stat-card">
          <span class="rt-stat-icon is-today"><Icon name="calendar" :size="16" /></span>
          <div class="rt-stat-value">{{ todayTrips.length }}</div>
          <div class="rt-stat-label">Hoy</div>
          <div class="rt-stat-sub">{{ todayDateStr }}</div>
        </div>
      </div>

      <!-- Viajes de hoy -->
      <section class="rt-today-section">
        <div class="rt-section-header">
          <h3>Viajes de hoy</h3>
          <a href="/viajes" class="rt-link-btn">Ver todos <Icon name="chevron-right" :size="14" /></a>
        </div>

        <div v-if="todayTrips.length === 0" class="rt-empty-state">
          <span class="rt-empty-icon"><Icon name="car" :size="26" /></span>
          <p>Sin viajes registrados hoy</p>
          <a href="/viajes" class="rt-btn-primary rt-btn-sm"><Icon name="plus" :size="15" /> Agregar viaje</a>
        </div>

        <ul v-else class="rt-trip-list">
          <li v-for="trip in todayTrips" :key="trip.id" class="rt-trip-item">
            <div class="rt-trip-info">
              <span class="rt-trip-type-badge" :class="trip.trip_type">
                <Icon :name="trip.trip_type === 'individual' ? 'user' : 'users'" :size="13" />
                {{ tripTypeLabel(trip.trip_type) }}
              </span>
              <span class="rt-trip-clients">{{ clientNames(trip) }}</span>
            </div>
            <span class="rt-trip-amount">${{ Number(trip.total_amount).toFixed(2) }}</span>
          </li>
        </ul>
      </section>

      <!-- Acceso rápido -->
      <div class="rt-quick-actions">
        <a href="/viajes" class="rt-btn-primary"><Icon name="plus" :size="16" /> Registrar viaje</a>
        <a href="/semanas" class="rt-btn-secondary"><Icon name="calendar" :size="16" /> Ver historial</a>
      </div>
    </template>

    <p v-if="error" class="rt-error" role="alert">
      <Icon name="alert-circle" :size="16" />
      <span>{{ error }}</span>
    </p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../lib/api.js';
import { formatWeekRange, formatDate, today } from '../lib/dates.js';
import Icon from './Icon.vue';

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

const paymentCountdown = computed(() => {
  if (!weekData.value) return '';
  const [y, m, d] = weekData.value.payment_date.split('-').map(Number);
  const payment = new Date(y, m - 1, d);
  const now = new Date();
  const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const days = Math.round((payment - todayMidnight) / 86400000);
  if (days < 0) return '';
  if (days === 0) return '¡Cobrás hoy!';
  if (days === 1) return 'Cobrás mañana';
  return `Faltan ${days} días para el cobro`;
});

const todayTrips = computed(() => {
  if (!weekData.value?.trips) return [];
  return weekData.value.trips.filter(t => t.date === todayStr);
});

const individualTrips = computed(() =>
  (weekData.value?.trips ?? []).filter(t => t.trip_type === 'individual')
);
const pairTrips = computed(() =>
  (weekData.value?.trips ?? []).filter(t => t.trip_type === 'pair')
);
const tripleTrips = computed(() =>
  (weekData.value?.trips ?? []).filter(t => t.trip_type === 'triple')
);

function sumAmounts(trips) {
  return trips.reduce((sum, t) => sum + Number(t.total_amount), 0);
}

function tripTypeLabel(type) {
  return type === 'individual' ? 'Individual' : type === 'triple' ? 'Triple' : 'Par';
}

function clientNames(trip) {
  return [trip.client1_name, trip.client2_name, trip.client3_name].filter(Boolean).join(' & ');
}

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
