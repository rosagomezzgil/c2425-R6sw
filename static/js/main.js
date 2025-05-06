/**
 * Este archivo JavaScript está diseñado para manejar la actualización dinámica de una página web
 * que muestra las predicciones de criptomonedas (específicamente para Bitcoin). Incluye funciones
 * para formatear precios, actualizar elementos de la interfaz de usuario con datos de predicción,
 * mostrar estados de carga, mostrar mensajes de error y gestionar las actualizaciones del gráfico
 * según los rangos de fechas seleccionados. También maneja la realización de llamadas a la API para
 * obtener los datos más recientes de predicción y actualizar dinámicamente el contenido en la página.
 */

// Función para formatear el precio como una cadena de moneda
function formatPrice(price) {
    return '$' + parseFloat(price).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Función para actualizar la interfaz de usuario con los datos de predicción
function updatePredictionUI(data) {
    // Actualizar precios y cambios con valores de precio formateados
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

// Función para mostrar el indicador de carga
function showLoading() {
    const elements = ['current-price', 'price-7d', 'percent-7d', 'price-30d', 'percent-30d'];
    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.dataset.originalText = el.innerText;
            el.innerText = 'Cargando...';
        }
    });
}

// Función para ocultar el indicador de carga
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

// Mostrar mensaje de error
function showErrorMessage(message, container) {
    // Eliminar mensajes de error existentes
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(el => el.remove());

    // Crear y mostrar el nuevo mensaje de error
    const statusEl = document.createElement('div');
    statusEl.className = 'error-message';
    statusEl.innerText = message || 'Error al cargar los datos. Por favor, inténtelo más tarde.';

    const targetContainer = container || document.querySelector('.prediction-container') || document.body;
    targetContainer.appendChild(statusEl);

    // Eliminar el mensaje después de 5 segundos
    setTimeout(() => {
        if (statusEl.parentNode) {
            statusEl.parentNode.removeChild(statusEl);
        }
    }, 5000);
}

// Cargar los datos iniciales
function loadInitialData() {
    // Mostrar indicador de carga
    showLoading();

    fetch('/api/bitcoin/prediction')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading();
            updatePredictionUI(data);
        })
        .catch(error => {
            hideLoading();
            console.error('Error al cargar los datos iniciales:', error);
            showErrorMessage('Error al cargar los datos. Por favor, inténtelo más tarde.');
        });
}

// Realizar la predicción
async function makePrediction() {
    try {
        // Obtener la fecha seleccionada
        const predictionDate = document.getElementById('prediction-date').value;
        const resultContainer = document.getElementById('prediction-result');
        const profitContainer = document.getElementById('prediction-profit');

        if (!predictionDate) {
            resultContainer.innerHTML = '<p class="error">Por favor, seleccione una fecha</p>';
            return;
        }

        // Mostrar estado de carga
        resultContainer.innerHTML = '<p>Calculando predicción...</p>';
        profitContainer.textContent = 'Calculando...';

        // Hacer la solicitud API con la fecha seleccionada
        const response = await fetch(`/api/bitcoin/prediction?prediction_date=${predictionDate}`);

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();

        // Formatear los números para su visualización
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

        // Calcular el porcentaje de ganancia potencial
        const profitPercentage = data.change_30d.toFixed(2);

        // Mostrar los resultados
        resultContainer.innerHTML = `
            <div class="prediction-result-container">
                <p><strong>Precio actual:</strong> ${currentPrice}</p>
                <p><strong>Precio predicho para ${formatDate(predictionDate)}:</strong> ${predictedPrice}</p>
                <p><strong>Cambio esperado:</strong> ${profitPercentage}%</p>
            </div>
        `;

        // Mostrar la información de ganancia con codificación de colores
        const profitClass = data.change_30d >= 0 ? 'positive-change' : 'negative-change';
        profitContainer.textContent = `${profitPercentage}%`;
        profitContainer.className = `profit-amount ${profitClass}`;

    } catch (error) {
        console.error('Error al realizar la predicción:', error);
        document.getElementById('prediction-result').innerHTML =
            `<p class="error">Error al obtener la predicción: ${error.message}</p>`;
        document.getElementById('prediction-profit').textContent = 'Error';
    }
}

// Función auxiliar para formatear la fecha en formato español
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Actualizar el gráfico con un nuevo rango de fechas
function updateChart() {
    // Obtener los elementos del DOM
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const chartIframe = document.querySelector('.graph-iframe');

    // Validar que los elementos existan
    if (!startDateInput || !endDateInput || !chartIframe) {
        console.error('Elementos del gráfico no encontrados');
        showErrorMessage('Error: Elementos del gráfico no encontrados');
        return;
    }

    const startDate = startDateInput.value;
    const endDate = endDateInput.value;

    // Validar las selecciones de fechas
    if (!startDate || !endDate) {
        showErrorMessage('Por favor, seleccione las fechas de inicio y fin');
        return;
    }

    try {
        // Convertir las fechas a objetos Date de JavaScript
        const startDateObj = new Date(startDate);
        const endDateObj = new Date(endDate);

        // Validar el rango de fechas
        if (startDateObj >= endDateObj) {
            showErrorMessage('La fecha de inicio debe ser anterior a la fecha de fin');
            return;
        }

        // Mostrar estado de actualización
        const updateStatus = document.createElement('div');
        updateStatus.className = 'update-status';
        updateStatus.innerText = 'Actualizando gráfico...';

        const container = document.querySelector('.prediction-container') || document.body;
        container.appendChild(updateStatus);

        // Formatear las fechas para la API (formato ISO)
        const formattedStartDate = startDate + 'T00:00:00';
        const formattedEndDate = endDate + 'T23:59:59';

        // Actualizar la URL del iframe
        const baseUrl = chartIframe.src.split('?')[0];
        const newSrc = `${baseUrl}?start=${encodeURIComponent(formattedStartDate)}&end=${encodeURIComponent(formattedEndDate)}&t=${Date.now()}`;
        chartIframe.src = newSrc;

        // Eliminar el estado después de un breve retraso
        setTimeout(() => {
            if (updateStatus.parentNode) {
                updateStatus.parentNode.removeChild(updateStatus);
            }
        }, 2000);
    } catch (error) {
        console.error('Error actualizando el gráfico:', error);
        showErrorMessage('Error actualizando el gráfico: ' + error.message);
    }
}

// Evento cuando el DOM está completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM completamente cargado');

    // Inicializar los inputs de fecha con valores predeterminados (del último mes hasta hoy)
    const today = new Date();
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(today.getMonth() - 1);

    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');

    if (startDateInput && endDateInput) {
        startDateInput.valueAsDate = oneMonthAgo;
        endDateInput.valueAsDate = today;
    }

    // Cargar los datos iniciales de Bitcoin
    loadInitialData();

    // Configurar el evento del botón de predicción
    const predictionBtn = document.getElementById('predict-btn');

    if (predictionBtn) {
        predictionBtn.addEventListener('click', makePrediction);
    } else {
        console.error('Botón del formulario de predicción no encontrado');
    }

    // Configurar el evento del botón para actualizar el gráfico
    const updateChartBtn = document.getElementById('update-chart');

    if (updateChartBtn) {
        updateChartBtn.addEventListener('click', updateChart);
    } else {
        console.error('Botón para actualizar gráfico no encontrado');
    }
});
