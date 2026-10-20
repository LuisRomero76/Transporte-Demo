<script setup lang="ts">
import { onBeforeUnmount, watchEffect } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { onSesionExpirada } from '@/api/client'
import ToastHost from '@/components/ui/ToastHost.vue'
import { useAuthStore } from '@/stores/auth'
import { useTemaStore } from '@/stores/tema'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const avisos = useToastStore()
const tema = useTemaStore()

// El tema vive en <html> para que también cubra los diálogos montados en <body>.
// El portal de clientes es siempre claro; el modo oscuro es solo del panel de operación.
watchEffect(() => {
  const oscuro = route.path.startsWith('/admin') && tema.oscuro
  document.documentElement.dataset.theme = oscuro ? 'dark' : 'light'
  const fondo = getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()
  if (fondo) document.querySelector('meta[name="theme-color"]')?.setAttribute('content', fondo)
})

// Si una llamada del panel responde 401, la sesión expiró: volver al inicio de sesión.
const quitar = onSesionExpirada(() => {
  if (auth.estado !== 'autenticado') return
  auth.olvidar()
  avisos.info('Tu sesión expiró', 'Vuelve a iniciar sesión para continuar.')
  void router.push({ name: 'admin-login', query: { siguiente: router.currentRoute.value.fullPath } })
})
onBeforeUnmount(quitar)
</script>

<template>
  <a
    href="#contenido"
    class="sr-only z-[70] rounded-full bg-pill-active px-4 py-2 font-semibold text-pill-active-fg focus:not-sr-only focus:fixed focus:top-3 focus:left-3"
  >
    Saltar al contenido
  </a>
  <RouterView />
  <ToastHost />
</template>
