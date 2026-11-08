const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatMessages = document.getElementById("chatMessages");

// DATA KRITERIA PENCARIAN
const criteria = {
    position: "",
    location: "",
    education: "",
    experience: "",
    jobType: "",
    salaryMin: "",
    gender: ""
};

// Urutan pertanyaan yang akan diajukan
const questions = {
    position: "Posisi pekerjaan apa yang kamu inginkan? Contohnya Sales, Marketing, atau Business Development.",
    location: "Di kota atau daerah mana kamu ingin bekerja?",
    education: "Apa pendidikan terakhir kamu? Contohnya SMA/SMK, D3/D4, S1, S2, atau S3.",
    experience: "Berapa tahun pengalaman kerja yang kamu miliki? Jika belum memiliki pengalaman, jawab 0 tahun.",
    jobType: "Jenis pekerjaan apa yang kamu inginkan? Contohnya Full-Time, Kontrak, Freelance, Part-Time, atau Magang.",
    salaryMin: "Berapa gaji minimum yang kamu harapkan? Contohnya Rp5.000.000 atau 5 juta.",
    gender: "Apa jenis kelamin yang ingin kamu pilih untuk kriteria lowongan? Jawab laki-laki, perempuan, atau semua."
};

// Label kriteria untuk rangkuman
const criteriaLabels = {
    position: "Posisi Pekerjaan",
    location: "Lokasi",
    education: "Pendidikan",
    experience: "Pengalaman",
    jobType: "Tipe Pekerjaan",
    salaryMin: "Gaji Minimum",
    gender: "Jenis Kelamin"
};

// Kriteria yang sedang ditanyakan
let currentQuestion = "position";

// FUNGSI MENAMPILKAN PESAN
function addMessage(message, sender) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender + "-message");

    const avatar = document.createElement("div");
    avatar.classList.add("message-avatar");
    avatar.textContent = sender === "ai" ? "AI" : "Kamu";

    const content = document.createElement("div");
    content.classList.add("message-content");
    content.textContent = message;

    messageElement.appendChild(avatar);
    messageElement.appendChild(content);

    chatMessages.appendChild(messageElement);

    // Mengatur agar pesan terbaru terlihat
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// FUNGSI NORMALISASI TEKS
function normalizeText(text) {
    return text
        .toLowerCase()
        .trim()
        .replace(/\s+/g, " ");
}

// MENGENALI POSISI PEKERJAAN
function extractPosition(text) {
    const positions = [
        "business development",
        "account executive",
        "sales executive",
        "sales representative",
        "key account",
        "relationship officer",
        "marketing staff",
        "digital marketing",
        "trade marketing",
        "marketing",
        "sales",
        "promotor",
        "partnership",
        "merchant",
        "commercial",
        "retail"
    ];

    return positions.find(position => text.includes(position)) || "";
}

// MENGENALI LOKASI
function extractLocation(text) {
    const locations = [
        "jakarta selatan",
        "jakarta pusat",
        "jakarta barat",
        "jakarta timur",
        "jakarta utara",
        "kepulauan seribu",
        "yogyakarta",
        "di yogyakarta",
        "surabaya",
        "bandung",
        "semarang",
        "medan",
        "makassar",
        "palembang",
        "denpasar",
        "tangerang",
        "bekasi",
        "depok",
        "bogor",
        "jakarta"
    ];

    return locations.find(location => text.includes(location)) || "";
}

// MENGENALI PENDIDIKAN
function extractEducation(text) {
    if (/\bs3\b/.test(text)) return "S3";
    if (/\bs2\b/.test(text)) return "S2";
    if (/\bs1\b/.test(text)) return "S1";
    if (/\bd3\b|\bd4\b/.test(text)) return "D3/D4";

    if (
        text.includes("sma") ||
        text.includes("smk")
    ) {
        return "SMA/SMK/Sederajat";
    }

    if (
        text.includes("smp") ||
        text.includes("mts")
    ) {
        return "SMP/Sederajat";
    }

    if (
        text.includes("sd") ||
        text.includes("sekolah dasar")
    ) {
        return "SD/Sederajat";
    }

    return "";
}

// MENGENALI PENGALAMAN
function extractExperience(text) {
    if (
        text.includes("fresh graduate") ||
        text.includes("belum punya pengalaman") ||
        text.includes("tanpa pengalaman") ||
        text.includes("belum berpengalaman")
    ) {
        return 0;
    }

    const match = text.match(/(\d+)\s*(tahun|thn)/);

    if (match) {
        return Number(match[1]);
    }

    return null;
}

// MENGENALI TIPE PEKERJAAN
function extractJobType(text) {
    if (text.includes("full-time") || text.includes("full time")) {
        return "Full-Time";
    }

    if (text.includes("part-time") || text.includes("part time")) {
        return "Part-Time";
    }

    if (text.includes("freelance")) {
        return "Freelance";
    }

    if (text.includes("kontrak")) {
        return "Kontrak";
    }

    if (text.includes("magang") || text.includes("internship")) {
        return "Magang";
    }

    return "";
}

// MENGENALI GAJI MINIMUM
function extractSalary(text) {
    const salaryText = text.replace(/\./g, "").replace(/,/g, ".");

    // Contoh: 5 juta, 5jt, atau 5.5 juta
    const millionMatch = salaryText.match(
        /(?:rp\s*)?(\d+(?:\.\d+)?)\s*(juta|jt)\b/
    );

    if (millionMatch) {
        return Math.round(Number(millionMatch[1]) * 1000000);
    }

    // Contoh: 5000000 atau Rp5000000
    const numberMatch = salaryText.match(
        /(?:rp\s*)?(\d{6,})\b/
    );

    if (numberMatch) {
        return Number(numberMatch[1]);
    }

    return null;
}

// MENGENALI JENIS KELAMIN
function extractGender(text) {
    if (
        text.includes("semua") ||
        text.includes("bebas") ||
        text.includes("tidak ada preferensi")
    ) {
        return "Semua";
    }

    if (
        text.includes("perempuan") ||
        text.includes("wanita")
    ) {
        return "Perempuan";
    }

    if (
        text.includes("laki-laki") ||
        text.includes("laki laki") ||
        text.includes("pria")
    ) {
        return "Laki-laki";
    }

    return "";
}

// MENGAMBIL KRITERIA DARI INPUT
function extractCriteria(text) {
    const normalized = normalizeText(text);

    const position = extractPosition(normalized);
    const location = extractLocation(normalized);
    const education = extractEducation(normalized);
    const experience = extractExperience(normalized);
    const jobType = extractJobType(normalized);
    const salary = extractSalary(normalized);
    const gender = extractGender(normalized);

    if (position) criteria.position = position;
    if (location) criteria.location = location;
    if (education) criteria.education = education;

    if (experience !== null) {
        criteria.experience = experience;
    }

    if (jobType) criteria.jobType = jobType;

    if (salary !== null) {
        criteria.salaryMin = salary;
    }

    if (gender) criteria.gender = gender;
}

// MENGECEK KRITERIA YANG BELUM LENGKAP
function getMissingCriteria() {
    return Object.keys(criteria).filter(key => {
        return criteria[key] === "";
    });
}

// MENGAJUKAN PERTANYAAN BERIKUTNYA
function askNextQuestion() {
    const missingCriteria = getMissingCriteria();

    if (missingCriteria.length > 0) {
        currentQuestion = missingCriteria[0];

        addMessage(questions[currentQuestion], "ai");
    } else {
        currentQuestion = null;
        showCriteriaSummary();
    }
}

// MENYIMPAN JAWABAN KRITERIA
function saveCurrentAnswer(text) {
    if (!currentQuestion) return;

    const answer = text.trim();
    const normalized = normalizeText(answer);

    switch (currentQuestion) {
        case "position":
            criteria.position = answer;
            break;

        case "location":
            criteria.location = answer;
            break;

        case "education":
            criteria.education =
                extractEducation(normalized) || answer;
            break;

        case "experience":
            criteria.experience = extractExperience(normalized);

            if (criteria.experience === null) {
                const number = normalized.match(/\d+/);
                criteria.experience = number
                    ? Number(number[0])
                    : answer;
            }
            break;

        case "jobType":
            criteria.jobType =
                extractJobType(normalized) || answer;
            break;

        case "salaryMin":
            criteria.salaryMin = extractSalary(normalized);

            if (criteria.salaryMin === null) {
                criteria.salaryMin = answer;
            }
            break;

        case "gender":
            criteria.gender =
                extractGender(normalized) || answer;
            break;
    }

    currentQuestion = null;
}

// FORMAT RUPIAH
function formatRupiah(amount) {
    if (typeof amount !== "number") {
        return amount;
    }

    return "Rp" + amount.toLocaleString("id-ID");
}

// MENAMPILKAN RANGKUMAN KRITERIA
function showCriteriaSummary() {
    const summary = Object.keys(criteria)
        .map(key => {
            let value = criteria[key];

            if (key === "salaryMin") {
                value = formatRupiah(value);
            }

            if (key === "experience") {
                value = value + " Tahun";
            }

            return criteriaLabels[key] + ": " + value;
        })
        .join("\n");

    // Simpan kriteria untuk digunakan halaman berikutnya
    localStorage.setItem(
        "jobSearchCriteria",
        JSON.stringify(criteria)
    );

    addMessage(
        "Terima kasih! Semua kriteria pencarian sudah lengkap.\n\n" +
        "Berikut rangkuman kebutuhan pekerjaan kamu:\n\n" +
        summary +
        "\n\nKriteria ini sudah disimpan. Kamu dapat melanjutkan ke halaman Rekomendasi.",
        "ai"
    );

    // Membuat tombol menuju halaman rekomendasi
    const button = document.createElement("a");
    button.href = "rekomendasi.html";
    button.textContent = "Lihat Rekomendasi Pekerjaan";
    button.classList.add("recommendation-button");

    const wrapper = document.createElement("div");
    wrapper.style.marginLeft = "48px";
    wrapper.appendChild(button);

    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// EVENT SUBMIT CHAT
chatForm.addEventListener("submit", function(event) {
    event.preventDefault();

    const message = userInput.value.trim();

    if (message === "") return;

    // Menampilkan pesan pengguna
    addMessage(message, "user");

    // Mengosongkan input
    userInput.value = "";

    // Jika sedang menjawab pertanyaan tertentu
    if (currentQuestion) {
        saveCurrentAnswer(message);
    }

    // Mengenali kriteria yang disebutkan dalam pesan
    extractCriteria(message);

    // Memeriksa dan menanyakan kriteria berikutnya
    askNextQuestion();
});