// DATA DETAIL LOWONGAN
const jobData = {
    "sales-executive": {
        title: "Sales Executive",
        company: "PT Maju Bersama",
        location: "Jakarta Selatan",
        education: "SMA/SMK/Sederajat",
        experience: "Minimal 1 Tahun",
        jobType: "Full-Time",
        gender: "Semua Jenis Kelamin",
        salaryMin: 5000000,
        salaryMax: 7000000,

        description: [
            "PT Maju Bersama sedang mencari kandidat untuk posisi Sales Executive yang bertanggung jawab dalam menawarkan produk dan layanan perusahaan kepada calon pelanggan.",
            "Kandidat diharapkan mampu membangun hubungan baik dengan pelanggan, memahami kebutuhan pasar, serta membantu perusahaan mencapai target penjualan yang telah ditentukan."
        ],

        requirements: [
            "Pendidikan minimal SMA/SMK/Sederajat.",
            "Memiliki pengalaman di bidang penjualan minimal 1 tahun.",
            "Memiliki kemampuan komunikasi yang baik.",
            "Mampu bekerja secara individu maupun tim.",
            "Mampu bekerja dengan target penjualan.",
            "Memiliki motivasi dan tanggung jawab yang tinggi."
        ],

        companyDescription:
            "PT Maju Bersama merupakan perusahaan yang bergerak di bidang penjualan dan distribusi produk. Perusahaan berfokus pada pengembangan pasar dan pelayanan kepada pelanggan."
    },

    "business-development": {
        title: "Business Development",
        company: "PT Digital Nusantara",
        location: "Jakarta Pusat",
        education: "S1",
        experience: "Minimal 2 Tahun",
        jobType: "Full-Time",
        gender: "Semua Jenis Kelamin",
        salaryMin: 7000000,
        salaryMax: 10000000,

        description: [
            "PT Digital Nusantara membuka kesempatan untuk posisi Business Development yang bertanggung jawab mengembangkan peluang bisnis dan menjalin hubungan dengan mitra perusahaan.",
            "Kandidat diharapkan mampu melakukan analisis pasar, mengidentifikasi peluang kerja sama, serta membantu meningkatkan pertumbuhan bisnis perusahaan."
        ],

        requirements: [
            "Pendidikan minimal S1.",
            "Memiliki pengalaman di bidang pengembangan bisnis minimal 2 tahun.",
            "Memiliki kemampuan komunikasi dan negosiasi yang baik.",
            "Mampu melakukan analisis peluang pasar.",
            "Mampu bekerja secara individu maupun tim.",
            "Memiliki kemampuan presentasi yang baik."
        ],

        companyDescription:
            "PT Digital Nusantara merupakan perusahaan yang bergerak di bidang layanan dan solusi digital. Perusahaan berfokus pada pengembangan bisnis serta pemanfaatan teknologi untuk mendukung kebutuhan pelanggan."
    },

    "marketing-staff": {
        title: "Marketing Staff",
        company: "PT Kreatif Indonesia",
        location: "Bandung",
        education: "D3/D4",
        experience: "Fresh Graduate",
        jobType: "Kontrak",
        gender: "Semua Jenis Kelamin",
        salaryMin: 4000000,
        salaryMax: 5500000,

        description: [
            "PT Kreatif Indonesia sedang mencari Marketing Staff untuk membantu pelaksanaan kegiatan pemasaran dan promosi produk perusahaan.",
            "Kandidat akan terlibat dalam penyusunan strategi pemasaran, pengelolaan materi promosi, serta kegiatan untuk meningkatkan jangkauan pasar."
        ],

        requirements: [
            "Pendidikan minimal D3/D4.",
            "Terbuka untuk lulusan baru.",
            "Memiliki minat di bidang pemasaran.",
            "Memiliki kemampuan komunikasi yang baik.",
            "Mampu bekerja sama dalam tim.",
            "Kreatif dan memiliki inisiatif."
        ],

        companyDescription:
            "PT Kreatif Indonesia merupakan perusahaan yang bergerak di bidang pemasaran dan layanan kreatif. Perusahaan berfokus pada kegiatan promosi dan pengembangan strategi pemasaran."
    },

    "account-executive": {
        title: "Account Executive",
        company: "PT Solusi Bisnis",
        location: "Surabaya",
        education: "S1",
        experience: "Minimal 1 Tahun",
        jobType: "Full-Time",
        gender: "Semua Jenis Kelamin",
        salaryMin: 5500000,
        salaryMax: 8000000,

        description: [
            "PT Solusi Bisnis membuka lowongan untuk posisi Account Executive yang bertanggung jawab mengelola hubungan dengan klien dan menawarkan solusi sesuai kebutuhan mereka.",
            "Kandidat diharapkan mampu menjaga hubungan baik dengan pelanggan, mengidentifikasi peluang kerja sama, serta mendukung pencapaian target perusahaan."
        ],

        requirements: [
            "Pendidikan minimal S1.",
            "Memiliki pengalaman kerja minimal 1 tahun.",
            "Memiliki kemampuan komunikasi dan negosiasi yang baik.",
            "Mampu membangun hubungan dengan klien.",
            "Berorientasi pada target.",
            "Mampu bekerja secara individu maupun tim."
        ],

        companyDescription:
            "PT Solusi Bisnis merupakan perusahaan yang bergerak di bidang layanan bisnis dan solusi untuk pelanggan. Perusahaan berfokus pada hubungan jangka panjang dengan klien dan pengembangan layanan."
    }
};

// FUNGSI FORMAT RUPIAH
function formatRupiah(amount) {
    return "Rp" + amount.toLocaleString("id-ID");
}

// MENGAMBIL ID DARI URL
const urlParams = new URLSearchParams(window.location.search);
const jobId = urlParams.get("id");

const job = jobData[jobId];

// MENAMPILKAN DETAIL LOWONGAN
function displayJobDetail(job) {
    const salary =
        formatRupiah(job.salaryMin) + " - " +
        formatRupiah(job.salaryMax);

    // Judul dan informasi utama
    document.getElementById("jobTitle").textContent = job.title;
    document.getElementById("companyName").textContent = job.company;
    document.getElementById("jobTypeTag").textContent = job.jobType;
    document.getElementById("locationTag").textContent = job.location;
    document.getElementById("salaryHeader").textContent = salary;

    // Informasi pekerjaan
    document.getElementById("jobLocation").textContent = job.location;
    document.getElementById("jobEducation").textContent = job.education;
    document.getElementById("jobExperience").textContent = job.experience;
    document.getElementById("jobType").textContent = job.jobType;
    document.getElementById("jobGender").textContent = job.gender;
    document.getElementById("jobSalary").textContent = salary;

    // Deskripsi pekerjaan
    const descriptionContainer =
        document.getElementById("jobDescription");

    descriptionContainer.innerHTML = "";

    job.description.forEach((paragraph) => {
        const p = document.createElement("p");
        p.textContent = paragraph;
        descriptionContainer.appendChild(p);
    });

    // Persyaratan pekerjaan
    const requirementContainer =
        document.getElementById("jobRequirements");

    requirementContainer.innerHTML = "";

    job.requirements.forEach((requirement) => {
        const li = document.createElement("li");
        li.textContent = requirement;
        requirementContainer.appendChild(li);
    });

    // Informasi perusahaan
    document.getElementById("companyDescription").textContent =
        job.companyDescription;

    // Informasi pada sidebar
    document.getElementById("sidebarCompany").textContent = job.company;
    document.getElementById("sidebarPosition").textContent = job.title;
    document.getElementById("sidebarLocation").textContent = job.location;
    document.getElementById("sidebarJobType").textContent = job.jobType;

    // Mengubah judul tab browser
    document.title = "Detail " + job.title;
}

// VALIDASI ID LOWONGAN
if (job) {
    displayJobDetail(job);
} else {
    document.getElementById("jobTitle").textContent =
        "Lowongan Tidak Ditemukan";

    document.getElementById("companyName").textContent =
        "Silakan kembali ke daftar lowongan.";

    document.querySelector(".detail-content").style.display = "none";
    document.querySelector(".detail-salary").style.display = "none";
    document.querySelector(".detail-tags").style.display = "none";
}