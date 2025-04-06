document.addEventListener('DOMContentLoaded', function() {
    // File upload display
    const fileInput = document.getElementById('resume');
    const fileNameDisplay = document.getElementById('file-name');
    
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = 'Choose file';
            }
        });
    }
    
    // Score circle animation
    const scoreCircle = document.querySelector('.score-circle');
    if (scoreCircle) {
        const score = parseFloat(scoreCircle.getAttribute('data-score'));
        let color;
        
        if (score >= 80) {
            color = '#2ecc71'; // Green for high scores
        } else if (score >= 60) {
            color = '#3498db'; // Blue for medium scores
        } else if (score >= 40) {
            color = '#f39c12'; // Orange for low-medium scores
        } else {
            color = '#e74c3c'; // Red for low scores
        }
        
        // Update score circle and gauge with the appropriate color
        scoreCircle.style.boxShadow = `inset 0 0 0 10px ${color}`;
        document.querySelector('.score-value').style.color = color;
        document.querySelector('.gauge-fill').style.backgroundColor = color;
        
        // Animate the gauge fill
        setTimeout(() => {
            document.querySelector('.gauge-fill').style.width = `${score}%`;
        }, 200);
    }
    
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    if (messages.length > 0) {
        setTimeout(() => {
            messages.forEach(message => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 500);
            });
        }, 5000);
    }
});