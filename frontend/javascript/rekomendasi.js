// Kriteria disimpan oleh halaman Asisten AI
const criteria = JSON.parse(localStorage.getItem("jobSearchCriteria"));

function displayCriteria() {
    const show = (id, value) => { document.getElementById(id).textContent = value ?? "-"; };

    show("criteriaPosition", criteria.position);
    show("criteriaLocation", criteria.location);
    show("criteriaEducation", criteria.education);
    show("criteriaExperience", criteria.experience != null ? criteria.experience + " Tahun" : "-");
    show("criteriaJobType", criteria.jobType);
    show("criteriaSalary", criteria.salaryMin != null ? formatRupiah(criteria.salaryMin) : "-");
    show("criteriaGender", criteria.gender);
}

function createRecommendationCard(job, attributeCount) {
    const card = document.createElement("div");
    card.className = "recommendation-card";

    const reasonText = job.reasons.length > 0
        ? job.reasons.join(", ") + "."
        : "Belum terdapat kriteria yang sesuai.";

    const kitaLulusButton = job.url
        ? `<a href="${escapeHtml(job.url)}" target="_blank" rel="noopener" class="job-button secondary">Buka di Kita Lulus</a>`
        : "";

    card.innerHTML = `
        <div class="recommendation-card-header">
            <div>
                <h3>${escapeHtml(job.title)}</h3>
                <p class="company-name">${escapeHtml(job.company)}</p>
            </div>

            <div class="match-score">
                <strong>${job.percentage % 1 === 0 ? job.percentage : job.percentage.toFixed(2).replace(".", ",")}%</strong>
                <span>Kecocokan</span>
            </div>
        </div>

        <div class="job-info">
            <span>${escapeHtml(job.location || "-")}</span>
            <span>${escapeHtml(job.education || "-")}</span>
            <span>${escapeHtml(job.jobType || "-")}</span>
        </div>

        <p class="job-salary">${escapeHtml(formatSalary(job.salaryMin, job.salaryMax))}</p>

        <div class="match-reason">
            <strong>Alasan Rekomendasi:</strong>
            <p>${escapeHtml(reasonText)}</p>
            <p>${job.score} dari ${attributeCount} kriteria terpenuhi.</p>
        </div>

        <div class="card-actions">
            <a href="detail.html?id=${encodeURIComponent(job.id)}" class="job-button">Lihat Lowongan</a>
            ${kitaLulusButton}
        </div>
    `;
    return card;
}

function showMessage(text, withLink) {
    document.getElementById("recommendationContainer").innerHTML = `
        <div class="recommendation-card">
            <p>${escapeHtml(text)}</p>
            ${withLink ? '<a href="asisten.html" class="job-button">Mulai Pencarian</a>' : ""}
        </div>
    `;
}

async function displayRecommendations() {
    const container = document.getElementById("recommendationContainer");
    const description = document.getElementById("recommendationDescription");

    description.textContent = "Menghitung rekomendasi...";
    container.innerHTML = "";

    try {
        // Backend membangun Knowledge Graph, menghitung skor 7 atribut, dan mengurutkan lowongan
        const data = await apiPost("/api/recommend", { criteria, limit: 20 });

        data.items.forEach(job => container.appendChild(createRecommendationCard(job, data.attributes)));

        description.textContent =
            `Menampilkan ${data.returned} lowongan teratas dari ${data.total} lowongan, ` +
            "diurutkan berdasarkan tingkat kecocokan dengan kriteria Anda.";

        if (data.items.length === 0) showMessage("Belum ada lowongan yang tersedia.", false);
    } catch (error) {
        description.textContent = "";
        if (error.status === 422) {
            showMessage("Kriteria pencarian belum lengkap. Silakan lengkapi melalui Asisten AI.", true);
        } else {
            showMessage(error.message, false);
        }
    }
}

if (!criteria) {
    document.querySelector(".criteria-section").style.display = "none";
    document.getElementById("recommendationDescription").textContent =
        "Anda belum memiliki kriteria pencarian. Silakan isi kriteria melalui Asisten AI terlebih dahulu.";
    showMessage("Belum ada kriteria pencarian yang tersimpan.", true);
} else {
    displayCriteria();
    displayRecommendations();
}
