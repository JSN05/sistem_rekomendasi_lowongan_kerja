// Konfigurasi + fungsi bersama untuk semua halaman.
// Jika frontend dibuka dari server backend (http://localhost:8000/...) alamat API otomatis sama;
// jika dibuka dari server lain (Live Server, file://) alamat default http://localhost:8000.
const API_BASE = (location.protocol.startsWith("http") && location.port === "8000")
    ? ""
    : "http://localhost:8000";

async function apiRequest(path, options = {}) {
    let response;
    try {
        response = await fetch(API_BASE + path, {
            headers: { "Content-Type": "application/json" },
            ...options
        });
    } catch (error) {
        throw new Error("Tidak dapat terhubung ke server. Pastikan backend sudah dijalankan.");
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = data && data.detail;
        const message = (detail && detail.message) || (typeof detail === "string" ? detail : "Terjadi kesalahan pada server.");
        const err = new Error(message);
        err.status = response.status;
        err.detail = detail;
        throw err;
    }

    return data;
}

function apiGet(path, params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== "" && value !== null && value !== undefined) {
            query.set(key, value);
        }
    });
    const qs = query.toString();
    return apiRequest(path + (qs ? "?" + qs : ""));
}

function apiPost(path, body) {
    return apiRequest(path, { method: "POST", body: JSON.stringify(body) });
}

// Mencegah XSS karena data lowongan berasal dari hasil scraping
function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[ch]));
}

function formatRupiah(amount) {
    return "Rp" + Number(amount).toLocaleString("id-ID");
}

function formatSalary(min, max) {
    if (min != null && max != null) return formatRupiah(min) + " - " + formatRupiah(max);
    if (min != null) return "Mulai " + formatRupiah(min);
    if (max != null) return "Hingga " + formatRupiah(max);
    return "Gaji tidak dicantumkan";
}

function formatExperience(job) {
    if (job.experienceMissing) return "Tidak ditentukan";
    if (!job.experience) return "Fresh Graduate / tanpa pengalaman";
    return "Minimal " + job.experience + " Tahun";
}
