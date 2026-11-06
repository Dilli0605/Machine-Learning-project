// Student Performance Prediction - Main Script

document.addEventListener('DOMContentLoaded', () => {
    // Role switch label adjustment in login modal/page
    const roleStudent = document.getElementById('role_student');
    const roleAdmin = document.getElementById('role_admin');
    const userLabel = document.getElementById('userLabel');

    if (roleStudent && roleAdmin && userLabel) {
        roleStudent.addEventListener('change', () => {
            if (roleStudent.checked) {
                userLabel.textContent = 'Email or Roll Number';
            }
        });

        roleAdmin.addEventListener('change', () => {
            if (roleAdmin.checked) {
                userLabel.textContent = 'Admin Username';
            }
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
