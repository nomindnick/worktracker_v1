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

    // Confirm before archiving (uses native confirm for archive form page)
    const archiveForms = document.querySelectorAll('form[action*="/archive"]');
    archiveForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to archive this project?')) {
                e.preventDefault();
            }
        });
    });

    // Custom confirmation modal for data-confirm forms
    const modal = document.getElementById('confirm-modal');
    const modalMessage = document.getElementById('confirm-message');
    const confirmOk = document.getElementById('confirm-ok');
    const confirmCancel = document.getElementById('confirm-cancel');
    let pendingForm = null;

    // Handle forms with data-confirm attribute
    document.querySelectorAll('form[data-confirm]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            pendingForm = form;
            modalMessage.textContent = form.getAttribute('data-confirm');
            modal.style.display = 'flex';
        });
    });

    // Modal cancel button
    if (confirmCancel) {
        confirmCancel.addEventListener('click', function() {
            modal.style.display = 'none';
            pendingForm = null;
        });
    }

    // Modal confirm button
    if (confirmOk) {
        confirmOk.addEventListener('click', function() {
            modal.style.display = 'none';
            if (pendingForm) {
                // Remove the data-confirm to prevent re-triggering
                pendingForm.removeAttribute('data-confirm');
                pendingForm.submit();
            }
        });
    }

    // Close modal on overlay click
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
                pendingForm = null;
            }
        });
    }

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
            modal.style.display = 'none';
            pendingForm = null;
        }
    });

    // Status preview expand/collapse
    document.querySelectorAll('.btn-expand').forEach(function(button) {
        button.addEventListener('click', function() {
            var preview = this.closest('.status-preview');
            var previewText = preview.querySelector('.preview-text');
            var fullText = this.getAttribute('data-full-text');

            if (this.textContent === 'Show more...') {
                this.setAttribute('data-preview-text', previewText.textContent);
                previewText.textContent = fullText;
                this.textContent = 'Show less';
            } else {
                previewText.textContent = this.getAttribute('data-preview-text');
                this.textContent = 'Show more...';
            }
        });
    });
});
