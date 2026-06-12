const ctx = document.getElementById('performanceChart');

if (ctx) {

    new Chart(ctx, {
        type: 'bar',

        data: {
            labels: ['Math', 'English', 'Science', 'Kiswahili'],

            datasets: [{
                label: 'Mean Score',

                data: [78, 67, 80, 74],

                borderWidth: 1
            }]
        },

        options: {
            responsive: true
        }
    });

}