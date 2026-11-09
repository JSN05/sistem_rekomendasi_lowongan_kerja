const jobId = new URLSearchParams(window.location.search).get("id");

function setText(id, value) {
    document.getElementById(id).textContent = value;
}

function fillList(containerId, items, tag) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    items.forEach(text => {
        const el = document.createElement(tag);
        el.textContent = text;
        container.appendChild(el);
    });
}

function displayJobDetail(job) {
    const salary = formatSalary(job.salaryMin, job.salaryMax);
    const location = job.location || "-";

    setText("jobTitle", job.title);
    setText("companyName", job.company);
    setText("jobTypeTag", job.jobType || "-");
    setText("locationTag", location);
    setText("salaryHeader", salary);

    setText("jobLocation", location);
    setText("jobEducation", job.education || "-");
    setText("jobExperience", formatExperience(job));
    setText("jobType", job.jobType || "-");
    setText("jobGender", job.gender || "Tidak ada ketentuan");
    setText("jobSalary", salary);

    // CSV hanya berisi atribut terstruktur, sehingga deskripsi disusun dari atribut tersebut
    const description = [
        `${job.company} membuka lowongan ${job.title} untuk penempatan di ${location}.`
    ];
    if (job.role) description.push(`Peran pekerjaan: ${job.role}.`);
    if (job.updatedAt) description.push(job.updatedAt + ".");
    if (job.closed) description.push("Lowongan ini sudah ditutup.");
    fillList("jobDescription", description, "p");

    const requirements = [];
    if (job.education) requirements.push("Pendidikan: " + job.education + ".");
    requirements.push("Pengalaman: " + formatExperience(job) + ".");
    requirements.push("Tipe pekerjaan: " + (job.jobType || "-") + ".");
    if (job.gender) requirements.push("Jenis kelamin: " + job.gender + ".");
    if (job.maxAge) requirements.push("Usia maksimal: " + job.maxAge + " tahun.");
    fillList("jobRequirements", requirements, "li");

    setText("sidebarCompany", job.company);
    setText("sidebarPosition", job.title);
    setText("sidebarLocation", location);
    setText("sidebarJobType", job.jobType || "-");

    const link = document.getElementById("kitalulusLink");
    if (job.url) {
        link.href = job.url;
    } else {
        link.style.display = "none";
    }

    document.title = "Detail " + job.title;
}

function showNotFound(message) {
    setText("jobTitle", "Lowongan Tidak Ditemukan");
    setText("companyName", message);
    document.querySelector(".detail-content").style.display = "none";
    document.querySelector(".detail-salary").style.display = "none";
    document.querySelector(".detail-tags").style.display = "none";
}

async function loadJob() {
    if (!jobId) {
        showNotFound("Silakan kembali ke daftar lowongan.");
        return;
    }
    try {
        displayJobDetail(await apiGet("/api/jobs/" + encodeURIComponent(jobId)));
    } catch (error) {
        showNotFound(error.status === 404 ? "Silakan kembali ke daftar lowongan." : error.message);
    }
}

loadJob();
