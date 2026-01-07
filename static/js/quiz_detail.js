    document.getElementById('startForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const response = await fetch(this.action, {
                method: 'POST',
            });
            
            if (response.ok) {
                const data = await response.json();
                window.location.href = `/quiz/attempt/${data.attempt_id}`;
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue');
        }
    });
