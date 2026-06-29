const categoryChart = document.getElementById("categoryChart");

new Chart(categoryChart, {
  type: "doughnut",

  data: {
    labels: ["Programming", "Science", "Novel", "History", "Others"],

    datasets: [
      {
        label: "Books",
        data: [25, 18, 30, 12, 15],
        backgroundColor: [
          "#3B82F6",
          "#10B981",
          "#F59E0B",
          "#EF4444",
          "#8B5CF6",
        ],
      },
    ],
  },

  options: {
    responsive: true,

    plugins: {
      legend: {
        position: "right",
        boxWidth: 15,
        boxHeight: 15,
        padding: 15,
        labels: {
          font: {
            size: 13,
          },
          color: "#475569",
        },
      },
    },
    maintainAspectRatio: false,
    cutout: "60%",
  },
});
