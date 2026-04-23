document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const generateBtn = document.getElementById('generate-btn');
    const submitBtn = document.getElementById('submit-quiz-btn');
    const resetBtn = document.getElementById('reset-btn');
    const pdfInput = document.getElementById('pdf-input');
    const fileNameDisplay = document.getElementById('file-name');
    
    // Sections
    const ingestSection = document.getElementById('ingest-section');
    const quizSection = document.getElementById('quiz-section');
    const evaluatingSection = document.getElementById('evaluating-section');
    const resultsSection = document.getElementById('results-section');
    const loader = document.getElementById('loader');
    
    // Containers
    const quizContainer = document.getElementById('quiz-container');
    const scoreContainer = document.getElementById('score-container');
    const explanationsContainer = document.getElementById('explanations-container');

    // State
    let currentQuestions = [];
    let currentContext = "";

    // Helper: Screen transitions
    function switchSection(hideElem, showElem) {
        hideElem.classList.remove('active-section');
        hideElem.classList.add('hidden');
        showElem.classList.remove('hidden');
        setTimeout(() => showElem.classList.add('active-section'), 10);
    }

    // File Selection Visual Logic
    pdfInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const fileName = e.target.files[0].name;
            fileNameDisplay.textContent = "📎 " + fileName;
            fileNameDisplay.parentElement.classList.add('has-file');
        } else {
            fileNameDisplay.textContent = 'Click to choose a PDF file';
            fileNameDisplay.parentElement.classList.remove('has-file');
        }
    });

    // Phase 1: Generate Quiz
    generateBtn.addEventListener('click', async () => {
        const file = pdfInput.files[0];
        if (!file) {
            alert("Please select a PDF file to generate a quiz.");
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);

        generateBtn.classList.add('hidden');
        loader.classList.remove('hidden');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                let errMsg = "Failed to generate quiz.";
                try {
                    const errData = await response.json();
                    if (errData.detail) errMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
                } catch(e) {}
                throw new Error("Server Error: " + errMsg);
            }
            
            const data = await response.json();
            currentQuestions = data.questions || [];
            currentContext = data.extracted_text || "No context found.";
            
            if (currentQuestions.length === 0) {
                alert("Could not generate questions. Text might be too short.");
                generateBtn.classList.remove('hidden');
                loader.classList.add('hidden');
                return;
            }

            renderQuiz(currentQuestions);
            switchSection(ingestSection, quizSection);
        } catch (error) {
            alert(error.message);
            generateBtn.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    });

    // Phase 2: Render Quiz
    function renderQuiz(questions) {
        quizContainer.innerHTML = '';
        questions.forEach((q, index) => {
            const num = index + 1;
            const qDiv = document.createElement('div');
            qDiv.className = 'question-block';
            
            let optionsHTML = '';
            q.options.forEach((opt, oIndex) => {
                optionsHTML += `
                    <li class="option-item">
                        <label class="option-label">
                            <input type="radio" name="q${index}" value="${opt}">
                            <span>${opt}</span>
                        </label>
                    </li>
                `;
            });

            qDiv.innerHTML = `
                <div class="question-text">${num}. ${q.question}</div>
                <ul class="options-list">${optionsHTML}</ul>
            `;
            quizContainer.appendChild(qDiv);
        });
    }

    // Phase 3: Submit Answers & Evaluate
    submitBtn.addEventListener('click', async () => {
        // Collect answers
        let allAnswered = true;
        const userAnswers = [];

        currentQuestions.forEach((q, index) => {
            const selected = document.querySelector(`input[name="q${index}"]:checked`);
            if (!selected) {
                allAnswered = false;
            } else {
                userAnswers.push(selected.value);
            }
        });

        if (!allAnswered) {
            alert("Please answer all questions before submitting.");
            return;
        }

        switchSection(quizSection, evaluatingSection);

        let correctCount = 0;
        let resultsHTML = '';

        // Evaluate each answer against backend RAG endpoint sequentially or in parallel
        for (let i = 0; i < currentQuestions.length; i++) {
            const q = currentQuestions[i];
            const uAns = userAnswers[i];
            
            try {
                const response = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        question: q.question,
                        user_answer: uAns,
                        correct_answer: q.answer,
                        context_text: currentContext
                    })
                });
                
                const data = await response.json();
                
                const isCorrect = data.is_correct;
                if (isCorrect) correctCount++;
                
                resultsHTML += `
                    <div class="result-item ${isCorrect ? 'result-correct' : 'result-wrong'}">
                        <div class="question-text">Q: ${q.question}</div>
                        <div><strong>Your Answer:</strong> ${uAns} - ${isCorrect ? '✅ Correct' : '❌ Wrong'}</div>
                        ${!isCorrect ? `<div><strong>Correct Answer:</strong> ${q.answer}</div>` : ''}
                        ${!isCorrect && data.reasoning ? `<div class="reasoning-box">💡 <strong>AI Reasoning:</strong> ${data.reasoning}</div>` : ''}
                    </div>
                `;
            } catch (err) {
                console.error("Evaluation error:", err);
            }
        }

        // Display results
        scoreContainer.innerHTML = `<h3>You scored ${correctCount} out of ${currentQuestions.length}</h3>`;
        explanationsContainer.innerHTML = resultsHTML;

        switchSection(evaluatingSection, resultsSection);
        
        // Reset button state just in case
        submitBtn.disabled = false;
        submitBtn.innerText = "Submit Answers";
    });

    // Reset workflow
    resetBtn.addEventListener('click', () => {
        pdfInput.value = '';
        fileNameDisplay.textContent = 'Click to choose a PDF file';
        fileNameDisplay.parentElement.classList.remove('has-file');
        
        currentQuestions = [];
        loader.classList.add('hidden');
        generateBtn.classList.remove('hidden');
        
        // Clear radios
        document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);

        switchSection(resultsSection, ingestSection);
    });
});
