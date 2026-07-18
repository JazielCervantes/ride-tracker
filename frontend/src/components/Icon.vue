<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="rt-icon"
    aria-hidden="true"
    v-html="path"
  ></svg>
</template>

<script setup>
import { computed } from 'vue';
import { ICON_PATHS } from '../lib/icons.js';

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 18 },
});

// Paths estáticos del proyecto (icons.js), nunca input del usuario
const path = computed(() => ICON_PATHS[props.name] || '');
</script>
