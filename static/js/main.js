/* 
   StockMaster - Main JavaScript
*/

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Feather Icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // Sidebar Toggle for Mobile
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    // Create overlay for mobile
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    if (menuToggle) {
        menuToggle.addEventListener('click', function (e) {
            e.preventDefault();
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }

    overlay.addEventListener('click', function () {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.remove();
            });
        }

        // Auto dismiss after 5 seconds if not error
        if (!alert.classList.contains('alert-error')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    });

    // Delete Confirmation Modal
    const deleteBtns = document.querySelectorAll('[data-confirm]');
    const modalOverlay = document.getElementById('delete-modal');

    if (modalOverlay) {
        const confirmBtn = modalOverlay.querySelector('.btn-danger');
        const cancelBtn = modalOverlay.querySelector('.btn-secondary');
        const itemText = modalOverlay.querySelector('.delete-item-name');
        let deleteUrl = '';

        deleteBtns.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                deleteUrl = this.getAttribute('href') || this.dataset.url;
                const name = this.dataset.name || 'this item';

                if (itemText) itemText.textContent = name;
                modalOverlay.classList.add('show');
            });
        });

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                modalOverlay.classList.remove('show');
            });
        }

        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                if (deleteUrl) {
                    // If it's a link
                    window.location.href = deleteUrl;

                    // If it's a form submission (optional, depends on implementation)
                    // const form = document.createElement('form');
                    // form.method = 'POST';
                    // form.action = deleteUrl;
                    // document.body.appendChild(form);
                    // form.submit();
                }
            });
        }

        // Close on outside click
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove('show');
            }
        });
    }

    // Dynamic Formsets (for Receipts/Deliveries)
    const addRowBtn = document.getElementById('add-row');
    if (addRowBtn) {
        addRowBtn.addEventListener('click', function () {
            const tableBody = document.querySelector('#items-table tbody');
            const totalForms = document.querySelector('#id_form-TOTAL_FORMS');
            const emptyRow = document.getElementById('empty-row').innerHTML;

            if (tableBody && totalForms && emptyRow) {
                const formIdx = totalForms.value;
                const newRow = document.createElement('tr');
                newRow.innerHTML = emptyRow.replace(/__prefix__/g, formIdx);
                tableBody.appendChild(newRow);
                totalForms.value = parseInt(formIdx) + 1;

                // Re-init icons for new row
                if (typeof feather !== 'undefined') {
                    feather.replace();
                }
            }
        });
    }

    // Remove Row
    document.addEventListener('click', function (e) {
        if (e.target.closest('.remove-row')) {
            const row = e.target.closest('tr');
            // If using Django formsets with can_delete, we might need to check a hidden box
            // For now, assuming simple JS removal for new rows
            if (row) {
                row.remove();
                // Note: Updating indices is complex, often better to just hide and set DELETE=on if existing
            }
        }
    });
});
