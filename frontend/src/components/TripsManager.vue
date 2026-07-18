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
      <button class="rt-btn-primary" @click="openCreate">
        <Icon name="plus" :size="16" /> Nuevo viaje
      </button>
    </div>

    <!-- Filtro de semana -->
    <div class="rt-filter-bar">
      <Icon name="filter" :size="15" class="rt-filter-icon" />
      <label for="week-select">Filtrar semana:</label>
      <select id="week-select" v-model="selectedWeek" @change="loadTrips">
        <option value="">Todos</option>
        <option v-for="ws in availableWeeks" :key="ws" :value="ws">
          {{ formatWeekRange(ws, weekEndFor(ws)) }}
        </option>
      </select>
    </div>

    <!-- Skeleton de carga -->
    <div v-if="loading" class="rt-table-wrapper" aria-busy="true" aria-label="Cargando viajes">
      <div class="rt-skel-table">
        <div class="rt-skeleton rt-skel-row rt-skel-row-header"></div>
        <div v-for="i in 4" :key="i" class="rt-skeleton rt-skel-row"></div>
      </div>
    </div>

    <!-- Tabla vacía -->
    <div v-else-if="trips.length === 0" class="rt-empty-state">
      <span class="rt-empty-icon"><Icon name="car" :size="26" /></span>
      <p>No hay viajes registrados{{ selectedWeek ? ' en esta semana' : '' }}.</p>
      <button class="rt-btn-primary rt-btn-sm" @click="openCreate">
        <Icon name="plus" :size="15" /> Registrar primer viaje
      </button>
    </div>

    <!-- Tabla de viajes -->
    <div v-else class="rt-table-wrapper">
      <!-- Resumen de semana -->
      <div v-if="selectedWeek" class="rt-week-summary-bar">
        <span>{{ trips.length }} viaje{{ trips.length !== 1 ? 's' : '' }}</span>
        <span class="rt-summary-income">Tarifas: <strong>${{ weekTotal.toFixed(2) }}</strong></span>
        <span v-if="weekTips > 0" class="rt-summary-tips">Propinas: <strong>${{ weekTips.toFixed(2) }}</strong></span>
        <span v-if="weekTips > 0" class="rt-summary-grand-total">Total: <strong>${{ weekGrandTotal.toFixed(2) }}</strong></span>
        <span class="rt-summary-payment">Cobro: {{ paymentDateLabel }}</span>
      </div>

      <table class="rt-table rt-trips-table">
        <thead>
          <tr>
            <th scope="col">Fecha</th>
            <th scope="col">Tipo</th>
            <th scope="col">Clientes</th>
            <th scope="col" class="text-right">Monto</th>
            <th scope="col">Notas</th>
            <th scope="col" class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trip in trips" :key="trip.id">
            <td>{{ formatDate(trip.date) }}</td>
            <td>
              <span class="rt-trip-type-badge" :class="trip.trip_type">
                <Icon :name="trip.trip_type === 'individual' ? 'user' : 'users'" :size="13" />
                {{ tripTypeLabel(trip.trip_type) }}
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
                <button class="rt-btn-icon" title="Editar" aria-label="Editar viaje" @click="openEdit(trip)">
                  <Icon name="pencil" :size="16" />
                </button>
                <button class="rt-btn-icon rt-btn-icon-danger" title="Eliminar" aria-label="Eliminar viaje" @click="confirmDelete(trip)">
                  <Icon name="trash" :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="actionError" class="rt-error" role="alert">
      <Icon name="alert-circle" :size="16" />
      <span>{{ actionError }}</span>
    </p>

    <!-- Modal TripForm -->
    <TripForm
      v-if="showForm"
      :trip="editingTrip"
      @close="closeForm"
      @saved="onTripSaved"
    />

    <!-- Confirmación de borrado -->
    <div v-if="deletingTrip" class="rt-modal-overlay" @click.self="deletingTrip = null">
      <div class="rt-modal rt-modal-sm" role="dialog" aria-modal="true" aria-label="Eliminar viaje">
        <div class="rt-modal-header">
          <h3>Eliminar viaje</h3>
          <button class="rt-modal-close" @click="deletingTrip = null" aria-label="Cerrar">
            <Icon name="x" :size="16" />
          </button>
        </div>
        <div class="rt-modal-body">
          <p>
            ¿Eliminar el viaje de <strong>{{ clientNames(deletingTrip) }}</strong>
            del {{ formatDate(deletingTrip.date) }}?
          </p>
          <p class="rt-error-msg">Esta acción no se puede deshacer.</p>
        </div>
        <div class="rt-modal-footer rt-modal-footer-pad">
          <button class="rt-btn-secondary" @click="deletingTrip = null" :disabled="deleting">Cancelar</button>
          <button class="rt-btn-danger" @click="doDelete" :disabled="deleting">
            {{ deleting ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast de confirmación -->
    <transition name="rt-toast">
      <div v-if="toast" class="rt-toast" role="status" aria-live="polite">
        <Icon name="check-circle" :size="17" />
        <span>{{ toast }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { api } from '../lib/api.js';
import { formatDate, formatWeekRange, getWeekEnd, getPaymentDate } from '../lib/dates.js';
import TripForm from './TripForm.vue';
import Icon from './Icon.vue';

const trips = ref([]);
const availableWeeks = ref([]);
const selectedWeek = ref('');
const loading = ref(true);
const actionError = ref('');
const showForm = ref(false);
const editingTrip = ref(null);
const deletingTrip = ref(null);
const deleting = ref(false);
const toast = ref('');
let toastTimer = null;

function weekEndFor(ws) { return getWeekEnd(ws); }

function tripTypeLabel(type) {
  return type === 'individual' ? 'Individual' : type === 'triple' ? 'Triple' : 'Par';
}

function clientNames(trip) {
  return [trip.client1_name, trip.client2_name, trip.client3_name].filter(Boolean).join(' & ');
}

function showToast(message) {
  toast.value = message;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.value = ''; }, 2600);
}

// Escape cierra el modal de confirmación de borrado
function onEscKey(e) {
  if (e.key === 'Escape' && deletingTrip.value && !deleting.value) {
    deletingTrip.value = null;
  }
}
watch(deletingTrip, (open) => {
  if (open) window.addEventListener('keydown', onEscKey);
  else window.removeEventListener('keydown', onEscKey);
});

onUnmounted(() => {
  clearTimeout(toastTimer);
  window.removeEventListener('keydown', onEscKey);
});

const weekTotal = computed(() =>
  trips.value.reduce((sum, t) => sum + Number(t.total_amount), 0)
);

const weekTips = computed(() =>
  trips.value.reduce((sum, t) => sum + Number(t.tip_amount || 0), 0)
);

const weekGrandTotal = computed(() => weekTotal.value + weekTips.value);

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
  showToast(editingTrip.value ? 'Viaje actualizado' : 'Viaje registrado');
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
    showToast('Viaje eliminado');
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
