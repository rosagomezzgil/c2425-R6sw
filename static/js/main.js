// Establecer fechas predeterminadas
document.addEventListener('DOMContentLoaded', function() {
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
    document.getElementById('calculate-btn').addEventListener('click', function() {
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

    // Añadir evento para el botón de actualizar
    document.getElementById('update-chart').addEventListener('click', function() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        // Aquí iría la lógica para actualizar el gráfico con las fechas seleccionadas
        console.log(`Actualizando gráfico desde ${startDate} hasta ${endDate}`);
        // En un caso real, aquí actualizarías la URL del iframe o harías una petición AJAX
    });
});