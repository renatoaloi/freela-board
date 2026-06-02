// Convencao do frontend para datas vindas do backend.
//
// O backend devolve `date` (Pydantic + SQLAlchemy + SQLite) como string
// `YYYY-MM-DD` no JSON, sem designador de fuso. Pela spec ECMAScript,
// `new Date("YYYY-MM-DD")` e interpretado como UTC midnight, o que faz
// `toLocaleDateString` recuar um dia em qualquer fuso a oeste do UTC
// (ex.: Brasil UTC-3 mostra D-1). Por isso estes helpers NAO usam
// `new Date` para formatar nem `toISOString` para gerar "hoje".
//
// i18n (formatos diferentes de dd/MM/yyyy ou outros locales) esta fora
// de escopo. O app e single-user pt-BR; ver openspec/changes/fix-timezone-rendering-dates/design.md.

export function formatDateBR(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y}`;
}

export function getTodayLocalISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
