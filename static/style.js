function dismissAlert(alert) {
    alert.classList.add('hide');
    setTimeout(() => alert.remove(), 250);
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert-close').forEach(button => {
        button.addEventListener('click', function () {
            dismissAlert(button.closest('.alert'));
        });
    });

    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            if (document.body.contains(alert)) {
                dismissAlert(alert);
            }
        }, 4000);
    });
});

function openDeleteModal(button) {
    const modal = document.getElementById('deleteModal');
    const title = document.getElementById('deleteModalTitle');
    const form = document.getElementById('deleteForm');
    title.textContent = button.dataset.title;
    form.action = `/admin/properties/${button.dataset.id}/delete`;
    modal.classList.add('visible');
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.remove('visible');
}
