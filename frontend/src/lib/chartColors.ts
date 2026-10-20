/** Colores de los gráficos leídos de tokens.css (ECharts dibuja en canvas y no entiende var()). */
function token(nombre: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(nombre).trim()
}

/** Llamar dentro de un computed que dependa del tema para que se recalculen al cambiarlo. */
export function coloresGrafico() {
  return {
    texto: token('--muted'),
    linea: token('--line'),
    superficie: token('--surface'),
    acento: token('--accent'),
    neutro: token('--pill-active-bg'),
    // La primera serie es neutra: el acento queda para resaltar (la línea, el día de hoy).
    serie: [token('--pill-active-bg'), token('--accent'), token('--info'), token('--success'), token('--warning'), token('--muted')],
  }
}
