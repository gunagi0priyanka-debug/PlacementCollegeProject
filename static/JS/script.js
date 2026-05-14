function toggleFields() {
    const userType = document.getElementById("user_type").value;
    const studentDiv = document.getElementById("student-fields");
    const companyDiv = document.getElementById("company-fields");

    if (userType === "student") {
        studentDiv.style.display = "block";
        companyDiv.style.display = "none";
        // Make student fields required if visible
        studentDiv.querySelectorAll('input').forEach(i => i.required = true);
        companyDiv.querySelectorAll('input').forEach(i => i.required = false);
    } else if (userType === "company") {
        studentDiv.style.display = "none";
        companyDiv.style.display = "block";
        // Make company fields required if visible
        studentDiv.querySelectorAll('input').forEach(i => i.required = false);
        companyDiv.querySelectorAll('input').forEach(i => i.required = true);
    }
}

// Run once on page load to ensure correct state
document.addEventListener('DOMContentLoaded', toggleFields);