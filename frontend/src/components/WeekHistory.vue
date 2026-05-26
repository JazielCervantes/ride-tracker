<template>
  <div class="rt-page">
    <div class="rt-page-header">
      <h2>Historial de semanas</h2>
    </div>

    <div v-if="loading" class="rt-loading"><p>Cargando semanas...</p></div>

    <div v-else-if="weeks.length === 0" class="rt-empty-state">
      <p>No hay semanas registradas aún.</p>
      <a href="/viajes" class="rt-btn-primary rt-btn-sm">Registrar primer viaje</a>
    </div>

    <div v-else>
      <!-- Tabla de semanas -->
      <div class="rt-table-wrapper">
        <table class="rt-table rt-week-history-table">
          <thead>
            <tr>
              <th>Semana</th>
              <th class="text-right rt-col-viajes">Viajes</th>
              <th class="text-right">Tarifas</th>
              <th class="text-right">Propinas</th>
              <th class="text-right">Total</th>
              <th class="rt-col-cobro">Fecha de cobro</th>
              <th></th>
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
                  <button class="rt-btn-text" @click="toggleWeek(week.week_start)">
                    Ver detalle ↓
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
                        <button class="rt-btn-text" @click="expandedWeek = null">Cerrar ↑</button>
                      </div>
                    </div>

                    <div v-if="detailLoading" class="rt-loading-sm"><p>Cargando viajes...</p></div>

                    <div v-else-if="!weekDetail?.trips?.length" class="rt-empty-state-sm">
                      <p>Sin viajes esta semana.</p>
                    </div>

                    <table v-else class="rt-table rt-detail-table">
                      <thead>
                        <tr>
                          <th>Fecha</th>
                          <th>Tipo</th>
                          <th>Clientes</th>
                          <th class="text-right">Tarifa</th>
                          <th class="text-right">Propina</th>
                          <th>Notas</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="trip in weekDetail.trips" :key="trip.id">
                          <td>{{ formatDate(trip.date) }}</td>
                          <td>
                            <span class="rt-trip-type-badge" :class="trip.trip_type">
                              {{ trip.trip_type === 'individual' ? '👤 Individual' : trip.trip_type === 'triple' ? '👥👤 Triple' : '👥 Par' }}
                            </span>
                          </td>
                          <td>
                            {{ trip.client1_name }}{{ trip.client2_name ? ` & ${trip.client2_name}` : '' }}{{ trip.client3_name ? ` & ${trip.client3_name}` : '' }}
                          </td>
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

    <p v-if="error" class="rt-error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../lib/api.js';
import { formatDate, formatWeekRange } from '../lib/dates.js';

const weeks = ref([]);
const loading = ref(true);
const error = ref('');
const expandedWeek = ref(null);
const weekDetail = ref(null);
const detailLoading = ref(false);

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
