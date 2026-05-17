/**
 * Dijital İmza Aracı — JavaScript
 * Yardım modalı ve UI etkileşimleri
 */

// Yardım modalı — ilk girişte göster
document.addEventListener('DOMContentLoaded', function () {
    const helpShown = localStorage.getItem('helpModalShown');
    if (!helpShown) {
        const modal = document.getElementById('helpModal');
        if (modal) {
            modal.classList.add('show');
        }
    }
});

function closeHelpModal() {
    const modal = document.getElementById('helpModal');
    if (modal) {
        modal.classList.remove('show');
        localStorage.setItem('helpModalShown', 'true');
    }
}

// Modal dışına tıklanınca kapat
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal-overlay')) {
        closeHelpModal();
    }
});
