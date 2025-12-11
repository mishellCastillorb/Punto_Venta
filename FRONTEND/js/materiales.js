// FRONTEND/js/materiales.js

document.addEventListener("DOMContentLoaded", () => {
    cargarMateriales();
});

async function cargarMateriales() {
    try {
        const materiales = await apiGet("/api/products/materials/");
        materiales.sort((a, b) => a.id - b.id);

        const tbody = document.getElementById("tabla-materiales");
        tbody.innerHTML = "";

        materiales.forEach(m => {
            tbody.innerHTML += `
                <tr class="border-b">
                    <td class="p-2">${m.id}</td>
                    <td class="p-2">${m.name}</td>
                    <td class="p-2">${m.purity || "-"}</td>
                    <td class="p-2 space-x-2">
                        <button class="px-3 py-1 text-sm bg-amber-700 text-white rounded"
                            onclick="editarMaterial(${m.id})">
                            Editar
                        </button>
                        <button class="px-3 py-1 text-sm bg-red-600 text-white rounded"
                            onclick="eliminarMaterial(${m.id})">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        console.error("Error al cargar materiales:", e);
        alert("No se pudieron cargar los materiales.");
    }
}

function abrirModalMaterial() {
    document.getElementById("modal-material-titulo").textContent = "Nuevo material";
    document.getElementById("m-id").value = "";
    document.getElementById("m-nombre").value = "";
    document.getElementById("m-pureza").value = "";
    document.getElementById("material-error").textContent = "";
    document.getElementById("modal-material").classList.remove("hidden");
}

function cerrarModalMaterial() {
    document.getElementById("modal-material").classList.add("hidden");
}

async function editarMaterial(id) {
    try {
        const m = await apiGet(`/api/products/materials/${id}/`);
        document.getElementById("modal-material-titulo").textContent = "Editar material";
        document.getElementById("m-id").value = m.id;
        document.getElementById("m-nombre").value = m.name;
        document.getElementById("m-pureza").value = m.purity || "";
        document.getElementById("material-error").textContent = "";
        document.getElementById("modal-material").classList.remove("hidden");
    } catch (e) {
        console.error("Error al cargar material:", e);
        alert("No se pudo cargar el material.");
    }
}

function validarMaterial() {
    const nombre = document.getElementById("m-nombre").value.trim();
    if (!nombre) return "El nombre es obligatorio.";
    if (nombre.length < 3) return "El nombre debe tener al menos 3 caracteres.";
    return null;
}

async function guardarMaterial() {
    const errorLabel = document.getElementById("material-error");
    const msg = validarMaterial();
    if (msg) {
        errorLabel.textContent = msg;
        return;
    }

    const id = document.getElementById("m-id").value;
    const data = {
        name: document.getElementById("m-nombre").value.trim(),
        purity: document.getElementById("m-pureza").value.trim()
    };

    let url = "/api/products/materials/";
    let method = "POST";

    if (id) {
        url = `/api/products/materials/${id}/`;
        method = "PUT";
    }

    const formData = new FormData();
    formData.append("name", data.name);
    formData.append("purity", data.purity);

    try {
        if (method === "POST") {
            await apiPostMultipart(url, formData);
        } else {
            await apiPutMultipart(url, formData);
        }
        cerrarModalMaterial();
        await cargarMateriales();
    } catch (e) {
        console.error("Error al guardar material:", e);
        errorLabel.textContent = "No se pudo guardar el material.";
    }
}

async function eliminarMaterial(id) {
    if (!confirm("¿Seguro que deseas eliminar este material?")) return;
    try {
        await apiDelete(`/api/products/materials/${id}/`);
        await cargarMateriales();
    } catch (e) {
        console.error("Error al eliminar material:", e);
        alert("No se pudo eliminar el material.");
    }
}
