document.addEventListener('DOMContentLoaded', function() {
    // Check if charts data is available
    if (typeof assessmentDates !== 'undefined' && typeof assessmentScores !== 'undefined') {
        renderAssessmentChart();
    }
    
    if (typeof emotionData !== 'undefined') {
        renderEmotionChart();
    }
    
    // Function to render assessment score chart
    function renderAssessmentChart() {
        const ctx = document.getElementById('assessment-chart').getContext('2d');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: assessmentDates,
                datasets: [{
                    label: 'Mental Health Score',
                    data: assessmentScores,
                    borderColor: '#5b6ef5',
                    backgroundColor: 'rgba(91, 110, 245, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#5b6ef5',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        },
                        title: {
                            display: true,
                            text: 'Score (0-100)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.parsed.y.toFixed(1)}`;
                            }
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    // Function to render emotion chart
    function renderEmotionChart() {
        const ctx = document.getElementById('emotion-chart').getContext('2d');
        
        // Process emotion data for chart
        const emotionColors = {
            'happy': 'rgba(75, 192, 192, 0.7)',
            'sad': 'rgba(54, 162, 235, 0.7)',
            'angry': 'rgba(255, 99, 132, 0.7)',
            'anxious': 'rgba(255, 159, 64, 0.7)',
            'stressed': 'rgba(153, 102, 255, 0.7)',
            'depressed': 'rgba(201, 203, 207, 0.7)',
            'fearful': 'rgba(255, 205, 86, 0.7)',
            'calm': 'rgba(75, 192, 150, 0.7)',
            'hopeful': 'rgba(120, 192, 75, 0.7)',
            'neutral': 'rgba(150, 150, 150, 0.7)'
        };
        
        // Get unique dates and emotions
        const dates = Object.keys(emotionData).sort();
        const allEmotions = new Set();
        
        // Collect all emotions
        for (const date in emotionData) {
            Object.keys(emotionData[date]).forEach(emotion => allEmotions.add(emotion));
        }
        
        // Create datasets
        const datasets = [];
        allEmotions.forEach(emotion => {
            const data = dates.map(date => emotionData[date][emotion] || 0);
            
            datasets.push({
                label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
                data: data,
                backgroundColor: emotionColors[emotion] || 'rgba(150, 150, 150, 0.7)',
                borderColor: emotionColors[emotion] ? emotionColors[emotion].replace('0.7', '1') : 'rgba(150, 150, 150, 1)',
                borderWidth: 1
            });
        });
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Emotional Intensity'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}`;
                            }
                        }
                    },
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }
    
    // Load assessment details when clicking on an assessment
    const assessmentItems = document.querySelectorAll('.assessment-item');
    assessmentItems.forEach(item => {
        item.addEventListener('click', function() {
            const assessmentId = this.dataset.id;
            
            // Toggle active class
            assessmentItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Load assessment details
            fetch(`/api/assessment_history`)
                .then(response => response.json())
                .then(data => {
                    const assessment = data.find(a => a.id == assessmentId);
                    if (assessment) {
                        displayAssessmentDetails(assessment);
                    }
                })
                .catch(error => {
                    console.error('Error loading assessment details:', error);
                });
        });
    });
    
    // Function to display assessment details
    function displayAssessmentDetails(assessment) {
        const detailsContainer = document.getElementById('assessment-details');
        
        // Format the date
        const date = new Date(assessment.date);
        const formattedDate = date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        // Get question text for each answer
        const questions = [
            "How would you rate your overall mood today?",
            "How would you rate your anxiety levels today?",
            "How would you rate your ability to cope with stress today?",
            "How would you rate your energy levels today?",
            "How would you rate your sleep quality last night?",
            "How would you rate your social connections today?",
            "How would you rate your overall sense of well-being today?"
        ];
        
        // Create HTML for answers
        let answersHtml = '';
        for (let i = 1; i <= 7; i++) {
            const questionKey = `q${i}`;
            const answer = assessment.answers[questionKey];
            const question = questions[i-1];
            
            answersHtml += `
                <div class="assessment-question">
                    <p><strong>Q${i}:</strong> ${question}</p>
                    <div class="answer-scale">
                        <span class="scale-label">Poor</span>
                        ${renderScalePoints(answer, 5)}
                        <span class="scale-label">Excellent</span>
                    </div>
                </div>
            `;
        }
        
        // Update the details container
        detailsContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5>${formattedDate}</h5>
                    <div class="overall-score">
                        Overall Score: <span class="badge bg-primary">${assessment.score.toFixed(1)}/100</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="assessment-answers">
                        ${answersHtml}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Helper function to render scale points
    function renderScalePoints(selected, max) {
        let html = '';
        for (let i = 1; i <= max; i++) {
            const activeClass = i <= selected ? 'active' : '';
            html += `<span class="scale-point ${activeClass}">${i}</span>`;
        }
        return html;
    }
});
