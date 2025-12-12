document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-categoria");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const name = form.querySelector("#id_name").value.trim();
    const errorBox = document.getElementById("cat-error");

    errorBox.textContent = "";

    if (!name) {
      e.preventDefault();
      errorBox.textContent = "El nombre es obligatorio.";
      return;
    }

    if (name.length < 3) {
      e.preventDefault();
      errorBox.textContent = "Debe tener al menos 3 caracteres.";
    }
  });
});
