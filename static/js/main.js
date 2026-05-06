// main.js - ToyZone Base JS functionality

document.addEventListener('DOMContentLoaded', function() {
    // Hide django messages automatically after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-important)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Handle Navbar scroll effect
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
            } else {
                navbar.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
            }
        });
    }

    // Interactive effects for category cards and promos
    const interactiveElements = document.querySelectorAll('.category-card, .promo-card, .age-card');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
        });
    });
});
