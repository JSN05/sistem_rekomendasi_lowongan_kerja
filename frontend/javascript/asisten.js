const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = chatForm.querySelector("button");

// Kriteria pencarian (null = belum diketahui). Kunci sama dengan API backend.
let criteria = {
    position: null, location: null, education: null, experience: null,
    jobType: null, salaryMin: null, gender: null
};

// Atribut yang sedang ditanyakan asisten (dikirim ke backend agar jawaban singkat
// seperti "1 tahun" atau "5 juta" dipahami sesuai konteks pertanyaan)
let asked = null;

const criteriaLabels = {
    position: "Posisi Pekerjaan",
    location: "Lokasi",
    education: "Pendidikan",
    experience: "Pengalaman",
    jobType: "Tipe Pekerjaan",
    salaryMin: "Gaji Minimum",
    gender: "Jenis Kelamin"
};

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
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageElement;
}

function setLoading(isLoading) {
    userInput.disabled = isLoading;
    sendButton.disabled = isLoading;
    if (!isLoading) userInput.focus();
}

function showCriteriaSummary() {
    const summary = Object.keys(criteriaLabels)
        .map(key => {
            let value = criteria[key];
            if (key === "salaryMin") value = formatRupiah(value);
            if (key === "experience") value = value + " Tahun";
            return criteriaLabels[key] + ": " + value;
        })
        .join("\n");

    // Disimpan untuk halaman Rekomendasi
    localStorage.setItem("jobSearchCriteria", JSON.stringify(criteria));

    addMessage(
        "Terima kasih! Semua kriteria pencarian sudah lengkap.\n\n" +
        "Berikut rangkuman kebutuhan pekerjaan kamu:\n\n" + summary +
        "\n\nKamu dapat melanjutkan ke halaman Rekomendasi, atau mengetik lagi untuk mengubah kriteria.",
        "ai"
    );

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

chatForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = userInput.value.trim();
    if (message === "") return;

    addMessage(message, "user");
    userInput.value = "";
    setLoading(true);

    const typing = addMessage("Sedang memproses...", "ai");

    try {
        // Backend: Llama 3.2 mengekstraksi 7 atribut, lalu menentukan pertanyaan berikutnya
        const result = await apiPost("/api/chat", { message, criteria, asked });

        typing.remove();
        criteria = result.criteria;
        asked = result.asked;

        if (result.complete) {
            const firstLine = result.reply.replace("Semua kriteria sudah lengkap.", "").trim();
            if (firstLine) addMessage(firstLine, "ai");
            showCriteriaSummary();
        } else {
            addMessage(result.reply, "ai");
        }
    } catch (error) {
        typing.remove();
        addMessage(error.message, "ai");
    } finally {
        setLoading(false);
    }
});
