document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard navigation for device rows
    const deviceRows = document.querySelectorAll('.device-row');
    deviceRows.forEach(row => {
        row.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const commandBtn = row.querySelector('.btn-command');
                if (commandBtn) {
                    commandBtn.click();
                }
            }
        });
    });

    // Handle action button loading states
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.add('loading');
            requestAnimationFrame(() => btn.classList.remove('loading'));
        });
    });
});
