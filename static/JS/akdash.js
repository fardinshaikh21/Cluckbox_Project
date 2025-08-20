function calculateTotal(row) {
    const rate = parseFloat(row.querySelector(".rate").textContent);
    const quantity = parseFloat(row.querySelector("input").value) || 0;
    const totalCell = row.querySelector(".row-total");
    const total = rate * quantity;
    totalCell.textContent = total.toFixed(2);
    calculateGrandTotal();
}

function calculateGrandTotal() {
    const totalCells = document.querySelectorAll(".row-total");
    let grandTotal = 0;
    totalCells.forEach(cell => {
        grandTotal += parseFloat(cell.textContent) || 0;
    });
    document.querySelector("#grand-total").textContent = grandTotal.toFixed(2);
}