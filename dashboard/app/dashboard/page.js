'use client'
// pages/dashboard.js
import React, { useEffect, useState, useRef } from 'react';
import DateRangePicker from '../_components/DateRangePicker';
import PieChart from '../_components/PieChart';
import { genderMentionByMonth, genderMentionOverall, singlePersonMentionByMonth, genderMentionByCategory, genderQuoteOverall, fetchCategoryList, fetchPersonList, fetchPublisherList, totalNumberOfArticles, fetchRegexList } from '../lib/data';
import createDescription from '../../util/description';
import LineChart from '../_components/LineChart';
import BarChart from '../_components/BarChart';
import SelectDropdown from '../_components/SelectDropdown';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import { useRouter } from 'next/navigation';
import CircularProgress from '@mui/material/CircularProgress';
import html2canvas from 'html2canvas';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowsRotate, faChartSimple, faChessKing, faChessQueen, faClipboard, faDownload, faList } from '@fortawesome/free-solid-svg-icons';
import highlevelpositions from '../../util/highlevelpositions'
import adaptToGerman from '@/util/translate-labels';
import ColorHints from '../_components/ColorHints';

import { useSearchParams } from 'next/navigation';
import Image from 'next/image';

const Dashboard = () => {
    const searchParams = useSearchParams();
    const [successfulLogin, setSuccessfulLogin] = useState(false);
    const [isCheckingSession, setIsCheckingSession] = useState(false);

    useEffect(() => {
        setSuccessfulLogin(searchParams.get('successfulLogin') === 'true');
    }, [searchParams]);


    const colors = {
        default: {
            male: "rgba(15, 32, 58, 1)",
            female: "rgba(242, 154, 89, 1)",
            title: "Anteil Frauen"
        },
        categorySelected: {
            male: "rgba(15, 32, 58, 1)",
            female: "rgba(235, 235, 96, 1)",
            title: "Anteil Frauen in Ressort"
        },
        highLevelPositionsSelected: {
            male: "rgba(15, 32, 58, 1)",
            female: "rgba(154, 115,	184, 1)",
            title: "Anteil Frauen mit Spitzenposition"
        },
    };
    let date = new Date();

    // Subtract 6 months from the current month
    date.setMonth(date.getMonth() - 7);

    // Set the date to the first day of that month
    date.setDate(1);
    const [startDate, setStartDate] = useState(new Date(date.toISOString().slice(0, 10)));
    date.setMonth(date.getMonth() + 6) ;
    date.setDate(date.getDate() - 1);
    const [endDate, setEndDate] = useState(new Date(date.toISOString().slice(0, 10)));
    const [mentionPieChartData, setMentionPieChartData] = useState({
        labels: [],
        datasets: [
            {
                label: 'Anteil an namentlich genannten Personen',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1,
            },
        ],
    });
    const [quotePieChartData, setQuotePieChartData] = useState({
        labels: [],
        datasets: [
            {
                label: 'Anteil an direkten Zitaten von Frauen und Männern',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1,
            },
        ],
    });
    const [stereotypePieChartData, setStereotypePieChartData] = useState([{
        labels: [],
        datasets: [
            {
                label: 'Ratio of Stereotypes by different genders',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1,
            },
        ],
    }, {
        labels: [],
        datasets: [
            {
                label: 'Ratio of Stereotypes by different genders',
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1,
            },
        ],
    }]);
    const [genderLineChartData, setGenderLineChartData] = useState({ rows: [], colorSet: colors.default });
    const [personLineChartData, setPersonLineChartData] = useState([]);
    const [genderCategoryBarChartData, setGenderCategoryBarChartData] = useState({ rows: [], colorSet: colors.default });
    const [selectedChart, setSelectedChart] = useState('mentionPieChart');
    const [selectedStereotype, setSelectedStereotype] = useState({ id: null, stereoTypeComparison: '' });
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [selectedHighLevelPosition, setSelectedHighLevelPosition] = useState('');
    const [selectedPeople, setSelectedPeople] = useState([]);
    const [selectedPublisher, setSelectedPublisher] = useState('');
    const [stereotypes, setStereotypes] = useState([]);
    const [categories, setCategories] = useState([]);
    const [peoples, setPeoples] = useState([]);
    const [publishers, setPublishers] = useState([]);
    const [description, setDescription] = useState('');

    const [user, setUser] = useState(null);

    const [isFetchingData, setIsFetchingData] = useState(false);
    const [fetchedDataForChart, setFetchedDataForChart] = useState(false);

    const fetchTimer = useRef(null);

    const checkSession = async () => {
        console.log('checkSession');
        try {
            const response = await fetch('/api/login', {
                method: 'GET',
                credentials: 'include',
            });
            if (response.ok) {
                setSuccessfulLogin(true);
            }
        } catch (error) {
        } finally {
            setIsCheckingSession(false);
        }
    };

    useEffect(() => {

        loadCategories(setCategories, setSelectedCategory);
        // checkSession();
    }, []);

    useEffect(() => {

        setFetchedDataForChart(false);

        setSelectedCategory('');
        setSelectedHighLevelPosition('');

    }, [selectedChart]);

    useEffect(() => {
        // Clear previous timer if a new change happens
        if (fetchTimer.current) {
            clearTimeout(fetchTimer.current);
        }

        // Set a new timer to fetch data after 3 seconds of inactivity
        fetchTimer.current = setTimeout(() => {
            fetchData();
        }, 500);

        // Cleanup timer when component unmounts
        return () => {
            clearTimeout(fetchTimer.current);
        };
    }, [selectedChart, startDate, endDate, selectedStereotype, selectedCategory, selectedHighLevelPosition, selectedPeople, selectedPublisher, ]);

    const loadCategories = async (setCategories, setSelectedCategory) => {
        const fetchedCategories = await fetchCategoryList();
        const CategoryNames = fetchedCategories.map((item) => {
            return {
                value: item.id,
                display: item.name
            };
        });
        setCategories([{
            value: '',
            display: 'Alle'
        }, ...CategoryNames]);
        setSelectedCategory('');
    };
    

    const getCategoryNameById = (id) =>{
        if(!id) return '';
        const filteredById = categories.filter(c => c.value == id);
        if (filteredById.length == 1){
            return filteredById[0].display;
        } else{
            return "unbekanntes Ressort";
        }
    }

    const loadPublishers = async (setPublishers, setSelectedPublisher, user) => {
        const fetchedPublishers = await fetchPublisherList(user);
        const publisherNames = fetchedPublishers.map((item) => {
            return {
                value: item.id,
                display: item.name
            };
        });
        setPublishers([{
            value: '',
            display: 'Alle'
        }, ...publisherNames]);
        setSelectedPublisher('');
    }

    const getPublisherNameById = (id) =>{
        if(!id) return '';
        const filteredById = publishers.filter(c => c.value == id);
        if (filteredById.length == 1){
            return filteredById[0].display;
        } else{
            return "unbekanntes Ressort";
        }
    }


    const fetchData = async () => {
        if(selectedChart == 'personLineChart' && selectedPeople.length == 0){
            setFetchedDataForChart(false);
            return;
        }
        setIsFetchingData(true);
        try {
            if (selectedChart === 'mentionPieChart') {
                const rows = await genderMentionOverall(startDate, endDate, selectedPublisher, selectedCategory, selectedHighLevelPosition);
                const description = createDescription(startDate, endDate, rows, selectedChart, getPublisherNameById(selectedPublisher), getCategoryNameById(selectedCategory), selectedHighLevelPosition);
                setDescription(description);

                const usedColorSet = getInUseColorSet();
                setMentionPieChartData({
                    labels: rows.map((row) => adaptToGerman(row.gender)),
                    datasets: [
                        {
                            label: 'Anteil namentlich genannter Personen',
                            data: rows.map((row) => row.total),
                            backgroundColor: [
                                usedColorSet.female, //'rgba(242, 154, 89, 1)',   // #F29A59 (female) with transparency
                                usedColorSet.male //'rgba(15, 32, 58, 1)',     // #0F203A (male) with transparency
                            ],
                            borderColor: [
                                usedColorSet.female, //'rgba(242, 154, 89, 1)',   // #F29A59 (female) with transparency
                                usedColorSet.male//'rgba(15, 32, 58, 1)',     // #0F203A (male) with transparency
                            ],
                            borderWidth: 1,
                        },
                    ],
                });
            } else if (selectedChart === 'quotePieChart') {
                const rows = await genderQuoteOverall(startDate, endDate, selectedPublisher, selectedCategory, selectedHighLevelPosition);
                const description = createDescription(startDate, endDate, rows, selectedChart, getPublisherNameById(selectedPublisher), getCategoryNameById(selectedCategory), selectedHighLevelPosition);
                setDescription(description);
                const usedColorSet = getInUseColorSet();
                setQuotePieChartData({
                    labels: rows.map((row) => adaptToGerman(row.gender)),
                    datasets: [
                        {
                            label: 'Anteile direkter Zitate von Männern und Frauen',
                            data: rows.map((row) => row.total),
                            backgroundColor: [
                                usedColorSet.female, //'rgba(242, 154, 89, 1)',   // #F29A59 (female) with transparency
                                usedColorSet.male //'rgba(15, 32, 58, 1)',     // #0F203A (male) with transparency
                            ],
                            borderColor: [
                                usedColorSet.female, //'rgba(242, 154, 89, 1)',   // #F29A59 (female) with transparency
                                usedColorSet.male//'rgba(15, 32, 58, 1)',     // #0F203A (male) with transparency
                            ],
                            borderWidth: 1,
                        },
                    ],
                });
            }
            else if (selectedChart === 'stereotypePieChart') {
                const rows = await genderStereotypeOverall(startDate, endDate, selectedStereotype.id, selectedCategory, selectedHighLevelPosition);
                const description = createDescription(startDate, endDate, rows, selectedChart);
                setDescription(description);
                const usedColorSet = getInUseColorSet();

                // Group the data by `stereo` field
                const groupedData = rows.reduce((acc, row) => {
                    if (!acc[row.stereo]) {
                        acc[row.stereo] = { labels: [], data: [] };
                    }
                    acc[row.stereo].labels.push(adaptToGerman(row.gender));
                    acc[row.stereo].data.push(row['count(ap.name)']);
                    return acc;
                }, {});

                // Prepare datasets for each stereotype
                const stereotypeChartData = Object.keys(groupedData).map((stereo) => ({
                    labels: groupedData[stereo].labels,
                    datasets: [
                        {
                            label: `Gender distribution for ${stereo}`,
                            data: groupedData[stereo].data,
                            backgroundColor: [
                                usedColorSet.female,
                                usedColorSet.male,
                            ],
                            borderColor: [
                                usedColorSet.female,
                                usedColorSet.male,
                            ],
                            borderWidth: 1,
                        },
                    ],
                }));

                setStereotypePieChartData(stereotypeChartData);
            }

            else if (selectedChart === 'genderLineChart') {
                const rows = await genderMentionByMonth(startDate, endDate, selectedCategory, user ? user : '', selectedHighLevelPosition);
                const description = createDescription(startDate, endDate, rows, selectedChart, '', getCategoryNameById(selectedCategory), selectedHighLevelPosition);
                setDescription(description);
                const data = {
                    rows: rows,
                    colorSet: getInUseColorSet(true)
                };
                setGenderLineChartData(data);
            } else if (selectedChart === 'personLineChart') {
                const rows = await singlePersonMentionByMonth(startDate, endDate, selectedPeople, selectedHighLevelPosition);
                const total_count = await totalNumberOfArticles(startDate, endDate)
                const description = createDescription(startDate, endDate, rows, selectedChart, '', '', '', total_count);
                setDescription(description);
                const data = {
                    rows: rows,
                    colorSet: getInUseColorSet(true)
                };
                setPersonLineChartData(data);
            } else if (selectedChart === 'genderCategoryBarChart') {
                const rows = await genderMentionByCategory(startDate, endDate, selectedPublisher, selectedHighLevelPosition);
                const total = await genderMentionOverall(startDate, endDate, selectedPublisher, '', selectedHighLevelPosition);
                const description = createDescription(startDate, endDate, rows, selectedChart, '', '', '', total);
                setDescription(description);
                const data = {
                    rows: rows,
                    colorSet: getInUseColorSet(false)
                };
                setGenderCategoryBarChartData(data);
            }
        } catch (e) {

        }

        setIsFetchingData(false);
        setFetchedDataForChart(true);
    };

    const router = useRouter();

    const handleLoginRedirect = () => {
        router.push('/login?successfulLogin=false');
    };

    const handleLogout = () => {
        localStorage.removeItem('user');
        window.location.reload();
    };

    const handleStartDateChange = (date) => {
        setStartDate(date);
    };

    const handleEndDateChange = (date) => {
        setEndDate(date);
    };

    const handleChartSelection = async (event) => {
        const selectedValue = event.target.value;
        setSelectedChart(selectedValue);

        if (selectedValue === 'stereotypePieChart') {
            const fetchedStereotypes = await fetchStereotypeList();
            // const stereotypeNames = fetchedStereotypes.map((item) => item.stereoTypeComparison);
            setStereotypes(fetchedStereotypes);
            setSelectedStereotype(fetchedStereotypes[0] || { id: null, stereoTypeComparison: '' }); // Set to the first stereotype or empty if none

        }

        if (selectedValue === 'personLineChart') {
            const fetchedPeoples = await fetchPersonList();
            const peopleNames = fetchedPeoples.map((item) => item.name);
            setPeoples(peopleNames);
        }

        if (selectedValue === 'mentionPieChart' || selectedValue === 'quotePieChart' || selectedValue === 'genderCategoryBarChart') {
            if (successfulLogin) {
                loadPublishers()
            }

        }
        if (selectedValue === 'genderLineChart') {

        }
    };

    const handleStereotypeSelection = (event) => {
        const selectedId = event.target.value; // assuming this is the id
        const selectedStereotype = stereotypes.find(stereotype => stereotype.id === parseInt(selectedId));
        setSelectedStereotype(selectedStereotype || { id: null, stereoTypeComparison: '' });
    };

    const handleCategorySelection = (event) => {
        setSelectedCategory(event.target.value);
    };

    const handleHighLevelPositionSelection = (event) => {
        setSelectedHighLevelPosition(event.target.value);
    };

    const handlePeopleSelection = (event, value) => {
        setSelectedPeople(value);
    };

    const handlePublisherSelection = (event, value) => {
        setSelectedPublisher(event.target.value);
    };

    const getInUseColorSet = (usesCategoryFilter = true) => {
        return selectedHighLevelPosition ? colors.highLevelPositionsSelected : (usesCategoryFilter && (selectedCategory && selectedCategory !== 'All') ? colors.categorySelected : colors.default);
    }
    
    return (
        <div className="w-full h-full flex flex-col">
            {isCheckingSession ? (
                <div className="flex w-full h-100">
                    <CircularProgress className='m-auto'/>
                </div>
            ) : (
                // {/* Main content area */}
                <div className="flex w-full flex-grow p-0 flex-wrap md:no-flex-wrap" >
                    {/* Left side (Controls) */}
                    <div className="md:w-80 w-full p-0 flex flex-col overflow-y-auto p-2 space-y-2 bg-gett-gradient-1">

                        {/* Header section (Login/Logout and Dashboard title) */}
                        <div className="w-full flex items-start px-2 py-1">
                            <h1 className="text-2xl  font-sans flex"><img className='mr-2' alt='GETT' src="/Logo_GETT_final.svg"/>Dashboard</h1>
                        </div>
                        <div className="flex flex-col">
                            <label className=""><FontAwesomeIcon icon={faChartSimple} className="mr-2" />Diagramm auswählen:</label>
                            <select
                                className="bg-white border border-gray-300 rounded px-2 py-1 shadow-inner "
                                value={selectedChart}
                                onChange={handleChartSelection}
                            >
                                <option value="mentionPieChart">Geschlechterverteilung</option>
                                <option value="genderLineChart">Geschlechterverteilung über die Zeit</option>
                                <option value="personLineChart">Nennungen einzelner Personen</option>
                                <option value="genderCategoryBarChart">Geschlechterverteilung nach Ressorts</option>
                                <option value="quotePieChart">Zitate Anteile der Geschlechter</option>
                            </select>
                        </div>
                        {selectedChart !== 'None' && (
                            <div className="flex flex-col">
                                <DateRangePicker
                                    startDate={startDate}
                                    endDate={endDate}
                                    onStartDateChange={handleStartDateChange}
                                    onEndDateChange={handleEndDateChange}
                                />
                            </div>
                        )}




                        {/* Conditional Content */}
                        <div className="flex flex-col items-start w-full">
                            {selectedChart === 'stereotypePieChart' && (
                                <div className="flex flex-col items-start w-full ">
                                    
                                        <SelectDropdown
                                            label="Stereotypenvergleich wählen:"
                                            id="stereotype-select"
                                            options={stereotypes.map(stereotype => ({
                                                value: stereotype.id,
                                                display: stereotype.stereoTypeComparison
                                            }))}
                                            value={selectedStereotype?.id || ''}
                                            onChange={handleStereotypeSelection}
                                        />
                                    
                                    <SelectDropdown
                                        label="Ressort auswählen:"
                                        id="category-select"
                                        options={categories}
                                        value={selectedCategory}
                                        onChange={handleCategorySelection}
                                        loading={categories.length === 0}
                                        icon={<FontAwesomeIcon icon={faList} />}
                                    />
                                    <div className="flex flex-col w-full">
                                        <SelectDropdown
                                            label="Nach Spitzenpostionen filtern:"
                                            id="hlp-select"
                                            options={highlevelpositions.map((pos) => ({ value: pos.value, display: pos.display }))}
                                            value={selectedHighLevelPosition}
                                            onChange={handleHighLevelPositionSelection}
                                            loading={false}
                                            icon={<><FontAwesomeIcon icon={faChessQueen} /><FontAwesomeIcon icon={faChessKing} /></>}
                                        />
                                    </div>
                                </div>
                            )}

                            {(selectedChart === 'mentionPieChart' || selectedChart === 'quotePieChart') && (
                                <div className="flex flex-col items-start w-full ">
                                    {successfulLogin && (
                                        <SelectDropdown
                                            label="Quelle auswählen:"
                                            id="publisher-select"
                                            options={publishers}
                                            value={selectedPublisher}
                                            onChange={handlePublisherSelection}
                                            loading={false}
                                        />
                                    )}
                                    <SelectDropdown
                                        label="Ressort auswählen:"
                                        id="category-select"
                                        options={categories}
                                        value={selectedCategory}
                                        onChange={handleCategorySelection}
                                        loading={categories.length === 0}
                                        icon={<FontAwesomeIcon icon={faList} />}
                                    />
                                    <SelectDropdown
                                        label="Nach Spitzenpostionen filtern:"
                                        id="hlp-select"
                                        options={highlevelpositions.map((pos) => ({ value: pos.value, display: pos.display }))}
                                        value={selectedHighLevelPosition}
                                        onChange={handleHighLevelPositionSelection}
                                        loading={false}
                                        icon={<><FontAwesomeIcon icon={faChessQueen} /><FontAwesomeIcon icon={faChessKing} /></>}
                                    />
                                </div>
                            )}

                            {selectedChart === 'genderCategoryBarChart' && (
                                <div className="flex flex-col items-start w-full ">
                                    {successfulLogin && (<SelectDropdown
                                        label="Quelle auswählen:"
                                        id="publisher-select"
                                        options={publishers}
                                        value={selectedPublisher}
                                        onChange={handlePublisherSelection}
                                        loading={false}
                                    />)}
                                    <div className="flex flex-col w-full">
                                        <SelectDropdown
                                            label="Nach Spitzenpostionen filtern:"
                                            id="hlp-select"
                                            options={highlevelpositions.map((pos) => ({ value: pos.value, display: pos.display }))}
                                            value={selectedHighLevelPosition}
                                            onChange={handleHighLevelPositionSelection}
                                            loading={false}
                                            icon={<><FontAwesomeIcon icon={faChessQueen} /><FontAwesomeIcon icon={faChessKing} /></>}
                                        />
                                    </div>
                                </div>

                            )}

                            {selectedChart === 'genderLineChart' && (
                                <div className="flex flex-col items-start w-full">
                                    <div className="flex flex-col  w-full">
                                        <SelectDropdown
                                            label="Ressort auswählen:"
                                            id="category-select"
                                            options={categories}
                                            value={selectedCategory}
                                            onChange={handleCategorySelection}
                                            loading={categories.length === 0}
                                            icon={<FontAwesomeIcon icon={faList} />}
                                        />
                                    </div>
                                    <div className="flex flex-col w-full">
                                        <SelectDropdown
                                            label="Nach Spitzenpostionen filtern:"
                                            id="hlp-select"
                                            options={highlevelpositions.map((pos) => ({ value: pos.value, display: pos.display }))}
                                            value={selectedHighLevelPosition}
                                            onChange={handleHighLevelPositionSelection}
                                            loading={false}
                                            icon={<><FontAwesomeIcon icon={faChessQueen} /><FontAwesomeIcon icon={faChessKing} /></>}
                                        />
                                    </div>
                                </div>
                            )}

                            {selectedChart === 'personLineChart' && (
                                <div className="flex flex-col justify-center items-start w-full">
                                    <div className="flex flex-col w-full">
                                        <label className="">Personen suchen:</label>
                                        <Autocomplete
                                            className="w-full bg-white rounded shadow-inner "
                                            multiple
                                            id="people-autocomplete"
                                            options={peoples}
                                            getOptionLabel={(option) => option}
                                            filterSelectedOptions
                                            onChange={handlePeopleSelection}
                                            renderInput={(params) => (
                                                <TextField
                                                    {...params}
                                                    variant="outlined"
                                                    label=""
                                                    placeholder=""
                                                />
                                            )}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="flex flex-col w-full items-end">
                            {selectedChart !== 'None' && !isFetchingData && (
                                <div>
                                    <button
                                        className="bg-gray-500 hover:bg-gray-700 text-white text-sm font-bold py-1 px-4 rounded"
                                        onClick={fetchData}
                                    >
                                        <FontAwesomeIcon icon={faArrowsRotate} className="mr-2" />Diagramm aktualisieren
                                    </button>

                                </div>
                            )}


                            {isFetchingData && (
                                <div className="flex">
                                    <CircularProgress />
                                </div>
                            )}
                        </div>

                        <ColorHints colors={colors}></ColorHints>
                        <div className='flex md:flex-col grow items-center justify-center content-center py-2'>
                            <a className='m-2 w-60 md:w-1/2'  href='https://www.tumcso.com'>
                                <img className='rounded' alt='Chair for Strategy and Organization' src="/cso.webp"/>
                            </a>
                            <a className='m-2 w-60 md:w-1/2 p-2 bg-white rounded'  href='https://www.yathos.de'>
                                <img className='rounded' alt='yathos GmbH' src="/yathos.png"/>
                            </a>
                            <a className='m-2 w-60 md:w-1/2 p-1 bg-white rounded'  href='https://www.innovative-frauen-im-fokus.de/'>
                                <img className='rounded' alt='Innovative Frauen im Fokus' src="/ifif.jpg"/>
                            </a>
                            <a className='m-2 w-60 md:w-1/2'  href='https://www.bmbf.de/bmbf/de/home/_documents/innovative-frauen-im-fokus.html/'>
                                <img className='rounded' alt='Bundesministerium für Bildung und Forschung' src="/BMBF_Format_richtig.png"/>
                            </a>
                        </div>
                        <div className='flex justify-center'>
                            {user ? (
                                <p className="text-sm my-auto mx-2">Welcome, {user}!</p>
                            ) : (
                                <p className="text-sm "></p>
                            )}
                            <div>
                                <button
                                    className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-1 px-4 text-sm rounded-lg transition duration-300"
                                    onClick={handleLoginRedirect}
                                >
                                    Anmelden
                                </button>
                            </div>

                        </div>
                    </div>

                    {/* Right side (Visualization) */}
                    <div className="content-width-wrapper flex">
                        {!fetchedDataForChart && !isFetchingData && selectedChart == 'personLineChart' &&
                            <div className="flex w-full h-100">
                            <div className='m-auto'>Wählen Sie mindestens eine Person im Filter.</div>
                        </div>
                        }
                        {fetchedDataForChart && !isFetchingData && 
                        <div className="flex flex-col justify-center items-center content-width overflow-hidden p-2 my-auto" id="chartContainer">
                            {/* Chart section */}
                            <div className="flex justify-center flex-col items-center w-full h-4/6" id="chartOnlyContainer">
                                {selectedChart === 'mentionPieChart' && <PieChart data={mentionPieChartData} />}
                                {selectedChart === 'genderLineChart' && <LineChart data={genderLineChartData} isGenderChart={true} title="Geschlechterverteilung über die Zeit" />}
                                {selectedChart === 'personLineChart' && <LineChart data={personLineChartData} isGenderChart={false} title="Nennungen einzelner Personen" />}
                                {selectedChart === 'genderCategoryBarChart' && <BarChart data={genderCategoryBarChartData} categories={categories}/>}
                                {selectedChart === 'quotePieChart' && <PieChart data={quotePieChartData} />}
                            </div>
                            {/* Description section */}
                            <div className="flex flex-col justify-center items-center w-100 md:px-md-20 p-2">
                                <div className="text-center text-sm">{description}</div>
                                {/* Download button */}
                                <button
                                    className="bg-gray-500 hover:bg-gray-700 text-white text-sm font-bold py-1 px-4 rounded m-2 no-download"
                                    onClick={() => {
                                        document.querySelectorAll('.no-download').forEach(el => el.style.display = 'none');

                                        html2canvas(document.querySelector('#chartContainer')).then(canvas => {
                                            const link = document.createElement('a');
                                            link.download = 'chart.png';
                                            link.href = canvas.toDataURL();
                                            link.click();
                                        });

                                        document.querySelectorAll('.no-download').forEach(el => el.style.display = '');
                                    }}
                                >
                                    <FontAwesomeIcon icon={faDownload} className="mr-2" />Diagramm mit Text speichern
                                </button>
                                <button
                                    className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-1 px-4 text-sm rounded flex items-center justify-center no-download"
                                    onClick={() => {
                                        navigator.clipboard.writeText(`${description} © GETT by CSO / BMBF`);
                                    }}
                                >
                                    <FontAwesomeIcon icon={faClipboard} className="mr-2" /> Nur Text in die Zwischenablage kopieren 
                                </button>
                            </div>
                        </div>}
                        {isFetchingData && (
                                <div className="flex w-full h-100">
                                    <CircularProgress className='m-auto'/>
                                </div>
                            )}
                    </div>


                </div>
            )}
        </div>
    );
}

export default Dashboard;

