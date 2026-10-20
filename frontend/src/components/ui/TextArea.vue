<script setup lang="ts">
import { useId } from 'vue'
import { useAtributosDeCampo } from '@/composables/useAtributosDeCampo'
import FormField from './FormField.vue'

defineOptions({ inheritAttrs: false })

const props = defineProps<{
  label?: string
  hint?: string
  error?: string | null
  required?: boolean
  id?: string
  rows?: number
}>()
const modelo = defineModel<string | null>()
const idFinal = props.id ?? useId()
const { raiz, control } = useAtributosDeCampo()
</script>

<template>
  <FormField v-bind="raiz" :id="idFinal" :label="label" :hint="hint" :error="error" :required="required">
    <template #default="{ describedby, invalid }">
      <textarea
        :id="idFinal"
        v-model="modelo"
        v-bind="control"
        :rows="rows ?? 4"
        :required="required"
        :aria-invalid="invalid || undefined"
        :aria-describedby="describedby"
        class="w-full rounded-inner border bg-surface-2 px-4 py-3 text-[15px] text-fg outline-none transition-colors focus:border-accent-line focus:ring-4 focus:ring-(--ring)"
        :class="invalid ? 'border-danger' : 'border-line'"
      />
    </template>
  </FormField>
</template>
