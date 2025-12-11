// Cargar datos al entrar
document.addEventListener("DOMContentLoaded", () => {
    cargarProveedores();
});

// ======================= LISTADO =======================

async function cargarProveedores() {
    try {
        const datos = await apiGet("/api/suppliers/");

        const tbody = document.getElementById("tabla-proveedores");
        tbody.innerHTML = "";

        datos.forEach(p => {
            tbody.innerHTML += `
                <tr class="border-b">
                    <td class="p-2">${p.name}</td>
                    <td class="p-2">${p.code}</td>
                    <td class="p-2">${p.phone}</td>
                    <td class="p-2">${p.email}</td>
                    <td class="p-2 space-x-2">
                        <button class="px-3 py-1 text-sm bg-amber-700 text-white rounded"
                            onclick="editarProveedor(${p.id})">
                            Editar
                        </button>
                        <button class="px-3 py-1 text-sm bg-amber-700 text-white rounded"
                            onclick="eliminarProveedor(${p.id})">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        console.error("Error al cargar proveedores:", e);
        alert("No se pudo cargar la lista de proveedores.");
    }
}

// ======================= MODAL =======================

function abrirModalProveedor() {
    document.getElementById("modal-title").textContent = "Nuevo proveedor";
    document.getElementById("btn-guardar").textContent = "Guardar";

    document.getElementById("prov-id").value = "";
    document.getElementById("prov-name").value = "";
    document.getElementById("prov-code").value = "";
    document.getElementById("prov-phone").value = "";
    document.getElementById("prov-email").value = "";
    document.getElementById("prov-notes").value = "";
    document.getElementById("prov-error").textContent = "";

    document.getElementById("modal-proveedor").classList.remove("hidden");
}

async function editarProveedor(id) {
    try {
        const p = await apiGet(`/api/suppliers/${id}/`);

        document.getElementById("modal-title").textContent = "Editar proveedor";
        document.getElementById("btn-guardar").textContent = "Actualizar";

        document.getElementById("prov-id").value = p.id;
        document.getElementById("prov-name").value = p.name || "";
        document.getElementById("prov-code").value = p.code || "";
        document.getElementById("prov-phone").value = p.phone || "";
        document.getElementById("prov-email").value = p.email || "";
        document.getElementById("prov-notes").value = p.notes || "";
        document.getElementById("prov-error").textContent = "";

        document.getElementById("modal-proveedor").classList.remove("hidden");
    } catch (e) {
        console.error("Error al cargar proveedor:", e);
        alert("No se pudo cargar la información del proveedor.");
    }
}

function cerrarModalProveedor() {
    document.getElementById("modal-proveedor").classList.add("hidden");
}

// ======================= VALIDACIÓN FRONT =======================

function validarProveedor() {
    const name  = document.getElementById("prov-name").value.trim();
    const code  = document.getElementById("prov-code").value.trim();
    const phone = document.getElementById("prov-phone").value.trim();
    const email = document.getElementById("prov-email").value.trim();

    if (!name) return "El nombre es obligatorio.";
    if (name.length < 3) return "El nombre debe tener al menos 3 caracteres.";

    if (!code) return "El código es obligatorio.";

    if (!phone) return "El teléfono es obligatorio.";
    if (!/^\d+$/.test(phone)) return "El teléfono solo debe contener dígitos.";
    if (phone.length < 7) return "El teléfono debe tener al menos 7 dígitos.";

    if (!email) return "El correo electrónico es obligatorio.";
    if (!email.includes("@")) return "Ingresa un correo válido.";

    return null;
}

// ======================= GUARDAR (CREATE / UPDATE) =======================

async function guardarProveedor() {
    const id = document.getElementById("prov-id").value;
    const errorLabel = document.getElementById("prov-error");
    errorLabel.textContent = "";

    const msg = validarProveedor();
    if (msg) {
        errorLabel.textContent = msg;
        return;
    }

    const payload = {
        name: document.getElementById("prov-name").value.trim(),
        code: document.getElementById("prov-code").value.trim(),
        phone: document.getElementById("prov-phone").value.trim(),
        email: document.getElementById("prov-email").value.trim(),
        notes: document.getElementById("prov-notes").value.trim() || null
    };

    try {
        if (id) {
            await apiPut(`/api/suppliers/${id}/`, payload);
        } else {
            await apiPost("/api/suppliers/", payload);
        }

        cerrarModalProveedor();
        cargarProveedores();
    } catch (e) {
        console.warn("Error al guardar proveedor:", e.data || e);

        let msgError = "No se pudo guardar el proveedor.";

        if (e.data) {
            const labels = {
                name: "Nombre",
                code: "Código",
                phone: "Teléfono",
                email: "Correo",
                non_field_errors: ""
            };

            const partes = [];
            for (const campo in e.data) {
                const valor = e.data[campo];
                const etiqueta = labels[campo] ?? campo;

                if (Array.isArray(valor)) {
                    partes.push(
                        etiqueta
                            ? `${etiqueta}: ${valor.join(" ")}`
                            : valor.join(" ")
                    );
                } else if (typeof valor === "string") {
                    partes.push(
                        etiqueta
                            ? `${etiqueta}: ${valor}`
                            : valor
                    );
                }
            }

            if (partes.length > 0) {
                msgError = partes.join(" | ");
            }
        }

        errorLabel.textContent = msgError;
    }
}

// ======================= ELIMINAR =======================

async function eliminarProveedor(id) {
    if (!confirm("¿Seguro que deseas eliminar este proveedor?")) return;

    try {
        await apiDelete(`/api/suppliers/${id}/`);
        cargarProveedores();
    } catch (e) {
        console.error("Error al eliminar proveedor:", e);

        let msg = "No se pudo eliminar el proveedor.";
        if (e.data && e.data.detail) {
            msg = e.data.detail;
        }
        alert(msg);
    }
}
