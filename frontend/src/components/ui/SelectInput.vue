<script setup lang="ts">
import { ChevronDown } from '@lucide/vue'
import { useId } from 'vue'
import { useAtributosDeCampo } from '@/composables/useAtributosDeCampo'
import FormField from './FormField.vue'

defineOptions({ inheritAttrs: false })

export interface Opcion {
  value: string | number | null
  label: string
  disabled?: boolean
}

const props = withDefaults(
  defineProps<{
    label?: string
    hint?: string
    error?: string | null
    required?: boolean
    id?: string
    options: Opcion[]
    placeholder?: string
    size?: 'md' | 'lg'
  }>(),
  { size: 'md' },
)
const modelo = defineModel<string | number | null>()
const idFinal = props.id ?? useId()
const { raiz, control } = useAtributosDeCampo()
</script>

<template>
  <FormField v-bind="raiz" :id="idFinal" :label="label" :hint="hint" :error="error" :required="required">
    <template #default="{ describedby, invalid }">
      <div class="relative">
        <select
          :id="idFinal"
          v-model="modelo"
          v-bind="control"
          :required="required"
          :aria-invalid="invalid || undefined"
          :aria-describedby="describedby"
          class="w-full appearance-none rounded-full border bg-surface-2 pr-10 pl-4 text-[15px] text-fg outline-none transition-colors focus:border-accent-line focus:ring-4 focus:ring-(--ring)"
          :class="[invalid ? 'border-danger' : 'border-line', size === 'lg' ? 'h-14' : 'h-11']"
        >
          <option v-if="placeholder" :value="null" disabled>{{ placeholder }}</option>
          <option v-for="o in options" :key="String(o.value)" :value="o.value" :disabled="o.disabled">
            {{ o.label }}
          </option>
        </select>
        <ChevronDown class="pointer-events-none absolute top-1/2 right-3.5 size-4 -translate-y-1/2 text-muted" aria-hidden="true" />
      </div>
    </template>
  </FormField>
</template>
