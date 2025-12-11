document.addEventListener("DOMContentLoaded", () => {
    //loadMenu();
    cargarClientes();
});

//Cargar lista y mostra botones
async function cargarClientes() {
    const clientes = await apiGet("/api/clients/list/", true);

    const tbody = document.getElementById("tabla-clientes");
    tbody.innerHTML = "";

    clientes.forEach(c => {
        tbody.innerHTML += `
            <tr class="border-b">
                <td class="p-2">${c.id}</td>
                <td class="p-2">${c.name}</td>
                <td class="p-2">${c.phone ?? "-"}</td>
                <td class="p-2">${c.email ?? "-"}</td>
                <td class="p-2">${c.address ?? "-"}</td>

                <td class="p-2 flex gap-2">
                    <button onclick="editarCliente(${c.id})"
                        class="bg-amber-700 text-white px-3 py-1 rounded text-sm">
                        Editar
                    </button>

                    <button onclick="eliminarCliente(${c.id})"
                        class="bg-red-600 text-white px-3 py-1 rounded text-sm">
                        Eliminar
                    </button>
                </td>
            </tr>
        `;
    });
}

// Modal vacio para crear clientes
function abrirModalCliente() {
    limpiarErrores();
    document.getElementById("modal-titulo").textContent = "Nuevo cliente";
    document.getElementById("c-id").value = "";

    document.getElementById("c-nombre").value = "";
    document.getElementById("c-telefono").value = "";
    document.getElementById("c-correo").value = "";
    document.getElementById("c-direccion").value = "";

    document.getElementById("modal-cliente").classList.remove("hidden");
}
//Modal con datos para editar cliente
async function editarCliente(id) {
    limpiarErrores();
    const cliente = await apiGet(`/api/clients/${id}/`, true);

    document.getElementById("modal-titulo").textContent = "Editar cliente";
    document.getElementById("c-id").value = cliente.id;

    document.getElementById("c-nombre").value = cliente.name;
    document.getElementById("c-telefono").value = cliente.phone ?? "";
    document.getElementById("c-correo").value = cliente.email ?? "";
    document.getElementById("c-direccion").value = cliente.address ?? "";

    document.getElementById("modal-cliente").classList.remove("hidden");
}

function limpiarErrores() {
    const campos = ["nombre", "apP", "apM", "tel", "email"];
    campos.forEach(c => {
        const el = document.getElementById(`err-${c}`);
        el.textContent = "";
        el.classList.add("hidden");
    });
}

//Validar
function validarFormularioCliente() {
    limpiarErrores(); // limpiar mensajes previos

    let valido = true;

    const nombre = document.getElementById("c-nombre").value.trim();
    const apP = document.getElementById("c-apellido-paterno").value.trim();
    const apM = document.getElementById("c-apellido-materno").value.trim();
    const tel = document.getElementById("c-telefono").value.trim();
    const email = document.getElementById("c-correo").value.trim();

    // name
    if (!nombre) {
        mostrarError("nombre", "El nombre es obligatorio");
        valido = false;
    }

    // Apellido paterno
    if (!apP) {
        mostrarError("apP", "El apellido paterno es obligatorio");
        valido = false;
    }

    // Apellido materno
    if (!apM) {
        mostrarError("apM", "El apellido materno es obligatorio");
        valido = false;
    }

    // phone
    if (!tel) {
        mostrarError("tel", "El teléfono es obligatorio");
        valido = false;
    } else if (!/^[0-9+ ]+$/.test(tel)) {
        mostrarError("tel", "El teléfono solo debe contener números o '+'");
        valido = false;
    }

    // Email
    if (!email) {
        mostrarError("email", "El correo es obligatorio");
        valido = false;
    } else if (!email.includes("@")) {
        mostrarError("email", "Formato de correo inválido");
        valido = false;
    }

    return valido;
}

// Mostrar errores
function mostrarError(campo, mensaje) {
    const el = document.getElementById(`err-${campo}`);
    el.textContent = mensaje;
    el.classList.remove("hidden");
}


// Guardar (para crear o editar)
async function guardarCliente() {
    if (!validarFormularioCliente()) return;

    const id = document.getElementById("c-id").value;

    const data = {
        name: document.getElementById("c-nombre").value,
        apellido_paterno: document.getElementById("c-apellido-paterno").value,
        apellido_materno: document.getElementById("c-apellido-materno").value,
        phone: document.getElementById("c-telefono").value,
        email: document.getElementById("c-correo").value,
        address: document.getElementById("c-direccion").value,
    };

    try {
        if (!id) {
            await apiPost("/api/clients/create/", data);
        } else {
            await apiPut(`/api/clients/${id}/`, data);
        }

        cerrarModalCliente();
        cargarClientes();
        return;

    } catch (err) {
        console.error("Error desde el backend:", err.data);

        // Telefono repetido
        if (err.data?.phone) {
            mostrarError("tel", "Este teléfono ya está registrado.");
        }

        // Correo repetido
        if (err.data?.email) {
            mostrarError("email", "Este correo ya está registrado.");
        }

        // Nombre invalido
        if (err.data?.name) {
            mostrarError("nombre", err.data.name[0]);
        }
        return; // NO cerrar modal
    }
}



//Eliminar cliente
async function eliminarCliente(id) {
    if (!confirm("¿Seguro que deseas eliminar este cliente?")) return;

    await apiDelete(`/api/clients/${id}/delete/`, true);

    cargarClientes();
}

//Cerrar modal
function cerrarModalCliente() {
    document.getElementById("modal-cliente").classList.add("hidden");
}
