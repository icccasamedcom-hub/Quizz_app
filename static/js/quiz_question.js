
    const attemptId = "{{ attempt._id }}";
    const questionId = parseInt("{{ attempt.current_question }}");
    let selectedAnswer = null;

    document.querySelectorAll('.option').forEach(option => {
        option.addEventListener('click', function () {
            document.querySelectorAll('.option').forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
            selectedAnswer = this.dataset.answer;
            document.getElementById('nextBtn').disabled = false;
        });
    });

    document.getElementById('nextBtn').addEventListener('click', async function () {
        if (!selectedAnswer) return;

        try {
            const response = await fetch(`/quiz/attempt/${attemptId}/answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer: selectedAnswer
                })
            });

            if (response.ok) {
                if (question_number == total_questions) {
                    window.location.href = `/quiz/attempt/${attemptId}/complete`;
                } else {
                    window.location.href = `/quiz/attempt/${attemptId}`;
                }
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue');
        }
    });
