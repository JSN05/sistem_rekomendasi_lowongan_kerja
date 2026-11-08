// Mengambil kriteria pencarian dari localStorage
const criteria = JSON.parse(localStorage.getItem("jobSearchCriteria"));

// Data dummy lowongan pekerjaan
const jobs = [
    {
        id: "sales-executive",
        title: "Sales Executive",
        company: "PT Maju Bersama",
        location: "Jakarta Selatan",
        education: "SMA/SMK/Sederajat",
        experience: 1,
        jobType: "Full-Time",
        salaryMin: 5000000,
        salaryMax: 7000000,
        gender: "Semua Jenis Kelamin"
    },
    {
        id: "business-development",
        title: "Business Development",
        company: "PT Digital Nusantara",
        location: "Jakarta Pusat",
        education: "S1",
        experience: 2,
        jobType: "Full-Time",
        salaryMin: 7000000,
        salaryMax: 10000000,
        gender: "Semua Jenis Kelamin"
    },
    {
        id: "marketing-staff",
        title: "Marketing Staff",
        company: "PT Kreatif Indonesia",
        location: "Bandung",
        education: "D3/D4",
        experience: 0,
        jobType: "Kontrak",
        salaryMin: 4000000,
        salaryMax: 5500000,
        gender: "Semua Jenis Kelamin"
    },
    {
        id: "account-executive",
        title: "Account Executive",
        company: "PT Solusi Bisnis",
        location: "Surabaya",
        education: "S1",
        experience: 1,
        jobType: "Full-Time",
        salaryMin: 5500000,
        salaryMax: 8000000,
        gender: "Semua Jenis Kelamin"
    }
];

// Mengubah teks menjadi format yang lebih mudah dibandingkan
function normalizeText(value) {
    return String(value || "")
        .toLowerCase()
        .trim()
        .replace(/[-_]/g, " ")
        .replace(/\s+/g, " ");
}

// Mengambil angka dari nilai pengalaman
function getNumber(value) {
    const match = String(value || "").match(/\d+/);
    return match ? Number(match[0]) : null;
}

// Mengambil angka gaji dari berbagai format
function getSalaryNumber(value) {
    if (typeof value === "number") {
        return value;
    }

    let text = String(value || "").toLowerCase().trim();

    if (!text) return 0;

    const number = parseFloat(
        text.replace(/[^\d.,]/g, "").replace(",", ".")
    );

    if (isNaN(number)) return 0;

    if (text.includes("juta") || text.includes("jt")) {
        return number * 1000000;
    }

    return number;
}

// Mengubah angka menjadi format Rupiah
function formatRupiah(value) {
    return new Intl.NumberFormat("id-ID", {
        style: "currency",
        currency: "IDR",
        maximumFractionDigits: 0
    }).format(value);
}

// Mengubah pendidikan menjadi tingkat pendidikan
function getEducationLevel(value) {
    const education = normalizeText(value);

    if (education.includes("sd")) return 1;
    if (education.includes("smp")) return 2;

    if (
        education.includes("sma") ||
        education.includes("smk") ||
        education.includes("sederajat")
    ) {
        return 3;
    }

    if (education.includes("d3") || education.includes("d4")) {
        return 4;
    }

    if (education === "s1") return 5;
    if (education === "s2") return 6;
    if (education === "s3") return 7;

    return 0;
}

// Memeriksa kecocokan posisi pekerjaan
function matchPosition(userPosition, jobTitle) {
    const position = normalizeText(userPosition);
    const title = normalizeText(jobTitle);

    if (!position) return false;

    const salesKeywords = [
        "sales",
        "account executive",
        "account manager"
    ];

    const businessKeywords = [
        "business",
        "business development",
        "partnership",
        "commercial"
    ];

    const marketingKeywords = [
        "marketing",
        "digital marketing",
        "brand"
    ];

    if (salesKeywords.some(keyword => position.includes(keyword))) {
        return (
            title.includes("sales") ||
            title.includes("account executive")
        );
    }

    if (businessKeywords.some(keyword => position.includes(keyword))) {
        return (
            title.includes("business") ||
            title.includes("account executive")
        );
    }

    if (marketingKeywords.some(keyword => position.includes(keyword))) {
        return title.includes("marketing");
    }

    return title.includes(position);
}

// Menghitung kecocokan satu lowongan dengan kriteria pengguna
function calculateMatch(job, criteria) {
    let matched = 0;
    const reasons = [];

    // 1. Posisi pekerjaan
    if (matchPosition(criteria.position, job.title)) {
        matched++;
        reasons.push("Posisi pekerjaan sesuai");
    }

    // 2. Lokasi
    const userLocation = normalizeText(criteria.location);
    const jobLocation = normalizeText(job.location);

    if (
        userLocation &&
        (
            jobLocation.includes(userLocation) ||
            userLocation.includes(jobLocation)
        )
    ) {
        matched++;
        reasons.push("Lokasi pekerjaan sesuai");
    }

    // 3. Pendidikan
    const userEducation = getEducationLevel(criteria.education);
    const jobEducation = getEducationLevel(job.education);

    if (userEducation > 0 && userEducation >= jobEducation) {
        matched++;
        reasons.push("Pendidikan memenuhi persyaratan");
    }

    // 4. Pengalaman
    const userExperience = getNumber(criteria.experience);

    if (
        userExperience !== null &&
        userExperience >= job.experience
    ) {
        matched++;
        reasons.push("Pengalaman kerja memenuhi persyaratan");
    }

    // 5. Tipe pekerjaan
    const userJobType = normalizeText(criteria.jobType);
    const jobType = normalizeText(job.jobType);

    if (userJobType && userJobType === jobType) {
        matched++;
        reasons.push("Tipe pekerjaan sesuai");
    }

    // 6. Gaji minimum
    const userSalary = getSalaryNumber(criteria.salaryMin);

    if (userSalary <= job.salaryMax) {
        matched++;
        reasons.push("Rentang gaji memenuhi harapan minimum");
    }

    // 7. Jenis kelamin
    const userGender = normalizeText(criteria.gender);
    const jobGender = normalizeText(job.gender);

    if (
        !userGender ||
        userGender.includes("semua") ||
        jobGender.includes("semua") ||
        userGender === jobGender
    ) {
        matched++;
        reasons.push("Persyaratan jenis kelamin sesuai");
    }

    const percentage = Math.round((matched / 7) * 100);

    return {
        percentage,
        matched,
        reasons
    };
}

// Menampilkan kriteria pencarian
function displayCriteria() {
    document.getElementById("criteriaPosition").textContent =
        criteria.position || "-";

    document.getElementById("criteriaLocation").textContent =
        criteria.location || "-";

    document.getElementById("criteriaEducation").textContent =
        criteria.education || "-";

    document.getElementById("criteriaExperience").textContent =
        criteria.experience
            ? `${criteria.experience} Tahun`
            : "0 Tahun";

    document.getElementById("criteriaJobType").textContent =
        criteria.jobType || "-";

    document.getElementById("criteriaSalary").textContent =
        formatRupiah(getSalaryNumber(criteria.salaryMin));

    document.getElementById("criteriaGender").textContent =
        criteria.gender || "-";
}

// Membuat tampilan satu kartu rekomendasi
function createRecommendationCard(job, result) {
    const card = document.createElement("div");
    card.className = "recommendation-card";

    const reasonText = result.reasons.length > 0
        ? result.reasons.join(", ") + "."
        : "Belum terdapat kriteria yang sesuai.";

    card.innerHTML = `
        <div class="recommendation-card-header">
            <div>
                <h3>${job.title}</h3>
                <p class="company-name">${job.company}</p>
            </div>

            <div class="match-score">
                <strong>${result.percentage}%</strong>
                <span>Kecocokan</span>
            </div>
        </div>

        <div class="job-info">
            <span>${job.location}</span>
            <span>${job.education}</span>
            <span>${job.jobType}</span>
        </div>

        <p class="job-salary">
            ${formatRupiah(job.salaryMin)} - ${formatRupiah(job.salaryMax)}
        </p>

        <div class="match-reason">
            <strong>Alasan Rekomendasi:</strong>
            <p>${reasonText}</p>
            <p>${result.matched} dari 7 kriteria terpenuhi.</p>
        </div>

        <a href="detail.html?id=${job.id}" class="job-button">
            Lihat Lowongan
        </a>
    `;

    return card;
}

// Menampilkan seluruh hasil rekomendasi
function displayRecommendations() {
    const container = document.getElementById("recommendationContainer");

    // Hitung kecocokan setiap lowongan
    const results = jobs.map(job => {
        const result = calculateMatch(job, criteria);

        return {
            job,
            ...result
        };
    });

    // Urutkan berdasarkan persentase kecocokan tertinggi
    results.sort((a, b) => b.percentage - a.percentage);

    // Kosongkan hasil sebelumnya
    container.innerHTML = "";

    // Tampilkan lowongan berdasarkan urutan kecocokan
    results.forEach(result => {
        const card = createRecommendationCard(
            result.job,
            result
        );

        container.appendChild(card);
    });

    document.getElementById("recommendationDescription").textContent =
        `Ditemukan ${results.length} lowongan yang telah diurutkan berdasarkan tingkat kecocokan dengan kriteria Anda.`;
}

// Periksa apakah kriteria tersedia
if (!criteria) {
    document.querySelector(".criteria-section").style.display = "none";

    document.getElementById("recommendationDescription").textContent =
        "Anda belum memiliki kriteria pencarian. Silakan isi kriteria melalui Asisten AI terlebih dahulu.";

    document.getElementById("recommendationContainer").innerHTML = `
        <div class="recommendation-card">
            <p>Belum ada kriteria pencarian yang tersimpan.</p>
            <a href="asisten.html" class="job-button">
                Mulai Pencarian
            </a>
        </div>
    `;
} else {
    displayCriteria();
    displayRecommendations();
}