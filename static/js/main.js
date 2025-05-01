// Establecer fechas predeterminadas
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM completamente cargado'); // Log para verificar carga del DOM

    const today = new Date();
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(today.getMonth() - 1);

    document.getElementById('start-date').valueAsDate = oneMonthAgo;
    document.getElementById('end-date').valueAsDate = today;

    // Función para formatear precio
    function formatPrice(price) {
        return '$' + parseFloat(price).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Función para actualizar la UI con los datos
    function updatePredictionUI(data) {
        // Actualizar precios y cambios
        document.getElementById('current-price').innerText = formatPrice(data.current_price);

        document.getElementById('price-7d').innerText = formatPrice(data.price_7d);
        document.getElementById('percent-7d').innerText = (data.change_7d > 0 ? '+' : '') + data.change_7d.toFixed(2) + '%';
        document.getElementById('change-7d').className = data.change_7d >= 0 ? 'data-change positive' : 'data-change negative';
        document.getElementById('arrow-7d').innerText = data.change_7d >= 0 ? '↑' : '↓';

        document.getElementById('price-30d').innerText = formatPrice(data.price_30d);
        document.getElementById('percent-30d').innerText = (data.change_30d > 0 ? '+' : '') + data.change_30d.toFixed(2) + '%';
        document.getElementById('change-30d').className = data.change_30d >= 0 ? 'data-change positive' : 'data-change negative';
        document.getElementById('arrow-30d').innerText = data.change_30d >= 0 ? '↑' : '↓';
    }

    // Cargar datos iniciales
    fetch('/api/bitcoin/current')
        .then(response => response.json())
        .then(data => {
            updatePredictionUI(data);
        })
        .catch(error => {
            console.error('Error cargando datos iniciales:', error);
        });

    // Manejar el cálculo de inversión
    const calculateBtn = document.getElementById('calculate-btn');
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function() {
            const amount = parseFloat(document.getElementById('investment-amount').value);

            if (!amount || isNaN(amount) || amount <= 0) {
                alert('Por favor, ingrese una cantidad válida para invertir');
                return;
            }

            // Enviar datos al backend
            fetch('/api/bitcoin/investment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ investment_amount: amount })
            })
            .then(response => response.json())
            .then(data => {
                // Actualizar predicciones
                updatePredictionUI(data);

                // Mostrar potenciales ganancias
                const currentProfit = document.getElementById('current-profit');
                const profit7d = document.getElementById('profit-7d');
                const profit30d = document.getElementById('profit-30d');

                // Actual (sin cambio)
                currentProfit.innerText = `Tu inversión: ${formatPrice(amount)}`;
                currentProfit.className = 'profit-amount';

                // 7 días
                const profit7dValue = amount * (1 + data.change_7d / 100) - amount;
                profit7d.innerText = `${profit7dValue >= 0 ? '+' : ''}${formatPrice(profit7dValue)}`;
                profit7d.className = 'profit-amount ' + (profit7dValue >= 0 ? 'profit-positive' : 'profit-negative');

                // 30 días
                const profit30dValue = amount * (1 + data.change_30d / 100) - amount;
                profit30d.innerText = `${profit30dValue >= 0 ? '+' : ''}${formatPrice(profit30dValue)}`;
                profit30d.className = 'profit-amount ' + (profit30dValue >= 0 ? 'profit-positive' : 'profit-negative');
            })
            .catch(error => {
                console.error('Error calculando inversión:', error);
                alert('Error al procesar su solicitud');
            });
        });
    } else {
        console.error('Elemento #calculate-btn no encontrado');
    }

    // Referencia al botón actualizar y verificamos que exista
    const updateChartBtn = document.getElementById('update-chart');

    if (updateChartBtn) {
        console.log('Botón update-chart encontrado, añadiendo event listener');

        // Añadir evento para el botón de actualizar
        updateChartBtn.addEventListener('click', function() {
            console.log('Botón update-chart clickeado');

            // Obtenemos los elementos del DOM
            const startDateInput = document.getElementById('start-date');
            const endDateInput = document.getElementById('end-date');

            if (!startDateInput || !endDateInput) {
                console.error('Elementos de fecha no encontrados');
                return;
            }

            const startDate = startDateInput.value;
            const endDate = endDateInput.value;

            console.log('Fechas obtenidas:', { startDate, endDate });

            // Validar que ambas fechas estén seleccionadas
            if (!startDate || !endDate) {
                alert('Por favor, selecciona fechas de inicio y fin');
                return;
            }

            try {
                // Convertir fechas a objetos Date de JavaScript
                const startDateObj = new Date(startDate);
                const endDateObj = new Date(endDate);

                console.log('Fechas convertidas:', {
                    startDateObj: startDateObj.toISOString(),
                    endDateObj: endDateObj.toISOString()
                });

                // Validar que la fecha de inicio es anterior a la fecha de fin
                if (startDateObj >= endDateObj) {
                    alert('La fecha de inicio debe ser anterior a la fecha de fin');
                    return;
                }

                // Formatear las fechas para que funcionen con fromisoformat() en Python
                const formattedStartDate = startDate + 'T00:00:00';
                const formattedEndDate = endDate + 'T23:59:59';

                console.log('Fechas formateadas:', { formattedStartDate, formattedEndDate });

                // Buscar el iframe de la gráfica
                const chartIframe = document.querySelector('.graph-iframe');

                if (!chartIframe) {
                    console.error('Iframe de gráfica no encontrado');
                    alert('Error: No se encontró el elemento de la gráfica');
                    return;
                }

                const currentSrc = chartIframe.src;
                console.log('URL actual del iframe:', currentSrc);

                // Remover parámetros anteriores si existen y crear nueva URL
                let newSrc = currentSrc.split('?')[0];
                newSrc += `?start=${encodeURIComponent(formattedStartDate)}&end=${encodeURIComponent(formattedEndDate)}&t=${Date.now()`;

                console.log('Nueva URL del iframe:', newSrc);

                // Actualizar la URL del iframe
                chartIframe.src = newSrc;
                console.log('URL del iframe actualizada');

                // Mostrar un feedback visual al usuario
                alert('Actualizando gráfico...');
            } catch (error) {
                console.error('Error al actualizar la gráfica:', error);
                alert('Error al actualizar la gráfica: ' + error.message);
            }
        });
    } else {
        console.error('Elemento #update-chart no encontrado');
    }
});