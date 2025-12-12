document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-material");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const name = form.querySelector("#id_name").value.trim();
    const purity = form.querySelector("#id_purity").value.trim();
    const errorBox = document.getElementById("mat-error");

    errorBox.textContent = "";

    if (!name) {
      e.preventDefault();
      errorBox.textContent = "El nombre del material es obligatorio.";
      return;
    }

    if (!purity) {
      e.preventDefault();
      errorBox.textContent = "La pureza es obligatoria.";
    }
  });
});
