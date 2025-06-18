document.addEventListener('DOMContentLoaded', function () {
    
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

    
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.add('loading');
            setTimeout(() => {
                btn.classList.remove('loading');
            }, 500); 
        });
    });
});
