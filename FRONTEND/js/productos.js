document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-producto");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    const name = form.querySelector("#id_name").value.trim();
    const compra = parseFloat(form.querySelector("#id_purchase_price").value);
    const venta = parseFloat(form.querySelector("#id_sale_price").value);
    const stock = parseInt(form.querySelector("#id_stock").value);
    const errorBox = document.getElementById("prod-error");

    errorBox.textContent = "";

    if (!name) {
      e.preventDefault();
      errorBox.textContent = "El nombre es obligatorio.";
      return;
    }

    if (isNaN(compra) || compra < 0) {
      e.preventDefault();
      errorBox.textContent = "El precio de compra no es válido.";
      return;
    }

    if (isNaN(venta) || venta < 0) {
      e.preventDefault();
      errorBox.textContent = "El precio de venta no es válido.";
      return;
    }

    if (venta < compra) {
      if (!confirm("El precio de venta es menor al de compra. ¿Deseas continuar?")) {
        e.preventDefault();
        return;
      }
    }

    if (isNaN(stock) || stock < 0) {
      e.preventDefault();
      errorBox.textContent = "El stock no puede ser negativo.";
    }
  });
});
