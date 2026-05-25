<template>
  <div class="rt-page">
    <div class="rt-page-header">
      <div>
        <h2>Viajes</h2>
        <p v-if="selectedWeek" class="rt-page-subtitle">
          Semana del {{ formatWeekRange(selectedWeek, weekEndFor(selectedWeek)) }}
        </p>
        <p v-else class="rt-page-subtitle">Todos los viajes</p>
      </div>
      <button class="rt-btn-primary" @click="openCreate">+ Nuevo viaje</button>
    </div>

    <!-- Filtro de semana -->
    <div class="rt-filter-bar">
      <label for="week-select">Filtrar semana:</label>
      <select id="week-select" v-model="selectedWeek" @change="loadTrips">
        <option value="">Todos</option>
        <option v-for="ws in availableWeeks" :key="ws" :value="ws">
          {{ formatWeekRange(ws, weekEndFor(ws)) }}
        </option>
      </select>
    </div>

    <!-- Carga -->
    <div v-if="loading" class="rt-loading"><p>Cargando viajes...</p></div>

    <!-- Tabla vacía -->
    <div v-else-if="trips.length === 0" class="rt-empty-state">
      <p>No hay viajes registrados{{ selectedWeek ? ' en esta semana' : '' }}.</p>
      <button class="rt-btn-primary rt-btn-sm" @click="openCreate">+ Registrar primer viaje</button>
    </div>

    <!-- Tabla de viajes -->
    <div v-else class="rt-table-wrapper">
      <!-- Resumen de semana -->
      <div v-if="selectedWeek" class="rt-week-summary-bar">
        <span>{{ trips.length }} viaje{{ trips.length !== 1 ? 's' : '' }}</span>
        <span class="rt-summary-income">Tarifas: <strong>${{ weekTotal.toFixed(2) }}</strong></span>
        <span v-if="weekTips > 0" class="rt-summary-tips">Propinas: <strong>${{ weekTips.toFixed(2) }}</strong></span>
        <span class="rt-summary-payment">Cobro: {{ paymentDateLabel }}</span>
      </div>

      <table class="rt-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Tipo</th>
            <th>Clientes</th>
            <th class="text-right">Monto</th>
            <th>Notas</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trip in trips" :key="trip.id">
            <td>{{ formatDate(trip.date) }}</td>
            <td>
              <span class="rt-trip-type-badge" :class="trip.trip_type">
                {{ trip.trip_type === 'individual' ? '👤 Individual' : trip.trip_type === 'triple' ? '👥👤 Triple' : '👥 Par' }}
              </span>
            </td>
            <td class="rt-clients-cell">
              <div>{{ trip.client1_name }}</div>
              <div v-if="trip.client2_name" class="rt-client2">{{ trip.client2_name }}</div>
              <div v-if="trip.client3_name" class="rt-client2">{{ trip.client3_name }}</div>
            </td>
            <td class="text-right rt-amount-cell">
              ${{ Number(trip.total_amount).toFixed(2) }}
              <div v-if="Number(trip.tip_amount) > 0" class="rt-tip-sub">+${{ Number(trip.tip_amount).toFixed(2) }} prop.</div>
            </td>
            <td class="rt-notes-cell">{{ trip.notes || '—' }}</td>
            <td class="text-right">
              <div class="rt-actions">
                <button class="rt-btn-icon" title="Editar" @click="openEdit(trip)">✏️</button>
                <button class="rt-btn-icon rt-btn-danger" title="Eliminar" @click="confirmDelete(trip)">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="actionError" class="rt-error">{{ actionError }}</p>

    <!-- Modal TripForm -->
    <TripForm
      v-if="showForm"
      :trip="editingTrip"
      @close="closeForm"
      @saved="onTripSaved"
    />

    <!-- Confirmación de borrado -->
    <div v-if="deletingTrip" class="rt-modal-overlay" @click.self="deletingTrip = null">
      <div class="rt-modal rt-modal-sm">
        <div class="rt-modal-header">
          <h3>Eliminar viaje</h3>
        </div>
        <div class="rt-modal-body">
          <p>
            ¿Eliminar el viaje de <strong>{{ deletingTrip.client1_name }}</strong>
            {{ deletingTrip.client2_name ? `& ${deletingTrip.client2_name}` : '' }}
            del {{ formatDate(deletingTrip.date) }}?
          </p>
          <p class="rt-error-msg">Esta acción no se puede deshacer.</p>
        </div>
        <div class="rt-modal-footer">
          <button class="rt-btn-secondary" @click="deletingTrip = null" :disabled="deleting">Cancelar</button>
          <button class="rt-btn-danger" @click="doDelete" :disabled="deleting">
            {{ deleting ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../lib/api.js';
import { formatDate, formatWeekRange, getWeekEnd, getPaymentDate, today } from '../lib/dates.js';
import TripForm from './TripForm.vue';

const trips = ref([]);
const availableWeeks = ref([]);
const selectedWeek = ref('');
const loading = ref(true);
const actionError = ref('');
const showForm = ref(false);
const editingTrip = ref(null);
const deletingTrip = ref(null);
const deleting = ref(false);

function weekEndFor(ws) { return getWeekEnd(ws); }

const weekTotal = computed(() =>
  trips.value.reduce((sum, t) => sum + Number(t.total_amount), 0)
);

const weekTips = computed(() =>
  trips.value.reduce((sum, t) => sum + Number(t.tip_amount || 0), 0)
);

const paymentDateLabel = computed(() => {
  if (!selectedWeek.value) return '';
  return formatDate(getPaymentDate(selectedWeek.value));
});

async function loadTrips() {
  loading.value = true;
  actionError.value = '';
  try {
    trips.value = await api.trips.list(selectedWeek.value || undefined);
  } catch (e) {
    if (e.message !== 'No autenticado') actionError.value = e.message;
  } finally {
    loading.value = false;
  }
}

async function loadWeeks() {
  try {
    const weeks = await api.weeks.list();
    availableWeeks.value = weeks.map(w => w.week_start);
    // Seleccionar la semana actual por defecto
    if (availableWeeks.value.length > 0) {
      selectedWeek.value = availableWeeks.value[0];
    }
  } catch (_) {
    // Ignorar error de semanas
  }
}

function openCreate() {
  editingTrip.value = null;
  showForm.value = true;
}

function openEdit(trip) {
  editingTrip.value = trip;
  showForm.value = true;
}

function closeForm() {
  showForm.value = false;
  editingTrip.value = null;
}

function onTripSaved() {
  loadTrips();
  loadWeeks();
}

function confirmDelete(trip) {
  deletingTrip.value = trip;
}

async function doDelete() {
  deleting.value = true;
  try {
    await api.trips.delete(deletingTrip.value.id);
    deletingTrip.value = null;
    loadTrips();
    loadWeeks();
  } catch (e) {
    actionError.value = e.message;
  } finally {
    deleting.value = false;
  }
}

onMounted(async () => {
  await loadWeeks();
  await loadTrips();
});
</script>
