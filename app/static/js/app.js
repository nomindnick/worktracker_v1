// Legal Worklist - Minimal JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Quick date buttons for follow-up form
    const quickDateButtons = document.querySelectorAll('.quick-dates button[data-days]');
    const dueDateInput = document.getElementById('due_date');

    quickDateButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const days = parseInt(this.getAttribute('data-days'));
            const date = new Date();
            date.setDate(date.getDate() + days);

            // Format as YYYY-MM-DD for input[type="date"]
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');

            if (dueDateInput) {
                dueDateInput.value = `${year}-${month}-${day}`;
            }
        });
    });

    // Set default internal deadline to 2 weeks from today for new projects
    const internalDeadlineInput = document.getElementById('internal_deadline');
    if (internalDeadlineInput && !internalDeadlineInput.value) {
        const date = new Date();
        date.setDate(date.getDate() + 14);

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');

        internalDeadlineInput.value = `${year}-${month}-${day}`;
    }

    // Confirm before archiving
    const archiveForms = document.querySelectorAll('form[action*="/archive"]');
    archiveForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to archive this project?')) {
                e.preventDefault();
            }
        });
    });
});
