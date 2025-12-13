document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-staff");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    const msg = validarStaffFront(form);
    const errorLabel = document.getElementById("staff-error");
    if (errorLabel) errorLabel.textContent = "";

    if (msg) {
      event.preventDefault();
      if (errorLabel) errorLabel.textContent = msg;
    }
  });
});

function validarStaffFront(form) {
  const username = (form.querySelector("#st-username")?.value || "").trim();
  const rol      = (form.querySelector("#st-rol")?.value || "").trim();

  const pass1    = (form.querySelector("#st-password1")?.value || "").trim();
  const pass2    = (form.querySelector("#st-password2")?.value || "").trim();

  const nombre   = (form.querySelector("#st-nombre")?.value || "").trim();
  const apP      = (form.querySelector("#st-ap")?.value || "").trim();
  const apM      = (form.querySelector("#st-am")?.value || "").trim();

  const email    = (form.querySelector("#st-email")?.value || "").trim();
  const telefono = (form.querySelector("#st-telefono")?.value || "").trim();
  const direccion= (form.querySelector("#st-direccion")?.value || "").trim();

  // Usuario (solo cuando existe en el form: crear)
  const usernameInput = form.querySelector("#st-username");
  if (usernameInput) {
    if (!username) return "El usuario es obligatorio.";
    if (username.length < 3) return "El usuario debe tener al menos 3 caracteres.";
    if (!/^[a-zA-Z0-9_.-]+$/.test(username)) {
      return "El usuario solo puede contener letras, números, guion, guion bajo y punto.";
    }
  }

  // Rol
  if (!rol) return "Debes seleccionar un rol.";

  // Contraseñas (solo cuando existen en el form: crear)
  const pass1Input = form.querySelector("#st-password1");
  const pass2Input = form.querySelector("#st-password2");
  if (pass1Input || pass2Input) {
    if (!pass1) return "La contraseña es obligatoria.";
    if (pass1.length < 6) return "La contraseña debe tener al menos 6 caracteres.";
    if (!pass2) return "Debes confirmar la contraseña.";
    if (pass1 !== pass2) return "Las contraseñas no coinciden.";
  }

  // Nombre
  if (!nombre) return "El nombre es obligatorio.";
  if (nombre.length < 3) return "El nombre debe tener al menos 3 caracteres.";

  // Apellidos
  if (!apP) return "El apellido paterno es obligatorio.";
  if (apP.length < 3) return "El apellido paterno debe tener al menos 3 caracteres.";

  if (!apM) return "El apellido materno es obligatorio.";
  if (apM.length < 3) return "El apellido materno debe tener al menos 3 caracteres.";

  // Email
  if (!email) return "El correo es obligatorio.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Ingresa un correo electrónico válido.";

  // Teléfono
  if (!telefono) return "El teléfono es obligatorio.";
  if (!/^\d+$/.test(telefono)) return "El teléfono solo debe contener dígitos.";
  if (telefono.length < 7) return "El teléfono debe tener al menos 7 dígitos.";
  if (telefono.length > 15) return "El teléfono no debe exceder 15 dígitos.";

  // Dirección
  if (!direccion) return "La dirección es obligatoria.";
  if (direccion.length < 5) return "La dirección debe tener al menos 5 caracteres.";

  return null;
}
