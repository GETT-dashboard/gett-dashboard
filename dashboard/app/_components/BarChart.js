import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, Tooltip, Legend, CategoryScale, LinearScale, Title } from 'chart.js';
import adaptToGerman from '@/util/translate-labels';

ChartJS.register(BarElement, Tooltip, Legend, CategoryScale, LinearScale, Title);

const BarChart = ({ data, categories }) => {
    const rows = data.rows || [];
    const colorSet = data.colorSet;
    const options = {
        indexAxis: 'x', // Set to 'x' for vertical bars
        elements: {
            bar: {
                borderWidth: 2,
            },
        },
        parsing: {
            xAxisKey: 'value',
        },
        responsive: true,
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
                text: 'Geschlechterverteilung nach Ressort',
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
                return `${(value * 1).toFixed(0)}%`; // Display percentage
              },
              color: '#fff', // Set the color of the percentage text
              font: {
                weight: 'bold',
              },
              align: 'center', // Align the text in the center of the slice
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                min: 0,
                max: 100, // Y-axis ranges from 0 to 100%
                ticks: {
                    callback: function(value) {
                        return value + '%'; // Append % to y-axis labels
                    }
                }
            }
        }
    };

    const sortedCategoriesByRow = rows.filter(row => row.gender == 'MALE')
        .map(row => categories.filter(category => row.categoryId == category.value)[0])
    // Prepare datasets for MALE, FEMALE, DIVERS
    const datasets = ['FEMALE', 'MALE'].map((gender, index) => {
        return {
            label: adaptToGerman(gender),
            data: sortedCategoriesByRow.map(category => {
                const item = rows.find(item => item.categoryId == category.value && item.gender === gender);
                console.log(item);
                return item ? item.percentage : 0;
            }),
            backgroundColor: [
                colorSet.female, //'rgba(242, 154, 89, 1)',   // #F29A59 
                colorSet.male, //'rgba(15, 32, 58, 1)',   // #0F203  
            ][index],
            borderColor: [
                colorSet.female, //'rgba(242, 154, 89, 1)',   // #F29A59 
                colorSet.male, //'rgba(15, 32, 58, 1)',   // #0F203  
            ][index],
            borderWidth: 1,
        };
    });

    const formattedData = {
        labels: sortedCategoriesByRow.map(category => category.display),
        datasets: datasets,
    };

    return <Bar data={formattedData} options={options} />;
};

export default BarChart;
