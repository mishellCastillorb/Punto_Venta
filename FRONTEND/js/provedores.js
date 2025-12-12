// FRONTEND/js/proveedores.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-proveedor");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    const msg = validarProveedorFront(form);
    const errorLabel = document.getElementById("prov-error");

    if (errorLabel) errorLabel.textContent = "";

    // Si hay error, evitamos el submit (solo cuando hay JS habilitado)
    if (msg) {
      event.preventDefault();
      if (errorLabel) errorLabel.textContent = msg;
    }
  });
});

function validarProveedorFront(form) {
  const name  = (form.querySelector("#prov-name")?.value || "").trim();
  const code  = (form.querySelector("#prov-code")?.value || "").trim();
  const phone = (form.querySelector("#prov-phone")?.value || "").trim();
  const email = (form.querySelector("#prov-email")?.value || "").trim();

  if (!name) return "El nombre es obligatorio.";
  if (name.length < 3) return "El nombre debe tener al menos 3 caracteres.";

  if (!code) return "El código es obligatorio.";

  if (!phone) return "El teléfono es obligatorio.";
  if (!/^\d+$/.test(phone)) return "El teléfono solo debe contener dígitos.";
  if (phone.length < 7) return "El teléfono debe tener al menos 7 dígitos.";
  if (phone.length > 15) return "El teléfono no debe exceder 15 dígitos.";

  if (!email) return "El correo electrónico es obligatorio.";
  // el input type="email" ya valida bastante, pero dejamos una extra simple
  if (!email.includes("@")) return "Ingresa un correo válido.";

  return null;
}
