import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  SubTitle
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels,
);

function selectColor(number) {
  const hue = number * 137.508; // use golden angle approximation
  return `hsl(${hue},50%,55%)`;
}

const LineChart = ({ data, isGenderChart, title }) => {
  // Extract unique dates
  const colorSet = data.colorSet;
  const rows = data.rows || [];
  const dates = Array.from(new Set(rows.map(item => item.date)));

  // Extract unique labels (either gender or name)
  const labels = Array.from(new Set(rows.map(item => item.gender || item.name)));

  // Map the data to chart datasets
  const chartData = {
    labels: dates,
    datasets: labels.map((label, index) => ({
      label,
      data: dates.map(date => {
        const item = rows.find(d => (d.gender === label || d.name === label) && d.date === date);
        return item ? item.total : 0;
      }),
      fill: false,
      backgroundColor: label === 'Anteil Frauen' ? colorSet.female :  label === 'Anteil Männer' ? colorSet.male : selectColor(index),
      borderColor: label === 'Anteil Frauen' ? colorSet.female :  label === 'Anteil Männer' ? colorSet.male : selectColor(index),
      borderWidth: label === 'Anteil Frauen' ? 2 :  label === 'Anteil Männer' ?  2 : 1, // Increase border width for overall
    })),
  };

  // Configure y-axis options based on whether it's a gender chart or not
  const yScaleOptions = isGenderChart
    ? {
        beginAtZero: true,
        min: 0,
        max: 100,
        ticks: {
          callback: function (value) {
            return value + '%'; // Append % for gender chart
          }
        }
      }
    : {
        beginAtZero: true, // Allow the scale to dynamically adjust based on data
      };

  const options = {
    layout: {
      padding: 50
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          padding: 20
        }
      },
      title: {
        display: true,
        text: title,
        padding: {
            top: 10,
            bottom: 10
        },
        font: {
          size: 24,
        }
      },
      datalabels: {
        anchor: 'end',
        align: 'bottom',
        offset: 5,
        formatter: function (value) {
          return value + (isGenderChart ? "%" : '');
        }
      },
    },
    scales: {
      y: yScaleOptions,
    }
  };

  return <Line data={chartData} options={options} />;
};

export default LineChart;
