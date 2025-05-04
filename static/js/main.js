// Function to format price
function formatPrice(price) {
    return '$' + parseFloat(price).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Function to update the UI with data
function updatePredictionUI(data) {
    // Update prices and changes
    document.getElementById('current-price').innerText = formatPrice(data.current_price);

    document.getElementById('price-7d').innerText = formatPrice(data.price_7d);
    document.getElementById('percent-7d').innerText = (data.change_7d > 0 ? '+' : '') + data.change_7d.toFixed(2) + '%';
    document.getElementById('change-7d').className = data.change_7d >= 0 ? 'positive-change' : 'negative-change';
    document.getElementById('arrow-7d').innerText = data.change_7d >= 0 ? '↑' : '↓';

    document.getElementById('price-30d').innerText = formatPrice(data.price_30d);
    document.getElementById('percent-30d').innerText = (data.change_30d > 0 ? '+' : '') + data.change_30d.toFixed(2) + '%';
    document.getElementById('change-30d').className = data.change_30d >= 0 ? 'positive-change' : 'negative-change';
    document.getElementById('arrow-30d').innerText = data.change_30d >= 0 ? '↑' : '↓';
}

// Function to show loading indicator
function showLoading() {
    const elements = ['current-price', 'price-7d', 'percent-7d', 'price-30d', 'percent-30d'];
    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.dataset.originalText = el.innerText;
            el.innerText = 'Loading...';
        }
    });
}

// Function to hide loading indicator
function hideLoading() {
    const elements = ['current-price', 'price-7d', 'percent-7d', 'price-30d', 'percent-30d'];
    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el && el.dataset.originalText) {
            el.innerText = el.dataset.originalText;
            delete el.dataset.originalText;
        }
    });
}

// Display error message
function showErrorMessage(message, container) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(el => el.remove());

    // Create and show new error message
    const statusEl = document.createElement('div');
    statusEl.className = 'error-message';
    statusEl.innerText = message || 'Error loading data. Please try again later.';

    const targetContainer = container || document.querySelector('.prediction-container') || document.body;
    targetContainer.appendChild(statusEl);

    // Remove message after 5 seconds
    setTimeout(() => {
        if (statusEl.parentNode) {
            statusEl.parentNode.removeChild(statusEl);
        }
    }, 5000);
}

// Load initial data
function loadInitialData() {
    // Show loading indicator
    showLoading();

    fetch('/api/bitcoin/current')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            updatePredictionUI(data);
        })
        .catch(error => {
            hideLoading();
            console.error('Error loading initial data:', error);
            showErrorMessage('Error loading data. Please try again later.');
        });
}

// Make prediction
async function makePrediction() {
    try {
        // Get the selected date
        const predictionDate = document.getElementById('prediction-date').value;
        const resultContainer = document.getElementById('prediction-result');
        const profitContainer = document.getElementById('prediction-profit');

        if (!predictionDate) {
            resultContainer.innerHTML = '<p class="error">Por favor, seleccione una fecha</p>';
            return;
        }

        // Show loading state
        resultContainer.innerHTML = '<p>Calculando predicción...</p>';
        profitContainer.textContent = 'Calculando...';

        // Make API request with the selected date
        const response = await fetch(`/api/bitcoin/prediction?prediction_date=${predictionDate}`);

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();

        // Format numbers for display
        const currentPrice = new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(data.current_price);

        const predictedPrice = new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(data.price_30d);

        // Calculate potential profit percentage
        const profitPercentage = data.change_30d.toFixed(2);

        // Display results
        resultContainer.innerHTML = `
            <div class="prediction-result-container">
                <p><strong>Precio actual:</strong> ${currentPrice}</p>
                <p><strong>Precio predicho para ${formatDate(predictionDate)}:</strong> ${predictedPrice}</p>
                <p><strong>Cambio esperado:</strong> ${profitPercentage}%</p>
            </div>
        `;

        // Display profit information with color coding
        const profitClass = data.change_30d >= 0 ? 'positive-profit' : 'negative-profit';
        profitContainer.textContent = `${profitPercentage}%`;
        profitContainer.className = `profit-amount ${profitClass}`;

    } catch (error) {
        console.error('Error making prediction:', error);
        document.getElementById('prediction-result').innerHTML =
            `<p class="error">Error al obtener la predicción: ${error.message}</p>`;
        document.getElementById('prediction-profit').textContent = 'Error';
    }
}

// Helper function to format date in Spanish format
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Update chart with new date range
function updateChart() {
    // Get DOM elements
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const chartIframe = document.querySelector('.graph-iframe');

    // Validate elements exist
    if (!startDateInput || !endDateInput || !chartIframe) {
        console.error('Required chart elements not found');
        showErrorMessage('Error: Chart elements not found');
        return;
    }

    const startDate = startDateInput.value;
    const endDate = endDateInput.value;

    // Validate date selections
    if (!startDate || !endDate) {
        showErrorMessage('Please select start and end dates');
        return;
    }

    try {
        // Convert dates to JavaScript Date objects
        const startDateObj = new Date(startDate);
        const endDateObj = new Date(endDate);

        // Validate date range
        if (startDateObj >= endDateObj) {
            showErrorMessage('Start date must be before end date');
            return;
        }

        // Show updating status
        const updateStatus = document.createElement('div');
        updateStatus.className = 'update-status';
        updateStatus.innerText = 'Updating chart...';

        const container = document.querySelector('.prediction-container') || document.body;
        container.appendChild(updateStatus);

        // Format dates for API (ISO format)
        const formattedStartDate = startDate + 'T00:00:00';
        const formattedEndDate = endDate + 'T23:59:59';

        // Update iframe URL
        const baseUrl = chartIframe.src.split('?')[0];
        const newSrc = `${baseUrl}?start=${encodeURIComponent(formattedStartDate)}&end=${encodeURIComponent(formattedEndDate)}&t=${Date.now()}`;
        chartIframe.src = newSrc;

        // Remove status after a short delay
        setTimeout(() => {
            if (updateStatus.parentNode) {
                updateStatus.parentNode.removeChild(updateStatus);
            }
        }, 2000);
    } catch (error) {
        console.error('Error updating chart:', error);
        showErrorMessage('Error updating chart: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');

    // Initialize date inputs with default values (last month to today)
    const today = new Date();
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(today.getMonth() - 1);

    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');

    if (startDateInput && endDateInput) {
        startDateInput.valueAsDate = oneMonthAgo;
        endDateInput.valueAsDate = today;
    }

    // Load initial bitcoin data
    loadInitialData();

    // Set up prediction form button event listener
    const predictionBtn = document.getElementById('predict-btn');

    if (predictionBtn) {
        predictionBtn.addEventListener('click', makePrediction);
    } else {
        console.error('Prediction form button not found');
    }

    // Set up update chart button event listener
    const updateChartBtn = document.getElementById('update-chart');

    if (updateChartBtn) {
        updateChartBtn.addEventListener('click', updateChart);
    } else {
        console.error('Update chart button not found');
    }
});