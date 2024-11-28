// components/common/DateRangePicker.js
import { faRightFromBracket, faRightToBracket } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'; 
import React from 'react';
import DatePicker, {  registerLocale } from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import de from "date-fns/locale/de"; // the locale you want
registerLocale("de", de); // register it with the name you want

const DateRangePicker = ({ startDate, endDate, onStartDateChange, onEndDateChange }) => {
    const handleStartDateChange = (date) => {
        if (date) {
            // Set the date to the first of the selected month
            onStartDateChange(new Date(Date.UTC(date.getFullYear(), date.getMonth(), 1)));
        }
    };

    const handleEndDateChange = (date) => {
        if (date) {
            // Set the date to the last of the selected month in GMT +2
            const lastDate = new Date(Date.UTC(date.getFullYear(), date.getMonth() + 1, 0)); // Last day of the month
            onEndDateChange(lastDate);
        }
    };

    return (
        <div className="flex flex-col">
            <div className="flex items-start mb-2">
                <label htmlFor="start-date" className="text-sm my-auto mr-auto "><FontAwesomeIcon icon={faRightFromBracket} className="mr-2" />Von</label>
                <DatePicker
                    locale="de"
                    id="start-date"
                    selected={startDate}
                    onChange={handleStartDateChange}
                    selectsStart
                    startDate={startDate}
                    endDate={endDate}
                    showMonthYearPicker
                    dateFormat="MM/yyyy"
                    className="border p-1 rounded shadow-inner "
                />
            </div>
            <div className="flex items-start">
                <label htmlFor="end-date" className="text-sm my-auto mr-auto "><FontAwesomeIcon icon={faRightToBracket} className="mr-2" />Bis</label>
                <DatePicker
                    locale="de"
                    id="end-date"
                    selected={endDate}
                    onChange={handleEndDateChange}
                    selectsEnd
                    startDate={startDate}
                    endDate={endDate}
                    minDate={new Date(startDate.getFullYear(), startDate.getMonth(), 1)} // Adjust minDate to the first of the start month
                    showMonthYearPicker
                    dateFormat="MM/yyyy"
                    className="border p-1 rounded shadow-inner "
                />
            </div>
        </div>
    );
};

export default DateRangePicker;
