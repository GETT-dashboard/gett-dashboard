// components/charts/PieChart.js
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels'; // Import the plugin

// Register the necessary Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, ChartDataLabels);

const PieChart = ({ data }) => {
  const options = {
    layout: {
      padding: 50
    },
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          padding: 20
        }
      },
      title: {
        display: true,
        text: data.labels.length > 0 ? data.datasets[0].label : 'Nutzen Sie "Diagramm aktualisieren" zur Anzeige',
        padding: {
            top: 10,
            bottom: 10
        },
        font: {
          size: 24,
        }
      },
      datalabels: {
        formatter: (value, context) => {
          // Calculate percentage
          const total = context.chart._metasets[0].total;
          const percentage = ((value / total) * 100).toFixed(2);
          return data.labels.length > 0 ? `${percentage}%`: ''; // Display percentage
        },
        color: '#fff', // Set the color of the percentage text
        font: {
          size: 14, // Set font size
          weight: 'bold',
        },
        align: 'center', // Align the text in the center of the slice
      },
    },
  };

  // Default data to show if no data is provided
  const defaultData = {
    labels: ['Nutzen Sie "Diagramm aktualisieren" zur Anzeige'],
    datasets: [
      {
        data: [1],
        backgroundColor: ['rgba(200, 200, 200, 0.5)'],
        borderColor: ['rgba(200, 200, 200, 1)'],
        borderWidth: 1,
      },
    ],
  };

  return <Pie data={data.labels.length > 0 ? data : defaultData} options={options} />;
};

export default PieChart;
