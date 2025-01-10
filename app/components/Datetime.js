"use client";

import styles from './styles/datetime.module.css'
import React, { useState } from 'react';
import 'react-datepicker/dist/react-datepicker.css'; 
import dayjs from 'dayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { StaticDateTimePicker } from '@mui/x-date-pickers/StaticDateTimePicker';

import TextField from '@mui/material/TextField';

export function Datetime({ selectedDateTime, setSelectedDateTime }) {
    // const [selectedDateTime, setSelectedDateTime] = useState(dayjs());
    const [showPicker, setShowPicker] = useState(false); 
  
    const handleButtonClick = () => {
      setShowPicker((prev) => !prev); 
    };
  
    return (
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <div className={styles.dateTimeContainer}>
          <button className={styles.button} onClick={handleButtonClick}>
            {selectedDateTime ? selectedDateTime.format('MMMM D, YYYY h:mm A') : 'Select Date & Time'}
          </button>
  
          {showPicker && (
            <div className={styles.pickerContainer}>
              <StaticDateTimePicker
                displayStaticWrapperAs="desktop"
                value={selectedDateTime}
                onChange={(newValue) => {
                  setSelectedDateTime(newValue);
                }}
                renderInput={(params) => <TextField {...params}/>}
              />
            </div>
          )}
        </div>
      </LocalizationProvider>
    )
  }

export default Datetime;