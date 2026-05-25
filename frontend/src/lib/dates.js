/**
 * Calcula el miércoles que inicia la semana que contiene la fecha dada.
 * Las semanas van de miércoles a martes.
 * @param {string} dateStr - Fecha en formato YYYY-MM-DD
 * @returns {string} - week_start en formato YYYY-MM-DD
 */
export function getWeekStart(dateStr) {
  const [year, month, day] = dateStr.split('-').map(Number);
  const d = new Date(year, month - 1, day);
  // getDay(): 0=dom, 1=lun, 2=mar, 3=mié, 4=jue, 5=vie, 6=sáb
  const daysSinceWednesday = (d.getDay() - 3 + 7) % 7;
  d.setDate(d.getDate() - daysSinceWednesday);
  return toISODate(d);
}

/**
 * Calcula el martes que cierra la semana (week_start + 6 días).
 * @param {string} weekStartStr
 * @returns {string}
 */
export function getWeekEnd(weekStartStr) {
  const [year, month, day] = weekStartStr.split('-').map(Number);
  const d = new Date(year, month - 1, day + 6);
  return toISODate(d);
}

/**
 * Calcula la fecha de cobro: viernes de la semana siguiente (week_start + 9 días).
 * @param {string} weekStartStr
 * @returns {string}
 */
export function getPaymentDate(weekStartStr) {
  const [year, month, day] = weekStartStr.split('-').map(Number);
  const d = new Date(year, month - 1, day + 9);
  return toISODate(d);
}

/**
 * Convierte un objeto Date a string YYYY-MM-DD.
 * @param {Date} d
 * @returns {string}
 */
export function toISODate(d) {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Formatea fecha YYYY-MM-DD de manera legible en español.
 * @param {string} dateStr
 * @returns {string}
 */
export function formatDate(dateStr) {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day).toLocaleDateString('es', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

/**
 * Formatea rango de semana legible.
 * @param {string} weekStartStr
 * @param {string} weekEndStr
 * @returns {string}
 */
export function formatWeekRange(weekStartStr, weekEndStr) {
  const [sy, sm, sd] = weekStartStr.split('-').map(Number);
  const [ey, em, ed] = weekEndStr.split('-').map(Number);
  const start = new Date(sy, sm - 1, sd);
  const end = new Date(ey, em - 1, ed);
  const startStr = start.toLocaleDateString('es', { day: 'numeric', month: 'short' });
  const endStr = end.toLocaleDateString('es', { day: 'numeric', month: 'short', year: 'numeric' });
  return `${startStr} – ${endStr}`;
}

/**
 * Devuelve "hoy" en formato YYYY-MM-DD.
 * @returns {string}
 */
export function today() {
  return toISODate(new Date());
}
