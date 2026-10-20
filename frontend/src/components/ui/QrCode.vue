<script setup lang="ts">
import QRCode from 'qrcode'
import { ref, watchEffect } from 'vue'

const props = withDefaults(defineProps<{ value: string; size?: number; label?: string }>(), { size: 160 })
const src = ref<string>('')

// El QR siempre se dibuja oscuro sobre blanco para que lo lea cualquier cámara.
function tinta(): string {
  return getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#111113'
}

watchEffect(async () => {
  try {
    src.value = await QRCode.toDataURL(props.value, {
      width: props.size * 2,
      margin: 1,
      errorCorrectionLevel: 'M',
      color: { dark: tinta(), light: '#FFFFFF' },
    })
  } catch {
    src.value = ''
  }
})
</script>

<template>
  <img
    v-if="src"
    :src="src"
    :width="size"
    :height="size"
    :alt="label ?? 'Código QR'"
    class="rounded-xl bg-white p-1.5"
  />
</template>
