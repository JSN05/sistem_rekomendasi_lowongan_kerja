const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");

const locationFilter = document.getElementById("locationFilter");
const educationFilter = document.getElementById("educationFilter");
const experienceFilter = document.getElementById("experienceFilter");
const jobTypeFilter = document.getElementById("jobTypeFilter");
const salaryFilter = document.getElementById("salaryFilter");
const genderFilter = document.getElementById("genderFilter");
const resetButton = document.getElementById("resetButton");

const jobContainer = document.getElementById("jobContainer");
const noResults = document.getElementById("noResults");
const resultInfo = document.getElementById("resultInfo");
const pagination = document.getElementById("pagination");

const PAGE_SIZE = 12;
let currentPage = 1;
let requestCounter = 0;   // mengabaikan respons lama jika filter berubah cepat

function createJobCard(job) {
    const card = document.createElement("div");
    card.className = "job-card";

    card.innerHTML = `
        <div class="job-card-header">
            <h3>${escapeHtml(job.title)}</h3>
            <span class="job-type">${escapeHtml(job.jobType || "-")}</span>
        </div>

        <p class="company-name">${escapeHtml(job.company)}</p>

        <div class="job-info">
            <span>${escapeHtml(job.location || "-")}</span>
            <span>${escapeHtml(job.education || "-")}</span>
            <span>${escapeHtml(formatExperience(job))}</span>
        </div>

        <p class="job-salary">${escapeHtml(formatSalary(job.salaryMin, job.salaryMax))}</p>

        <a href="detail.html?id=${encodeURIComponent(job.id)}" class="job-button">Lihat Detail</a>
    `;
    return card;
}

function renderPagination(data) {
    pagination.innerHTML = "";
    if (data.totalPages <= 1) return;

    const prev = document.createElement("button");
    prev.textContent = "Sebelumnya";
    prev.disabled = data.page <= 1;
    prev.addEventListener("click", () => loadJobs(data.page - 1));

    const info = document.createElement("span");
    info.textContent = `Halaman ${data.page} dari ${data.totalPages}`;

    const next = document.createElement("button");
    next.textContent = "Berikutnya";
    next.disabled = data.page >= data.totalPages;
    next.addEventListener("click", () => loadJobs(data.page + 1));

    pagination.append(prev, info, next);
}

async function loadJobs(page = 1) {
    currentPage = page;
    const requestId = ++requestCounter;

    try {
        const data = await apiGet("/api/jobs", {
            q: searchInput.value.trim(),
            location: locationFilter.value,
            education: educationFilter.value,
            experience: experienceFilter.value,
            job_type: jobTypeFilter.value,
            salary_min: salaryFilter.value,
            gender: genderFilter.value,
            page: currentPage,
            page_size: PAGE_SIZE
        });

        if (requestId !== requestCounter) return;

        jobContainer.innerHTML = "";
        data.items.forEach(job => jobContainer.appendChild(createJobCard(job)));

        noResults.style.display = data.total === 0 ? "block" : "none";
        noResults.textContent = "Tidak ada lowongan yang sesuai dengan kriteria pencarian Anda.";
        resultInfo.textContent = `Menampilkan ${data.items.length} dari ${data.total} lowongan.`;
        renderPagination(data);
    } catch (error) {
        if (requestId !== requestCounter) return;
        jobContainer.innerHTML = "";
        pagination.innerHTML = "";
        noResults.style.display = "block";
        noResults.textContent = error.message;
        resultInfo.textContent = "";
    }
}

// Mengisi pilihan lokasi dari data lowongan yang ada di backend
async function loadLocationOptions() {
    try {
        const meta = await apiGet("/api/meta");
        meta.locations.forEach(loc => {
            const option = document.createElement("option");
            option.value = loc.value;
            option.textContent = `${loc.label} (${loc.count})`;
            locationFilter.appendChild(option);
        });
    } catch (error) {
        // filter lokasi tetap kosong; daftar lowongan akan menampilkan pesan kesalahan
    }
}

// Pencarian langsung saat mengetik (ditunda sebentar agar tidak membanjiri server)
let searchTimer = null;
searchInput.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => loadJobs(1), 300);
});
searchButton.addEventListener("click", () => loadJobs(1));

[locationFilter, educationFilter, jobTypeFilter, genderFilter].forEach(el =>
    el.addEventListener("change", () => loadJobs(1)));

[experienceFilter, salaryFilter].forEach(el => {
    let timer = null;
    el.addEventListener("input", () => {
        clearTimeout(timer);
        timer = setTimeout(() => loadJobs(1), 400);
    });
});

resetButton.addEventListener("click", () => {
    searchInput.value = "";
    locationFilter.value = "";
    educationFilter.value = "";
    experienceFilter.value = "";
    jobTypeFilter.value = "";
    salaryFilter.value = "";
    genderFilter.value = "";
    loadJobs(1);
});

loadLocationOptions();
loadJobs(1);
