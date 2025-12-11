// FRONTEND/js/productos.js

document.addEventListener("DOMContentLoaded", () => {
    cargarProductos();
});

// LISTADO

async function cargarProductos() {
    try {
        const [productos, categorias, materiales] = await Promise.all([
            apiGet("/api/products/"),
            apiGet("/api/products/categories/"),
            apiGet("/api/products/materials/")
        ]);

        // Mapear ids → nombres para mostrar en tabla
        const categoryMap = {};
        categorias.forEach(c => categoryMap[c.id] = c.name);

        const materialMap = {};
        materiales.forEach(m => {
            const label = m.purity ? `${m.name} (${m.purity})` : m.name;
            materialMap[m.id] = label;
        });

        // Lo nuevo primero
        productos.sort((a, b) => b.id - a.id);

        const tbody = document.getElementById("tabla-productos");
        tbody.innerHTML = "";

        productos.forEach(p => {
            const imgSrc = p.image ? API + p.image : null;
            const categoria = p.category ? (categoryMap[p.category] || p.category) : "-";
            const material = p.material ? (materialMap[p.material] || p.material) : "-";

            tbody.innerHTML += `
                <tr class="border-b">
                    <td class="p-2">
                        ${imgSrc
                            ? `<img src="${imgSrc}" class="w-12 h-12 object-cover rounded">`
                            : `<span class="text-gray-400">-</span>`}
                    </td>
                    <td class="p-2">${p.code || "-"}</td>
                    <td class="p-2">${p.name}</td>
                    <td class="p-2">${categoria}</td>
                    <td class="p-2">${material}</td>
                    <td class="p-2">$${p.sale_price}</td>
                    <td class="p-2">${p.stock}</td>
                    <td class="p-2 space-x-2">
                        <button
                            class="px-3 py-1 text-sm bg-amber-700 text-white rounded"
                            onclick="editarProducto(${p.id})">
                            Editar
                        </button>
                        <button
                            class="px-3 py-1 text-sm bg-red-600 text-white rounded"
                            onclick="eliminarProducto(${p.id})">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });

    } catch (e) {
        console.error("Error al cargar productos:", e);
        alert("No se pudieron cargar los productos.");
    }
}

//  MODAL

function abrirModalProducto() {
    document.getElementById("modal-titulo").textContent = "Nuevo producto";
    document.getElementById("btn-guardar-producto").textContent = "Guardar";

    document.getElementById("p-id").value = "";
    document.getElementById("p-nombre").value = "";
    document.getElementById("p-precio").value = "";
    document.getElementById("p-precio-compra").value = "";
    document.getElementById("p-stock").value = "";
    document.getElementById("p-peso").value = "";
    document.getElementById("p-imagen").value = "";
    document.getElementById("producto-error").textContent = "";

    document.getElementById("modal-producto").classList.remove("hidden");
    cargarCatalogos();
}

async function editarProducto(id) {
    try {
        const p = await apiGet(`/api/products/${id}/`);
        document.getElementById("modal-titulo").textContent = "Editar producto";
        document.getElementById("btn-guardar-producto").textContent = "Actualizar";
        document.getElementById("producto-error").textContent = "";

        await cargarCatalogos();

        document.getElementById("p-id").value = p.id;
        document.getElementById("p-nombre").value = p.name;
        document.getElementById("p-precio").value = p.sale_price;
        document.getElementById("p-precio-compra").value = p.purchase_price;
        document.getElementById("p-stock").value = p.stock;
        document.getElementById("p-peso").value = p.weight ?? "";

        if (p.category) document.getElementById("p-category").value = p.category;
        if (p.supplier) document.getElementById("p-supplier").value = p.supplier;
        if (p.material) document.getElementById("p-material").value = p.material;

        // Imagen: no se rellena, usuario decide si sube una nueva
        document.getElementById("p-imagen").value = "";

        document.getElementById("modal-producto").classList.remove("hidden");
    } catch (e) {
        console.error("Error al cargar producto:", e);
        alert("No se pudo cargar la información del producto.");
    }
}

function cerrarModalProducto() {
    document.getElementById("modal-producto").classList.add("hidden");
}

//  VALIDACIÓN FRONT

function validarFormularioProducto() {
    const errores = [];

    const name = document.getElementById("p-nombre").value.trim();
    const category = document.getElementById("p-category").value;
    const salePrice = document.getElementById("p-precio").value.trim();
    const purchasePrice = document.getElementById("p-precio-compra").value.trim();
    const stock = document.getElementById("p-stock").value.trim();
    const weight = document.getElementById("p-peso").value.trim();
    const supplier = document.getElementById("p-supplier").value;
    const material = document.getElementById("p-material").value;

    const imageInput = document.getElementById("p-imagen");
    const isEdit = document.getElementById("p-id").value !== "";

    if (!name) errores.push("El nombre es obligatorio.");
    if (name && name.length < 3) errores.push("El nombre debe tener al menos 3 caracteres.");

    if (!category) errores.push("Debe seleccionar una categoría.");
    if (!supplier) errores.push("Debe seleccionar un proveedor.");
    if (!material) errores.push("Debe seleccionar un material.");

    const venta = parseFloat(salePrice);
    if (isNaN(venta) || venta <= 0) {
        errores.push("El precio de venta debe ser un número mayor a 0.");
    }

    const compra = parseFloat(purchasePrice);
    if (isNaN(compra) || compra < 0) {
        errores.push("El precio de compra debe ser un número mayor o igual a 0.");
    }

    const stockNum = parseInt(stock, 10);
    if (isNaN(stockNum) || stockNum < 0) {
        errores.push("El stock debe ser un número mayor o igual a 0.");
    }

    if (weight) {
        const pesoNum = parseFloat(weight);
        if (isNaN(pesoNum) || pesoNum <= 0) {
            errores.push("El peso debe ser un número mayor a 0.");
        }
    } else {
        errores.push("El peso es obligatorio.");
    }

    // En creación la imagen es obligatoria
    if (!isEdit && imageInput.files.length === 0) {
        errores.push("Debe subir una imagen del producto.");
    }

    const errorLabel = document.getElementById("producto-error");
    if (errores.length > 0) {
        errorLabel.textContent = errores.join(" | ");
        return false;
    }

    errorLabel.textContent = "";
    return true;
}

//  GUARDAR (CREAR / EDITAR)

async function guardarProducto() {
    if (!validarFormularioProducto()) return;

    const id = document.getElementById("p-id").value;
    const errorLabel = document.getElementById("producto-error");

    const formData = new FormData();
    formData.append("name", document.getElementById("p-nombre").value.trim());
    formData.append("category", document.getElementById("p-category").value);
    formData.append("purchase_price", document.getElementById("p-precio-compra").value.trim());
    formData.append("sale_price", document.getElementById("p-precio").value.trim());
    formData.append("weight", document.getElementById("p-peso").value.trim());
    formData.append("stock", document.getElementById("p-stock").value.trim());
    formData.append("supplier", document.getElementById("p-supplier").value);
    formData.append("material", document.getElementById("p-material").value);

    const file = document.getElementById("p-imagen").files[0];
    if (file) {
        formData.append("image", file);
    }

    let url = "/api/products/";
    let method = "POST";

    if (id) {
        url = `/api/products/${id}/`;
        method = "PUT";
    }

    try {
        if (method === "POST") {
            await apiPostMultipart(url, formData);
        } else {
            await apiPutMultipart(url, formData);
        }

        cerrarModalProducto();
        await cargarProductos();
    } catch (e) {
        console.error("Error al guardar producto:", e);
        let msgError = "No se pudo guardar el producto.";

        if (e.data) {
            const partes = [];
            const etiquetaMap = {
                name: "Nombre",
                category: "Categoría",
                purchase_price: "Precio de compra",
                sale_price: "Precio de venta",
                stock: "Stock",
                weight: "Peso",
                supplier: "Proveedor",
                material: "Material",
                image: "Imagen"
            };

            for (const campo in e.data) {
                const valor = e.data[campo];
                const etiqueta = etiquetaMap[campo] ?? campo;

                if (Array.isArray(valor)) {
                    partes.push(`${etiqueta}: ${valor.join(" ")}`);
                } else if (typeof valor === "string") {
                    partes.push(`${etiqueta}: ${valor}`);
                }
            }

            if (partes.length > 0) {
                msgError = partes.join(" | ");
            }
        }

        errorLabel.textContent = msgError;
    }
}

//  ELIMINAR

async function eliminarProducto(id) {
    if (!confirm("¿Seguro que deseas eliminar este producto?")) return;

    try {
        await apiDelete(`/api/products/${id}/`);
        await cargarProductos();
    } catch (e) {
        console.error("Error al eliminar producto:", e);
        alert("No se pudo eliminar el producto.");
    }
}

//  CATALOGOS

async function cargarCatalogos() {
    try {
        const [categorias, proveedores, materiales] = await Promise.all([
            apiGet("/api/products/categories/"),
            apiGet("/api/suppliers/"),
            apiGet("/api/products/materials/")
        ]);

        const catSelect = document.getElementById("p-category");
        const supSelect = document.getElementById("p-supplier");
        const matSelect = document.getElementById("p-material");

        catSelect.innerHTML = '<option value="">Seleccione categoría</option>';
        supSelect.innerHTML = '<option value="">Seleccione proveedor</option>';
        matSelect.innerHTML = '<option value="">Seleccione material</option>';

        categorias.forEach(c => {
            catSelect.innerHTML += `<option value="${c.id}">${c.name}</option>`;
        });

        proveedores.forEach(s => {
            supSelect.innerHTML += `<option value="${s.id}">${s.name}</option>`;
        });

        materiales.forEach(m => {
            const label = m.purity ? `${m.name} (${m.purity})` : m.name;
            matSelect.innerHTML += `<option value="${m.id}">${label}</option>`;
        });

    } catch (e) {
        console.error("Error al cargar catálogos:", e);
        alert("No se pudieron cargar los catálogos de producto.");
    }
}
