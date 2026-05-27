// Cloud Billing System - Main JS
document.addEventListener('DOMContentLoaded', function() {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    var toastList = toastElList.map(function(el) { return new bootstrap.Toast(el); });
    toastList.forEach(function(toast) { toast.show(); });
});
