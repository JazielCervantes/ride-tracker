<template>
  <!-- Overlay -->
  <div class="rt-modal-overlay" @click.self="$emit('close')">
    <div class="rt-modal" role="dialog" :aria-label="trip ? 'Editar viaje' : 'Nuevo viaje'">
      <div class="rt-modal-header">
        <h3>{{ trip ? 'Editar viaje' : 'Nuevo viaje' }}</h3>
        <button class="rt-modal-close" @click="$emit('close')" aria-label="Cerrar">✕</button>
      </div>

      <form class="rt-modal-body" @submit.prevent="handleSubmit">
        <!-- Fecha -->
        <div class="rt-field">
          <label for="tf-date">Fecha</label>
          <input id="tf-date" v-model="form.date" type="date" required :max="todayStr" />
        </div>

        <!-- Tipo de viaje -->
        <div class="rt-field">
          <label>Tipo de viaje</label>
          <div class="rt-radio-group">
            <label class="rt-radio-option" :class="{ selected: form.trip_type === 'individual' }">
              <input v-model="form.trip_type" type="radio" value="individual" />
              <span>👤 Individual <small>$30</small></span>
            </label>
            <label class="rt-radio-option" :class="{ selected: form.trip_type === 'pair' }">
              <input v-model="form.trip_type" type="radio" value="pair" />
              <span>👥 En par <small>$25 c/u</small></span>
            </label>
            <label class="rt-radio-option" :class="{ selected: form.trip_type === 'triple' }">
              <input v-model="form.trip_type" type="radio" value="triple" />
              <span>👥👤 Triple <small>$25 c/u</small></span>
            </label>
          </div>
        </div>

        <!-- Cliente 1 -->
        <div class="rt-field">
          <label for="tf-client1">
            {{ form.trip_type === 'individual' ? 'Cliente' : 'Cliente 1' }}
          </label>
          <input
            id="tf-client1"
            v-model="form.client1_name"
            type="text"
            placeholder="Nombre del cliente"
            required
          />
        </div>

        <!-- Cliente 2 (para par y triple) -->
        <div v-if="form.trip_type === 'pair' || form.trip_type === 'triple'" class="rt-field">
          <label for="tf-client2">Cliente 2</label>
          <input
            id="tf-client2"
            v-model="form.client2_name"
            type="text"
            placeholder="Nombre del segundo cliente"
            required
          />
        </div>

        <!-- Cliente 3 (solo para triple) -->
        <div v-if="form.trip_type === 'triple'" class="rt-field">
          <label for="tf-client3">Cliente 3</label>
          <input
            id="tf-client3"
            v-model="form.client3_name"
            type="text"
            placeholder="Nombre del tercer cliente"
            required
          />
        </div>

        <!-- Notas -->
        <div class="rt-field">
          <label for="tf-notes">Notas <small>(opcional)</small></label>
          <textarea id="tf-notes" v-model="form.notes" rows="2" placeholder="Observaciones..."></textarea>
        </div>

        <!-- Propina -->
        <div class="rt-field">
          <label for="tf-tip">Propina <small>(opcional)</small></label>
          <input
            id="tf-tip"
            v-model.number="form.tip_amount"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
          />
        </div>

        <!-- Resumen de monto -->
        <div class="rt-amount-preview">
          <span>Tarifa:</span>
          <strong>${{ amountPreview }}</strong>
          <template v-if="form.tip_amount > 0">
            <span> + ${{ Number(form.tip_amount).toFixed(2) }} propina
              = <strong>${{ (parseFloat(amountPreview) + (parseFloat(form.tip_amount) || 0)).toFixed(2) }}</strong>
            </span>
          </template>
        </div>

        <p v-if="error" class="rt-error">{{ error }}</p>

        <div class="rt-modal-footer">
          <button type="button" class="rt-btn-secondary" @click="$emit('close')" :disabled="loading">
            Cancelar
          </button>
          <button type="submit" class="rt-btn-primary" :disabled="loading">
            {{ loading ? 'Guardando...' : (trip ? 'Guardar cambios' : 'Agregar viaje') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { api } from '../lib/api.js';
import { today } from '../lib/dates.js';

const props = defineProps({
  trip: { type: Object, default: null },
});

const emit = defineEmits(['close', 'saved']);

const todayStr = today();

const form = ref({
  date: props.trip?.date ?? todayStr,
  trip_type: props.trip?.trip_type ?? 'individual',
  client1_name: props.trip?.client1_name ?? '',
  client2_name: props.trip?.client2_name ?? '',
  client3_name: props.trip?.client3_name ?? '',
  tip_amount: props.trip?.tip_amount ? Number(props.trip.tip_amount) : 0,
  notes: props.trip?.notes ?? '',
});

const loading = ref(false);
const error = ref('');

// Limpiar nombres de clientes extra al cambiar tipo
watch(() => form.value.trip_type, (newType) => {
  if (newType === 'individual') {
    form.value.client2_name = '';
    form.value.client3_name = '';
  } else if (newType === 'pair') {
    form.value.client3_name = '';
  }
});

const amountPreview = computed(() => {
  if (form.value.trip_type === 'individual') return '30.00';
  if (form.value.trip_type === 'triple') return '75.00';
  return '50.00';
});

async function handleSubmit() {
  error.value = '';
  loading.value = true;

  const data = {
    date: form.value.date,
    trip_type: form.value.trip_type,
    client1_name: form.value.client1_name.trim(),
    tip_amount: parseFloat(form.value.tip_amount) || 0,
    notes: form.value.notes.trim(),
  };

  if (form.value.trip_type === 'pair') {
    data.client2_name = form.value.client2_name.trim();
  }

  if (form.value.trip_type === 'triple') {
    data.client2_name = form.value.client2_name.trim();
    data.client3_name = form.value.client3_name.trim();
  }

  try {
    let result;
    if (props.trip) {
      result = await api.trips.update(props.trip.id, data);
    } else {
      result = await api.trips.create(data);
    }
    emit('saved', result);
    emit('close');
  } catch (e) {
    error.value = e.message || 'Error al guardar el viaje';
  } finally {
    loading.value = false;
  }
}
</script>
