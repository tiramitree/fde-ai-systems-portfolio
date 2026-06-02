export function byId(id) {
  return document.getElementById(id);
}

export function setOptions(select, rows, selectedId, labelFn) {
  select.innerHTML = rows
    .map((row) => {
      const selected = row.id === selectedId ? "selected" : "";
      return `<option value="${row.id}" ${selected}>${labelFn(row)}</option>`;
    })
    .join("");
}
