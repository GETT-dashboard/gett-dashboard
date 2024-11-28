// SelectDropdown.js
import React from 'react';
import CircularProgress from '@mui/material/CircularProgress';

const SelectDropdown = ({ label, id, options, value, onChange, loading, icon }) => {
    return (
      <div className="flex flex-col w-full">
        <label className="">
          {icon && <span className="mr-2">{icon}</span>}
          {label}
        </label>
        {loading ? (
          <div className="flex flex-col items-center">
            <label>Loading {label}...</label>
            <CircularProgress/>
          </div>
        ) : (
          <select
            id={id}
            className="bg-white border border-gray-300 rounded px-2 py-1 w-full shadow-inner "
            value={value}
            onChange={onChange}
          >
            {options.map((option) =>
              typeof option === "string" ? (
                <option key={option} value={option}>
                  {option}
                </option>
              ) : (
                <option key={option.value} value={option.value}>
                  {option.display}
                </option>
              )
            )}
          </select>
        )}
      </div>
    );
  };
  
  export default SelectDropdown;
