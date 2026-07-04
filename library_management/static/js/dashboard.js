const labels = JSON.parse(
    document.getElementById("chart-labels").textContent
);

const counts = JSON.parse(
    document.getElementById("chart-counts").textContent
);

const categoryChart = document.getElementById("categoryChart");

new Chart(categoryChart, {
    type: "doughnut",

    data: {
        labels: labels,

        datasets: [{
            label: "Books",
            data: counts,
            backgroundColor: [
                "#3B82F6",
                "#10B981",
                "#F59E0B",
                "#EF4444",
                "#8B5CF6",
                "#EC4899",
                "#14B8A6"
            ],
        }],
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "right",
            },
        },
        cutout: "60%",
    },
});