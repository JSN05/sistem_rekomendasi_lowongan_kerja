
 // ======================================
 // MENGAMBIL ELEMEN HTML
 // ======================================
console.log("JavaScript Lowongan berhasil dimuat!");
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");

const locationFilter = document.getElementById("locationFilter");
const educationFilter = document.getElementById("educationFilter");
const experienceFilter = document.getElementById("experienceFilter");
const jobTypeFilter = document.getElementById("jobTypeFilter");
const salaryFilter = document.getElementById("salaryFilter");
const genderFilter = document.getElementById("genderFilter");

const resetButton = document.getElementById("resetButton");

const jobCards = document.querySelectorAll(".job-card");
const noResults = document.getElementById("noResults");

// ======================================
// FUNGSI NORMALISASI TEKS
// ======================================

function normalizeText(text) {
    return text.toLowerCase().trim().replace(/\s+/g, " ");
}

// ======================================
// FUNGSI MENGUBAH PENDIDIKAN KE LEVEL
// ======================================

function getEducationLevel(education) {
    const value = normalizeText(education);

    if (value.includes("smp") || value.includes("mts")) return 1;
    if (value.includes("sma") || value.includes("smk")) return 2;
    if (value.includes("d3") || value.includes("d4")) return 3;
    if (value.includes("s1")) return 4;

    return 0;
}

// ======================================
// FUNGSI FILTER LOWONGAN
// ======================================

function filterJobs() {
    const searchValue = normalizeText(searchInput.value);

    const locationValue = normalizeText(locationFilter.value);
    const educationValue = normalizeText(educationFilter.value);
    const jobTypeValue = normalizeText(jobTypeFilter.value);
    const genderValue = normalizeText(genderFilter.value);

    const experienceValue = experienceFilter.value;
    const salaryValue = salaryFilter.value;

    let visibleJobs = 0;

    jobCards.forEach(function(card) {

        // Mengambil informasi dari atribut data-* HTML
        const title = normalizeText(card.querySelector("h3").textContent);
        const company = normalizeText(card.querySelector(".company-name").textContent);

        const location = normalizeText(card.dataset.location);
        const education = normalizeText(card.dataset.education);
        const jobType = normalizeText(card.dataset.jobType);
        const gender = normalizeText(card.dataset.gender);

        const requiredExperience = Number(card.dataset.experience);
        const maximumSalary = Number(card.dataset.salaryMax);

        // 1. Pencarian berdasarkan posisi atau perusahaan
        const matchesSearch =
            searchValue === "" ||
            title.includes(searchValue) ||
            company.includes(searchValue);

        // 2. Filter lokasi
        const matchesLocation =
            locationValue === "" ||
            location.includes(locationValue);

        // 3. Filter pendidikan
        let matchesEducation = true;

        if (educationValue !== "" && educationValue !== "semua jenjang") {
            const selectedEducationLevel = getEducationLevel(educationValue);
            const requiredEducationLevel = getEducationLevel(education);

            matchesEducation =
                selectedEducationLevel >= requiredEducationLevel;
        }

        // 4. Filter pengalaman
        const matchesExperience =
            experienceValue === "" ||
            Number(experienceValue) >= requiredExperience;

        // 5. Filter tipe pekerjaan
        const matchesJobType =
            jobTypeValue === "" ||
            jobType === jobTypeValue;

        // 6. Filter gaji minimum
        const matchesSalary =
            salaryValue === "" ||
            maximumSalary >= Number(salaryValue);

        // 7. Filter jenis kelamin
        const matchesGender =
            genderValue === "" ||
            genderValue === "semua jenis kelamin" ||
            gender === "semua jenis kelamin" ||
            gender === genderValue;

        // Menggabungkan semua kriteria
        const isMatch =
            matchesSearch &&
            matchesLocation &&
            matchesEducation &&
            matchesExperience &&
            matchesJobType &&
            matchesSalary &&
            matchesGender;

        // Menampilkan atau menyembunyikan kartu
        if (isMatch) {
            card.style.display = "";
            visibleJobs++;
        } else {
            card.style.display = "none";
        }
    });

    // Menampilkan pesan jika tidak ada hasil
    noResults.style.display = visibleJobs === 0 ? "block" : "none";
}

// ======================================
// TOMBOL CARI
// ======================================

searchButton.addEventListener("click", function() {
    filterJobs();
});

// Pencarian langsung saat mengetik
searchInput.addEventListener("input", filterJobs);

// ======================================
// EVENT LISTENER FILTER
// ======================================

locationFilter.addEventListener("change", filterJobs);
educationFilter.addEventListener("change", filterJobs);
experienceFilter.addEventListener("input", filterJobs);
jobTypeFilter.addEventListener("change", filterJobs);
salaryFilter.addEventListener("input", filterJobs);
genderFilter.addEventListener("change", filterJobs);

// ======================================
// TOMBOL RESET FILTER
// ======================================

resetButton.addEventListener("click", function() {
    // Mengosongkan pencarian
    searchInput.value = "";

    // Mengembalikan semua filter ke pilihan awal
    locationFilter.value = "";
    educationFilter.value = "";
    experienceFilter.value = "";
    jobTypeFilter.value = "";
    salaryFilter.value = "";
    genderFilter.value = "";

    // Menampilkan kembali seluruh lowongan
    filterJobs();
});

// ======================================
// MENJALANKAN FILTER SAAT HALAMAN DIBUKA
// ======================================

filterJobs();