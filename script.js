// 1. Function to render emails
function renderEmails(emailList) {
    const container = document.getElementById("email-results");
    container.innerHTML = ""; // clear previous results

    emailList.forEach(item => {
        const card = document.createElement("div");
        card.classList.add("email-card");

        const categoryBadge = document.createElement("span");
        categoryBadge.classList.add("category", item.category);
        categoryBadge.textContent = item.category;

        const emailText = document.createElement("div");
        emailText.classList.add("email-text");
        emailText.textContent = item.email;

        card.appendChild(categoryBadge);
        card.appendChild(emailText);

        container.appendChild(card);
    });
}

// 2. Function to decode MIME subjects
function decodeMimeString(str) {
    try {
        return decodeURIComponent(
            str.replace(/=\?utf-8\?q\?/i, "")
               .replace(/\?=/i, "")
               .replace(/_/g, " ")
               .replace(/=([A-F0-9]{2})/gi, function(match, p1) {
                   return String.fromCharCode(parseInt(p1, 16));
               })
        );
    } catch (e) {
        return str; // fallback if decoding fails
    }
}

// 3. Function to categorize emails
function categorizeEmail(subject) {
    const s = subject.toLowerCase();

    if (s.includes("crypto") || s.includes("tesla") || s.includes("offer") || s.includes("sale")) return "spam";
    if (s.includes("syllabus") || s.includes("notes") || s.includes("university") || s.includes("tata consultancy") || s.includes("software engineer")) return "university";
    if (s.includes("google developer profile")) return "personal";
    if (s.includes("shortcut to smarter") || s.includes("work")) return "work";
    if (s.includes("black friday") || s.includes("subscription")) return "ads";

    return "uncategorized"; // fallback
}

// 4. jQuery ready and AJAX
$(document).ready(function () {
    $("#emailForm").submit(function (e) {
        e.preventDefault();

        $("#loading").removeClass("hidden");
        $("#email-results").html(""); // clear previous results

        let payload = {
            email: $("#email").val(),
            password: $("#password").val(),
            count: $("#count").val()
        };

        $.ajax({
            url: '/api',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function (data) {
                $("#loading").addClass("hidden");

                // decode & categorize each email before rendering
                const processedEmails = data.map(item => ({
                    email: decodeMimeString(item.email),
                    category: categorizeEmail(decodeMimeString(item.email))
                }));

                renderEmails(processedEmails);
            },
            error: function () {
                $("#loading").addClass("hidden");
                $("#email-results").html('<p class="text-red-500">Error occurred.</p>');
            }
        });
    });
});
