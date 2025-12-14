(() => {
  const $ = (id) => document.getElementById(id);

  function getCookie(name) {
    const v = `; ${document.cookie}`;
    const parts = v.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }

  const ajaxUrl = $("ajax_update_url")?.value;
  const payBlock = $("pay_block");
  const btnCobrar = $("btn_cobrar");

  const inpDesc = $("inp_descuento_pct");
  const selMetodo = $("sel_metodo_pago");
  const inpPagado = $("inp_pagado");

  const uiSubtotal = $("ui_subtotal");
  const uiDescPct = $("ui_desc_pct");
  const uiDescMonto = $("ui_desc_monto");
  const uiTotal = $("ui_total");
  const uiCambio = $("ui_cambio");
  const uiFaltante = $("ui_faltante");
  const uiAlert = $("ui_alert");

  function setPayEnabled(enabled) {
    if (!payBlock) return;
    payBlock.classList.toggle("opacity-50", !enabled);
    payBlock.classList.toggle("pointer-events-none", !enabled);
    payBlock.classList.toggle("select-none", !enabled);

    [inpDesc, selMetodo, inpPagado].forEach((el) => {
      if (!el) return;
      el.disabled = !enabled;
    });
  }

  function setCobrarEnabled(enabled) {
    if (!btnCobrar) return;
    btnCobrar.disabled = !enabled;
    btnCobrar.classList.toggle("opacity-60", !enabled);
    btnCobrar.classList.toggle("cursor-not-allowed", !enabled);
  }

  function moneyText(v) {
    return (v ?? "0.00").toString();
  }

  async function postForm(url, data) {
    const form = new FormData();
    Object.keys(data).forEach((k) => form.append(k, data[k]));

    const csrf = getCookie("csrftoken");

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrf,
      },
      body: form,
      credentials: "same-origin",
    });

    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      throw new Error("Respuesta no JSON (posible 403/CSRF).");
    }
    return await res.json();
  }

  function validateInputsLocal() {
    if (!inpDesc || !selMetodo || !inpPagado) return;

    let d = parseInt(inpDesc.value || "0", 10);
    if (Number.isNaN(d)) d = 0;
    if (d < 0) d = 0;
    if (d > 100) d = 100;
    inpDesc.value = String(d);

    if (inpPagado.value && parseFloat(inpPagado.value) < 0) inpPagado.value = "0";
  }

  async function updateTotals() {
    if (!ajaxUrl) return;

    validateInputsLocal();

    const descuento_pct = inpDesc ? inpDesc.value : "0";
    const metodo_pago = selMetodo ? selMetodo.value : "CASH";
    const cantidad_pagada = inpPagado ? inpPagado.value : "";

    try {
      const data = await postForm(ajaxUrl, { descuento_pct, metodo_pago, cantidad_pagada });
      if (!data.ok) return;

      const hasItems = !!data.has_items;
      setPayEnabled(hasItems);

      if (uiSubtotal) uiSubtotal.textContent = moneyText(data.subtotal);
      if (uiDescPct) uiDescPct.textContent = moneyText(data.descuento_pct);
      if (uiDescMonto) uiDescMonto.textContent = moneyText(data.descuento_monto);
      if (uiTotal) uiTotal.textContent = moneyText(data.total);
      if (uiCambio) uiCambio.textContent = moneyText(data.cambio);
      if (uiFaltante) uiFaltante.textContent = moneyText(data.faltante);

      if (uiAlert) {
        if (parseFloat(data.faltante) > 0) {
          uiAlert.textContent = "Falta dinero para completar el pago.";
          uiAlert.classList.remove("hidden");
        } else {
          uiAlert.textContent = "";
          uiAlert.classList.add("hidden");
        }
      }

      setCobrarEnabled(!!data.can_charge);
    } catch (e) {
      // console.error(e);
    }
  }

  [inpDesc, selMetodo, inpPagado].forEach((el) => {
    if (!el) return;
    el.addEventListener("input", () => updateTotals());
    el.addEventListener("change", () => updateTotals());
  });

  updateTotals();

  // Cliente registrado: buscar y seleccionar
  const clientSearchUrl = $("client_search_url")?.value;
  const clientSelectTpl = $("client_select_url_tpl")?.value;
  const inpClient = $("inp_client_search");
  const btnClient = $("btn_client_search");
  const clientResults = $("client_results");

  function renderClients(items) {
    if (!clientResults) return;
    clientResults.innerHTML = "";

    if (!items.length) {
      clientResults.innerHTML = `<div class="text-sm text-gray-400">Sin resultados.</div>`;
      return;
    }

    items.forEach((c) => {
      const div = document.createElement("div");
      div.className = "border rounded p-2 flex items-center justify-between gap-2";

      const left = document.createElement("div");
      left.className = "min-w-0";
      left.innerHTML = `
        <div class="text-sm font-semibold truncate">${c.name}</div>
        <div class="text-xs text-gray-500">${c.phone ? c.phone : ""}</div>
      `;

      const form = document.createElement("form");
      form.method = "post";
      form.className = "m-0";
      form.action = clientSelectTpl.replace("999999", String(c.id));

      const csrf = getCookie("csrftoken");
      form.innerHTML = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf}">
        <button type="submit" class="px-3 py-1 text-sm bg-amber-700 text-white rounded hover:bg-amber-800">Seleccionar</button>
      `;

      div.appendChild(left);
      div.appendChild(form);
      clientResults.appendChild(div);
    });
  }

  async function searchClients() {
    if (!clientSearchUrl || !inpClient) return;
    const q = (inpClient.value || "").trim();
    if (q.length < 2) {
      renderClients([]);
      return;
    }

    const url = `${clientSearchUrl}?q=${encodeURIComponent(q)}`;
    const res = await fetch(url, { credentials: "same-origin" });
    const data = await res.json();
    if (data.ok) renderClients(data.results || []);
  }

  if (btnClient) btnClient.addEventListener("click", searchClients);
  if (inpClient) inpClient.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      searchClients();
    }
  });
})();
