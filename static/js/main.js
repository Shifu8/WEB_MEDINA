document.addEventListener('DOMContentLoaded', function () {

    // ---- Sidebar Toggle ----
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            sidebar.classList.toggle('show');
        });
    }

    // ---- Auto-dismiss alerts after 4s ----
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 4000);
    });

    // ---- Delete confirmation ----
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            const msg = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // ---- Invoice: Add line item ----
    const addItemBtn = document.getElementById('addItemBtn');
    const itemsContainer = document.getElementById('itemsContainer');
    let itemIndex = 0;

    if (addItemBtn && itemsContainer) {
        addItemBtn.addEventListener('click', function () {
            addLineItem();
        });
    }

    // if we have a container but no items yet, add a default row
    if (itemsContainer && itemsContainer.querySelectorAll('.line-item').length === 0) {
        addLineItem();
    }

    function addLineItem(productId, quantity) {
        const div = document.createElement('div');
        div.className = 'line-item row g-2 align-items-center';
        div.dataset.index = itemIndex;

        const productOptions = document.querySelector('#productSelectTemplate')?.innerHTML || '';

        div.innerHTML =
            '<div class="col-md-5">' +
            '<select name="product_id[]" class="form-select form-select-sm product-select" required>' +
            '<option value="">Select product</option>' +
            productOptions +
            '</select>' +
            '</div>' +
            '<div class="col-md-3">' +
            '<input type="number" name="quantity[]" class="form-control form-control-sm item-qty" placeholder="Qty" min="1" value="1" required>' +
            '</div>' +
            '<div class="col-md-2">' +
            '<span class="line-total form-control-plaintext text-end fw-bold">$0.00</span>' +
            '</div>' +
            '<div class="col-md-2 text-end">' +
            '<button type="button" class="btn btn-outline-danger btn-sm remove-item"><i class="bi bi-trash"></i></button>' +
            '</div>';

        itemsContainer.appendChild(div);

        const select = div.querySelector('.product-select');
        const qtyInput = div.querySelector('.item-qty');
        const totalSpan = div.querySelector('.line-total');

        if (productId) select.value = productId;

        function updateLineTotal() {
            const pid = select.value;
            if (!pid) {
                totalSpan.textContent = '$0.00';
                return;
            }
            const qty = parseInt(qtyInput.value) || 0;
            fetch('/api/products/' + pid)
                .then(function (r) { return r.json(); })
                .then(function (product) {
                    if (product && product.price) {
                        const lineTotal = product.price * qty;
                        totalSpan.textContent = '$' + lineTotal.toFixed(2);
                        updateInvoiceTotal();
                    }
                })
                .catch(function () {
                    totalSpan.textContent = '$0.00';
                });
        }

        select.addEventListener('change', updateLineTotal);
        qtyInput.addEventListener('input', updateLineTotal);

        div.querySelector('.remove-item').addEventListener('click', function () {
            div.remove();
            updateInvoiceTotal();
        });

        itemIndex++;
        updateLineTotal();
    }

    function updateInvoiceTotal() {
        let total = 0;
        document.querySelectorAll('.line-total').forEach(function (el) {
            const val = parseFloat(el.textContent.replace('$', '')) || 0;
            total += val;
        });
        const el = document.getElementById('invoiceGrandTotal');
        if (el) el.textContent = '$' + total.toFixed(2);
    }

    // ---- Auto-calculate invoice totals when products change ----
    document.addEventListener('change', function (e) {
        if (e.target.matches('.product-select') || e.target.matches('.item-qty')) {
            updateInvoiceTotal();
        }
    });

    // ---- Confirm delete modals (Bootstrap) ----
    document.querySelectorAll('[data-bs-toggle="modal"][data-target]').forEach(function (el) {
        el.addEventListener('click', function () {
            const target = this.getAttribute('data-target');
            const modal = document.querySelector(target);
            if (modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });

    // ---- Tooltip init ----
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });

});
