<template>
  <div class="rt-page">
    <div class="rt-page-header">
      <div>
        <h2>Historial de semanas</h2>
        <p class="rt-page-subtitle">Semanas de miércoles a martes · cobro el viernes siguiente</p>
      </div>
    </div>

    <!-- Skeleton de carga -->
    <div v-if="loading" class="rt-table-wrapper" aria-busy="true" aria-label="Cargando semanas">
      <div class="rt-skel-table">
        <div class="rt-skeleton rt-skel-row rt-skel-row-header"></div>
        <div v-for="i in 4" :key="i" class="rt-skeleton rt-skel-row"></div>
      </div>
    </div>

    <div v-else-if="weeks.length === 0" class="rt-empty-state">
      <span class="rt-empty-icon"><Icon name="calendar" :size="26" /></span>
      <p>No hay semanas registradas aún.</p>
      <a href="/viajes" class="rt-btn-primary rt-btn-sm"><Icon name="plus" :size="15" /> Registrar primer viaje</a>
    </div>

    <div v-else>
      <!-- Tabla de semanas -->
      <div class="rt-table-wrapper">
        <table class="rt-table rt-week-history-table">
          <thead>
            <tr>
              <th scope="col">Semana</th>
              <th scope="col" class="text-right rt-col-viajes">Viajes</th>
              <th scope="col" class="text-right">Tarifas</th>
              <th scope="col" class="text-right">Propinas</th>
              <th scope="col" class="text-right">Total</th>
              <th scope="col" class="rt-col-cobro">Fecha de cobro</th>
              <th scope="col"><span class="rt-visually-hidden">Detalle</span></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="week in weeks"
              :key="week.week_start"
              class="rt-week-row"
              :class="{ expanded: expandedWeek === week.week_start }"
            >
              <template v-if="expandedWeek !== week.week_start">
                <td>{{ formatWeekRange(week.week_start, week.week_end) }}</td>
                <td class="text-right rt-col-viajes">{{ week.total_trips }}</td>
                <td class="text-right rt-amount-cell">${{ Number(week.total_income).toFixed(2) }}</td>
                <td class="text-right rt-amount-cell rt-tips-cell">
                  {{ Number(week.total_tips ?? 0) > 0 ? '$' + Number(week.total_tips).toFixed(2) : '—' }}
                </td>
                <td class="text-right rt-amount-cell rt-grand-total-cell">
                  ${{ (Number(week.total_income) + Number(week.total_tips ?? 0)).toFixed(2) }}
                </td>
                <td class="rt-col-cobro">{{ formatDate(week.payment_date) }}</td>
                <td class="text-right">
                  <button class="rt-btn-text" aria-label="Ver detalle de la semana" @click="toggleWeek(week.week_start)">
                    <span class="rt-btn-text-label">Ver detalle</span> <Icon name="chevron-down" :size="14" />
                  </button>
                </td>
              </template>
              <template v-else>
                <!-- Fila expandida — ocupa toda la tabla -->
                <td colspan="7" class="rt-week-detail-cell">
                  <div class="rt-week-detail">
                    <div class="rt-week-detail-header">
                      <div>
                        <strong>{{ formatWeekRange(week.week_start, week.week_end) }}</strong>
                        <span class="rt-detail-meta">Cobro: {{ formatDate(week.payment_date) }}</span>
                      </div>
                      <div class="rt-detail-totals">
                        <span>{{ weekDetail?.total_trips ?? '...' }} viajes</span>
                        <span class="rt-income-highlight">${{ Number(weekDetail?.total_income ?? 0).toFixed(2) }} tarifas</span>
                        <span v-if="Number(weekDetail?.total_tips) > 0" class="rt-income-tips-sm">+${{ Number(weekDetail?.total_tips ?? 0).toFixed(2) }} prop.</span>
                        <span v-if="Number(weekDetail?.total_tips) > 0" class="rt-income-grand-total">= ${{ (Number(weekDetail?.total_income ?? 0) + Number(weekDetail?.total_tips ?? 0)).toFixed(2) }} total</span>
                        <button class="rt-btn-text" aria-label="Cerrar detalle" @click="expandedWeek = null">
                          <span class="rt-btn-text-label">Cerrar</span> <Icon name="chevron-up" :size="14" />
                        </button>
                      </div>
                    </div>

                    <div v-if="detailLoading" class="rt-loading-sm"><p>Cargando viajes...</p></div>

                    <div v-else-if="!weekDetail?.trips?.length" class="rt-empty-state-sm">
                      <p>Sin viajes esta semana.</p>
                    </div>

                    <table v-else class="rt-table rt-detail-table">
                      <thead>
                        <tr>
                          <th scope="col">Fecha</th>
                          <th scope="col">Tipo</th>
                          <th scope="col">Clientes</th>
                          <th scope="col" class="text-right">Tarifa</th>
                          <th scope="col" class="text-right">Propina</th>
                          <th scope="col">Notas</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="trip in weekDetail.trips" :key="trip.id">
                          <td>{{ formatDate(trip.date) }}</td>
                          <td>
                            <span class="rt-trip-type-badge" :class="trip.trip_type">
                              <Icon :name="trip.trip_type === 'individual' ? 'user' : 'users'" :size="13" />
                              {{ tripTypeLabel(trip.trip_type) }}
                            </span>
                          </td>
                          <td>{{ clientNames(trip) }}</td>
                          <td class="text-right rt-amount-cell">${{ Number(trip.total_amount).toFixed(2) }}</td>
                          <td class="text-right rt-amount-cell">
                            {{ Number(trip.tip_amount) > 0 ? '$' + Number(trip.tip_amount).toFixed(2) : '—' }}
                          </td>
                          <td>{{ trip.notes || '—' }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p v-if="error" class="rt-error" role="alert">
      <Icon name="alert-circle" :size="16" />
      <span>{{ error }}</span>
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../lib/api.js';
import { formatDate, formatWeekRange } from '../lib/dates.js';
import Icon from './Icon.vue';

const weeks = ref([]);
const loading = ref(true);
const error = ref('');
const expandedWeek = ref(null);
const weekDetail = ref(null);
const detailLoading = ref(false);

function tripTypeLabel(type) {
  return type === 'individual' ? 'Individual' : type === 'triple' ? 'Triple' : 'Par';
}

function clientNames(trip) {
  return [trip.client1_name, trip.client2_name, trip.client3_name].filter(Boolean).join(' & ');
}

async function toggleWeek(weekStart) {
  if (expandedWeek.value === weekStart) {
    expandedWeek.value = null;
    weekDetail.value = null;
    return;
  }
  expandedWeek.value = weekStart;
  weekDetail.value = null;
  detailLoading.value = true;
  try {
    weekDetail.value = await api.weeks.get(weekStart);
  } catch (e) {
    error.value = e.message;
  } finally {
    detailLoading.value = false;
  }
}

onMounted(async () => {
  try {
    weeks.value = await api.weeks.list();
  } catch (e) {
    if (e.message !== 'No autenticado') error.value = e.message;
  } finally {
    loading.value = false;
  }
});
</script>
