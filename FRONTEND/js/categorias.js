// FRONTEND/js/categorias.js

document.addEventListener("DOMContentLoaded", () => {
    cargarCategorias();
});

async function cargarCategorias() {
    try {
        const categorias = await apiGet("/api/products/categories/");
        categorias.sort((a, b) => a.id - b.id);

        const tbody = document.getElementById("tabla-categorias");
        tbody.innerHTML = "";

        categorias.forEach(c => {
            tbody.innerHTML += `
                <tr class="border-b">
                    <td class="p-2">${c.id}</td>
                    <td class="p-2">${c.name}</td>
                    <td class="p-2 space-x-2">
                        <button class="px-3 py-1 text-sm bg-amber-700 text-white rounded"
                            onclick="editarCategoria(${c.id})">
                            Editar
                        </button>
                        <button class="px-3 py-1 text-sm bg-red-600 text-white rounded"
                            onclick="eliminarCategoria(${c.id})">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (e) {
        console.error("Error al cargar categorías:", e);
        alert("No se pudieron cargar las categorías.");
    }
}

function abrirModalCategoria() {
    document.getElementById("modal-categoria-titulo").textContent = "Nueva categoría";
    document.getElementById("c-id").value = "";
    document.getElementById("c-nombre").value = "";
    document.getElementById("categoria-error").textContent = "";
    document.getElementById("modal-categoria").classList.remove("hidden");
}

function cerrarModalCategoria() {
    document.getElementById("modal-categoria").classList.add("hidden");
}

async function editarCategoria(id) {
    try {
        const c = await apiGet(`/api/products/categories/${id}/`);
        document.getElementById("modal-categoria-titulo").textContent = "Editar categoría";
        document.getElementById("c-id").value = c.id;
        document.getElementById("c-nombre").value = c.name;
        document.getElementById("categoria-error").textContent = "";
        document.getElementById("modal-categoria").classList.remove("hidden");
    } catch (e) {
        console.error("Error al cargar categoría:", e);
        alert("No se pudo cargar la categoría.");
    }
}

function validarCategoria() {
    const nombre = document.getElementById("c-nombre").value.trim();
    if (!nombre) return "El nombre es obligatorio.";
    if (nombre.length < 3) return "El nombre debe tener al menos 3 caracteres.";
    return null;
}

async function guardarCategoria() {
    const errorLabel = document.getElementById("categoria-error");
    const msg = validarCategoria();
    if (msg) {
        errorLabel.textContent = msg;
        return;
    }

    const id = document.getElementById("c-id").value;
    const data = { name: document.getElementById("c-nombre").value.trim() };

    let url = "/api/products/categories/";
    let method = "POST";

    if (id) {
        url = `/api/products/categories/${id}/`;
        method = "PUT";
    }

    const formData = new FormData();
    formData.append("name", data.name);

    try {
        if (method === "POST") {
            await apiPostMultipart(url, formData);
        } else {
            await apiPutMultipart(url, formData);
        }
        cerrarModalCategoria();
        await cargarCategorias();
    } catch (e) {
        console.error("Error al guardar categoría:", e);
        errorLabel.textContent = "No se pudo guardar la categoría.";
    }
}

async function eliminarCategoria(id) {
    if (!confirm("¿Seguro que deseas eliminar esta categoría?")) return;
    try {
        await apiDelete(`/api/products/categories/${id}/`);
        await cargarCategorias();
    } catch (e) {
        console.error("Error al eliminar categoría:", e);
        alert("No se pudo eliminar la categoría.");
    }
}
