document.addEventListener('DOMContentLoaded', function() {
    const commandForm = document.getElementById('commandForm');
    const outputDisplay = document.getElementById('outputDisplay');

    commandForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get the command and device IP
        const command = document.getElementById('command').value;
        const deviceIp = document.querySelector('input[name="device_ip"]').value;
        
        // Show loading state
        commandForm.classList.add('loading');
        outputDisplay.innerHTML = '<p>Executing command...</p>';
        
        try {
            const response = await fetch('/execute-command/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ 
                    command: command,
                    device_ip: deviceIp
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                outputDisplay.innerHTML = `<pre>${JSON.stringify(data.output, null, 2)}</pre>`;
            } else {
                outputDisplay.innerHTML = `<p class="error">Error: ${data.message}</p>`;
            }
        } catch (error) {
            outputDisplay.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        } finally {
            commandForm.classList.remove('loading');
        }
    });
});