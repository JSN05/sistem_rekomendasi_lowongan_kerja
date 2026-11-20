const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = chatForm.querySelector("button");
const newChatButton = document.getElementById("newChatButton");

const STORAGE_HISTORY = "assistantChatHistory";
const STORAGE_CRITERIA = "jobSearchCriteria";
const STORAGE_ASKED = "assistantAsked";

const EMPTY_CRITERIA = {
    position: null,
    location: null,
    education: null,
    experience: null,
    jobType: null,
    salaryMin: null,
    gender: null
};

const criteriaLabels = {
    position: "Posisi Pekerjaan",
    location: "Lokasi",
    education: "Pendidikan",
    experience: "Pengalaman",
    jobType: "Tipe Pekerjaan",
    salaryMin: "Gaji Minimum",
    gender: "Jenis Kelamin"
};

function loadStorage(key, fallback) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : fallback;
    } catch (error) {
        return fallback;
    }
}

let criteria = {
    ...EMPTY_CRITERIA,
    ...loadStorage(STORAGE_CRITERIA, {})
};

let asked = loadStorage(STORAGE_ASKED, null);

let chatHistory = loadStorage(STORAGE_HISTORY, []);

if (!Array.isArray(chatHistory)) {
    chatHistory = [];
}

function saveConversation() {
    localStorage.setItem(STORAGE_HISTORY, JSON.stringify(chatHistory));
    localStorage.setItem(STORAGE_CRITERIA, JSON.stringify(criteria));
    localStorage.setItem(STORAGE_ASKED, JSON.stringify(asked));
}

function renderMessage(message, sender) {
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
}

function addMessage(message, sender) {
    chatHistory.push({
        message: message,
        sender: sender
    });

    renderMessage(message, sender);
    saveConversation();

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showRecommendationButton() {
    const oldButton = document.getElementById("recommendationAction");

    if (oldButton) {
        oldButton.remove();
    }

    const wrapper = document.createElement("div");
    wrapper.id = "recommendationAction";
    wrapper.style.marginLeft = "48px";
    wrapper.style.marginTop = "12px";

    const button = document.createElement("a");
    button.href = "/Rekomendasi";
    button.textContent = "Lihat Rekomendasi Pekerjaan";
    button.classList.add("recommendation-button");

    wrapper.appendChild(button);
    chatMessages.appendChild(wrapper);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showCompletedGuidance() {
    addMessage(
        "Kamu juga bisa mengubah kriteria pencarian kapan saja. " +
        "Contohnya:\n\n" +
        "- Ganti lokasi saya menjadi Bandung.\n" +
        "- Ubah gaji minimum menjadi 7 juta.\n" +
        "- Saya ingin posisi Marketing, bukan Sales.\n\n" +
        "Kriteria lainnya akan tetap dipertahankan. " +
        "Jika ingin memulai pencarian yang benar-benar baru, " +
        "gunakan tombol Percakapan Baru.",
        "ai"
    );

    showRecommendationButton();
}

function showCriteriaSummary() {
    const summary = Object.keys(criteriaLabels)
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

    addMessage(
        "Terima kasih! Semua kriteria pencarian sudah lengkap.\n\n" +
        "Berikut rangkuman kebutuhan pekerjaan kamu:\n\n" +
        summary,
        "ai"
    );

    showCompletedGuidance();
}

function restoreConversation() {
    chatMessages.innerHTML = "";

    if (chatHistory.length === 0) {
        addMessage(
            "Halo! Selamat datang di Asisten Pencarian Kerja.\n\n" +
            "Saya bisa membantu kamu mencari lowongan kerja " +
            "di bidang penjualan dan bisnis.\n\n" +
            "Pekerjaan seperti apa yang sedang kamu cari? " +
            "Misalnya, sales, marketing, atau business development.",
            "ai"
        );
    } else {
        chatHistory.forEach(item => {
            renderMessage(item.message, item.sender);
        });
    }

    const complete = Object.keys(criteriaLabels).every(
        key => criteria[key] !== null && criteria[key] !== ""
    );

    if (complete) {
        showRecommendationButton();
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setLoading(isLoading) {
    userInput.disabled = isLoading;
    sendButton.disabled = isLoading;

    if (!isLoading) {
        userInput.focus();
    }
}

chatForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = userInput.value.trim();

    if (message === "") return;

    addMessage(message, "user");

    userInput.value = "";
    setLoading(true);

    const typing = renderTyping();

    const previousCriteria = { ...criteria };

    try {
        const result = await apiPost("/api/chat", {
            message,
            criteria,
            asked
        });

        typing.remove();

        criteria = {
            ...EMPTY_CRITERIA,
            ...result.criteria
        };

        asked = result.asked;

        saveConversation();

        const wasComplete = Object.keys(criteriaLabels).every(
            key => previousCriteria[key] !== null &&
                   previousCriteria[key] !== ""
        );

        const hasChanged = Object.keys(criteriaLabels).some(
            key => previousCriteria[key] !== criteria[key]
        );

        if (result.complete) {
            if (!wasComplete) {
                showCriteriaSummary();
            } else if (hasChanged) {
                const changed = Object.keys(criteriaLabels)
                    .filter(key => previousCriteria[key] !== criteria[key])
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

                addMessage(
                    "Kriteria pencarian berhasil diperbarui:\n\n" +
                    changed,
                    "ai"
                );

                showCompletedGuidance();
            } else {
                addMessage(
                    "Kriteria pencarian kamu masih lengkap. " +
                    "Kamu bisa melihat rekomendasi atau mengetik " +
                    "kriteria yang ingin diubah.",
                    "ai"
                );

                showRecommendationButton();
            }
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

function renderTyping() {
    const element = document.createElement("div");
    element.classList.add("message", "ai-message");

    const content = document.createElement("div");
    content.classList.add("message-content");
    content.textContent = "Sedang memproses...";

    element.appendChild(content);
    chatMessages.appendChild(element);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return element;
}

newChatButton.addEventListener("click", function () {
    const confirmed = confirm(
        "Apakah kamu yakin ingin memulai percakapan baru? " +
        "Riwayat percakapan dan kriteria sebelumnya akan dihapus."
    );

    if (!confirmed) return;

    criteria = { ...EMPTY_CRITERIA };
    asked = null;
    chatHistory = [];

    localStorage.removeItem(STORAGE_HISTORY);
    localStorage.removeItem(STORAGE_CRITERIA);
    localStorage.removeItem(STORAGE_ASKED);

    restoreConversation();
    userInput.focus();
});

restoreConversation();