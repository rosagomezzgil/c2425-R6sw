// Establecer fechas predeterminadas
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(today.getMonth() - 1);

    document.getElementById('start-date').valueAsDate = oneMonthAgo;
    document.getElementById('end-date').valueAsDate = today;

    // Añadir evento para el botón de actualizar
    document.getElementById('update-chart').addEventListener('click', function() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        // Aquí iría la lógica para actualizar el gráfico con las fechas seleccionadas
        console.log(`Actualizando gráfico desde ${startDate} hasta ${endDate}`);
        // En un caso real, aquí actualizarías la URL del iframe o harías una petición AJAX
    });
});