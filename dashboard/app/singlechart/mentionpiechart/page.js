'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import PieChart from '../../_components/PieChart';
import { genderMentionOverall } from '../../lib/data';

const SinglePieChart = () => {
    const searchParams = useSearchParams();
    const publisher = searchParams.get('publisher');

    const [mentionPieChartData, setMentionPieChartData] = useState({
        labels: [],
        datasets: [
            {
                label: 'Ratio of Mentions of different genders',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1,
            },
        ],
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                const rows = await genderMentionOverall(new Date('2023-03-01'), new Date('2023-04-01'), publisher, 'Sport');
                setMentionPieChartData({
                    labels: rows.map((row) => row.gender),
                    datasets: [
                        {
                            label: 'Ratio of Mentions of different genders',
                            data: rows.map((row) => row.total),
                            backgroundColor: [
                                'rgba(200, 200, 200, 0.5)',
                                'rgba(255, 99, 132, 0.2)',
                                'rgba(54, 162, 235, 0.2)',
                            ],
                            borderColor: [
                                'rgba(200, 200, 200, 0.5)',
                                'rgba(255, 99, 132, 1)',
                                'rgba(54, 162, 235, 1)',
                            ],
                            borderWidth: 1,
                        },
                    ],
                });
            } catch (error) {
                console.error('Error fetching pie chart data:', error);
            }
        };

        fetchData();
    }, [publisher]);  // Runs again if 'publisher' changes

    return (
        <div>
            <h1>Pie Chart</h1>
            <PieChart data={mentionPieChartData} />
        </div>
    );
};

export default function SinglePieChartPage() {
    return (
        <div>
            <h1>Single Mention Pie Chart</h1>
            <Suspense fallback={<div>Loading Pie Chart...</div>}>
                <SinglePieChart />
            </Suspense>
        </div>
    );
}
