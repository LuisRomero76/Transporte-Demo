<script setup lang="ts">
import { useId } from 'vue'
import { useAtributosDeCampo } from '@/composables/useAtributosDeCampo'
import FormField from './FormField.vue'

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    label?: string
    hint?: string
    error?: string | null
    required?: boolean
    id?: string
    mono?: boolean
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
      <div
        class="flex items-center gap-2.5 rounded-full border bg-surface-2 px-4 transition-colors focus-within:border-accent-line focus-within:ring-4 focus-within:ring-(--ring)"
        :class="[invalid ? 'border-danger' : 'border-line', size === 'lg' ? 'h-14' : 'h-11']"
      >
        <slot name="icono" />
        <input
          :id="idFinal"
          v-model="modelo"
          v-bind="control"
          :required="required"
          :aria-invalid="invalid || undefined"
          :aria-describedby="describedby"
          class="w-full min-w-0 bg-transparent text-[15px] text-fg outline-none placeholder:text-muted"
          :class="mono ? 'codigo tracking-widest placeholder:font-sans placeholder:tracking-normal' : ''"
        />
        <slot name="sufijo" />
      </div>
    </template>
  </FormField>
</template>
