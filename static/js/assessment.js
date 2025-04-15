document.addEventListener('DOMContentLoaded', function() {
    const assessmentForm = document.getElementById('assessment-form');
    const questionGroups = document.querySelectorAll('.question-group');
    const nextButtons = document.querySelectorAll('.btn-next');
    const prevButtons = document.querySelectorAll('.btn-prev');
    const progressBar = document.getElementById('assessment-progress');
    const submitButton = document.getElementById('submit-assessment');
    
    let currentQuestion = 0;
    const totalQuestions = questionGroups.length;
    
    // Initialize - show only first question
    updateVisibleQuestion();
    updateProgressBar();
    
    // Handle next button clicks
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const questionGroup = this.closest('.question-group');
            const questionNumber = parseInt(questionGroup.dataset.question);
            
            // Check if question is answered
            const radioButtons = questionGroup.querySelectorAll('input[type="radio"]');
            let answered = false;
            radioButtons.forEach(radio => {
                if (radio.checked) {
                    answered = true;
                }
            });
            
            if (!answered) {
                showError(questionGroup, "Please select an answer before continuing");
                return;
            }
            
            // Move to next question
            currentQuestion = questionNumber;
            updateVisibleQuestion();
            updateProgressBar();
            scrollToTop();
        });
    });
    
    // Handle previous button clicks
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            currentQuestion--;
            updateVisibleQuestion();
            updateProgressBar();
            scrollToTop();
        });
    });
    
    // Handle radio button selections
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove error message when an option is selected
            const questionGroup = this.closest('.question-group');
            clearError(questionGroup);
            
            // Style the selected option
            const allOptions = questionGroup.querySelectorAll('.rating-option');
            allOptions.forEach(option => {
                option.classList.remove('selected');
            });
            
            const selectedOption = this.closest('.rating-option');
            if (selectedOption) {
                selectedOption.classList.add('selected');
            }
            
            // Auto-advance to next question after selection (except on last question)
            const questionNumber = parseInt(questionGroup.dataset.question);
            if (questionNumber < totalQuestions - 1) {
                setTimeout(() => {
                    currentQuestion = questionNumber;
                    updateVisibleQuestion();
                    updateProgressBar();
                    scrollToTop();
                }, 500);
            }
        });
    });
    
    // Form submission validation
    assessmentForm.addEventListener('submit', function(e) {
        // Check if all questions are answered
        let allAnswered = true;
        
        questionGroups.forEach(group => {
            const radioButtons = group.querySelectorAll('input[type="radio"]');
            let answered = false;
            radioButtons.forEach(radio => {
                if (radio.checked) {
                    answered = true;
                }
            });
            
            if (!answered) {
                allAnswered = false;
                showError(group, "Please select an answer for this question");
            }
        });
        
        if (!allAnswered) {
            e.preventDefault();
            alert("Please answer all questions before submitting.");
            
            // Show the first unanswered question
            for (let i = 0; i < questionGroups.length; i++) {
                const group = questionGroups[i];
                const radioButtons = group.querySelectorAll('input[type="radio"]');
                let answered = false;
                
                radioButtons.forEach(radio => {
                    if (radio.checked) {
                        answered = true;
                    }
                });
                
                if (!answered) {
                    currentQuestion = i;
                    updateVisibleQuestion();
                    updateProgressBar();
                    scrollToTop();
                    break;
                }
            }
        }
    });
    
    // Helper functions
    function updateVisibleQuestion() {
        questionGroups.forEach((group, index) => {
            if (index === currentQuestion) {
                group.classList.add('active');
            } else {
                group.classList.remove('active');
            }
        });
        
        // Show/hide prev button on first question
        const firstPrevButton = document.querySelector('.btn-prev');
        if (currentQuestion === 0) {
            firstPrevButton.style.visibility = 'hidden';
        } else {
            firstPrevButton.style.visibility = 'visible';
        }
        
        // Show/hide next button on last question
        const lastNextButton = questionGroups[totalQuestions - 1].querySelector('.btn-next');
        if (currentQuestion === totalQuestions - 1) {
            submitButton.style.display = 'block';
            lastNextButton.style.display = 'none';
        } else {
            submitButton.style.display = 'none';
            lastNextButton.style.display = 'block';
        }
    }
    
    function updateProgressBar() {
        const progress = ((currentQuestion + 1) / totalQuestions) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        
        // Update progress text
        const progressText = document.getElementById('progress-text');
        if (progressText) {
            progressText.textContent = `Question ${currentQuestion + 1} of ${totalQuestions}`;
        }
    }
    
    function showError(questionGroup, message) {
        clearError(questionGroup);
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'alert alert-danger error-message mt-2';
        errorMessage.textContent = message;
        
        questionGroup.appendChild(errorMessage);
        
        // Highlight options
        const options = questionGroup.querySelectorAll('.rating-option');
        options.forEach(option => {
            option.classList.add('error');
        });
    }
    
    function clearError(questionGroup) {
        const errorMessage = questionGroup.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
        
        // Remove error highlighting
        const options = questionGroup.querySelectorAll('.rating-option');
        options.forEach(option => {
            option.classList.remove('error');
        });
    }
    
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
});
