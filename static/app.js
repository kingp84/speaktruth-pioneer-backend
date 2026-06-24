async function loadAssignmentsForDate(year, month, day) {
    const url = `https://pioneer-and-bell-speaktruth.onrender.com/assignments/api/${year}/${month}/${day}/`;

    console.log("Fetching:", url);

    try {
        const response = await fetch(url);

        console.log("Status:", response.status);

        if (!response.ok) {
            console.error("Fetch failed:", response.statusText);
            return { assignments: [] };
        }

        const data = await response.json();
        console.log("Data received:", data);
        return data;

    } catch (err) {
        console.error("Network error:", err);
        return { assignments: [] };
    }
}

function saveAsPDF() {
    const element = document.getElementById("song-list");

    const options = {
        margin: 10,
        filename: 'song_list.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'letter', orientation: 'portrait' }
    };

    html2pdf().set(options).from(element).save();
}

// Example: attach to a date picker
document.addEventListener("DOMContentLoaded", () => {
    const dateInput = document.getElementById("date");

    if (dateInput) {
        dateInput.addEventListener("change", async () => {
            const dt = new Date(dateInput.value);
            const data = await loadAssignmentsForDate(
                dt.getFullYear(),
                dt.getMonth() + 1,
                dt.getDate()
            );

            displayAssignments(data.assignments);
            fillAssignmentFields(data.assignments);
        });
    }
});

function displayAssignments(assignments) {
    function fillAssignmentFields(assignments) {
    const roleMap = {
        "Opening Prayer": "openingprayer",
        "Closing Prayer": "closingprayer",
        "Scripture Reading": "scriptures",
        "Preaching": "preaching",
        "Invitation": "invitation",
        "Bible Class": "classteacher"
    };

    assignments.forEach(a => {
        const fieldId = roleMap[a.role];
        if (fieldId) {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = a.person || "";
            }
        }
    });
}
    container.innerHTML = "";

    assignments.forEach(a => {
        const div = document.createElement("div");
        div.className = "assignment-item";
        div.textContent = `${a.role}: ${a.person || "Unassigned"}`;
        container.appendChild(div);
    });
}