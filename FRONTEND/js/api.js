// FRONTEND/js/api.js
// Helpers mínimos para consumir la API de Django

const API = "http://127.0.0.1:8000";

async function apiGet(url) {
    const res = await fetch(API + url);

    let body = null;
    try {
        body = await res.json();
    } catch (_) {
        body = null;
    }

    if (!res.ok) {
        const err = new Error("API GET error");
        err.status = res.status;
        err.data = body;
        throw err;
    }

    return body;
}

async function apiPostMultipart(url, formData) {
    const res = await fetch(API + url, {
        method: "POST",
        body: formData
    });

    let body = null;
    try {
        body = await res.json();
    } catch (_) {
        body = null;
    }

    if (!res.ok) {
        const err = new Error("API POST error");
        err.status = res.status;
        err.data = body;
        throw err;
    }

    return body;
}

async function apiPutMultipart(url, formData) {
    const res = await fetch(API + url, {
        method: "PUT",
        body: formData
    });

    let body = null;
    try {
        body = await res.json();
    } catch (_) {
        body = null;
    }

    if (!res.ok) {
        const err = new Error("API PUT error");
        err.status = res.status;
        err.data = body;
        throw err;
    }

    return body;
}

async function apiDelete(url) {
    const res = await fetch(API + url, {
        method: "DELETE"
    });

    let body = null;
    try {
        body = await res.json();
    } catch (_) {
        body = null;
    }

    if (!res.ok) {
        const err = new Error("API DELETE error");
        err.status = res.status;
        err.data = body;
        throw err;
    }

    return body;
}
