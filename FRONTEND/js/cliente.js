document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-cliente");
    if (!form) return;

    form.addEventListener("submit", (event) => {
        const msg = validarClienteFront(form);
        const errorLabel = document.getElementById("cliente-error");

        if (errorLabel) errorLabel.textContent = "";

        if (msg) {
            event.preventDefault();
            if (errorLabel) errorLabel.textContent = msg;
        }
    });
});

function validarClienteFront(form) {
    const nombre = (form.querySelector("#c-nombre")?.value || "").trim();
    const apP    = (form.querySelector("#c-apellido-paterno")?.value || "").trim();
    const apM    = (form.querySelector("#c-apellido-materno")?.value || "").trim();
    const phone  = (form.querySelector("#c-telefono")?.value || "").trim();
    const email  = (form.querySelector("#c-correo")?.value || "").trim();
    const rfc    = (form.querySelector("#c-rfc")?.value || "").trim();

    // Nombre
    if (!nombre) return "El nombre es obligatorio.";
    if (nombre.length < 3) return "El nombre debe tener al menos 3 caracteres.";

    // Apellidos
    if (!apP) return "El apellido paterno es obligatorio.";
    if (apP.length < 3) return "El apellido paterno debe tener al menos 3 caracteres.";

    if (!apM) return "El apellido materno es obligatorio.";
    if (apM.length < 3) return "El apellido materno debe tener al menos 3 caracteres.";

    // Teléfono
    if (phone) {
        if (!/^\d+$/.test(phone)) return "El teléfono solo debe contener dígitos.";
        if (phone.length < 7) return "El teléfono debe tener al menos 7 dígitos.";
        if (phone.length > 15) return "El teléfono no debe exceder 15 dígitos.";
    }

    // Email
    if (email && !email.includes("@")) {
        return "Ingresa un correo electrónico válido.";
    }

    // RFC
    if (rfc) {
        if (!/^[A-ZÑ&0-9]{12,13}$/i.test(rfc)) {
            return "El RFC debe tener 12 a 13 caracteres (letras y números).";
        }
    }

    return null;
}
