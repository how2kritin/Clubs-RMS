import React, { useState, useEffect, ChangeEvent, FormEvent } from 'react';
import './ScheduleInterviews.css';

interface TimeRange {
  id: number;
  startTime: string;
  endTime: string;
}

interface DateSchedule {
  date: string;
  timeRanges: TimeRange[];
}

interface ScheduleInterviewsFormResponse {
  interviewSchedule: {
    slotDurationMinutes: number;
    interviewPanelCount: number;
    dates: Array<{
      date: string;
      timeRanges: Array<{
        startTime: string;
        endTime: string;
      }>;
    }>;
    totalInterviewSlots: number;
  };
}

const ScheduleInterviews: React.FC = () => {
  const [dates, setDates] = useState<DateSchedule[]>([]);
  const [slotDuration, setSlotDuration] = useState<number>(30); // in minutes
  const [panelCount, setPanelCount] = useState<number>(1);
  const [newDate, setNewDate] = useState<string>('');
  const [totalSlots, setTotalSlots] = useState<number>(0);

  // Calculate total slots whenever relevant data changes
  useEffect(() => {
    calculateTotalSlots();
  }, [dates, slotDuration, panelCount]);

  const calculateTotalSlots = (): void => {
    if (!dates.length || slotDuration <= 0) return;

    // Calculate total minutes across all time ranges
    const totalMinutes = dates.reduce((sum, date) => {
      return sum + date.timeRanges.reduce((daySum, range) => {
        const startTime = parseTimeToMinutes(range.startTime);
        const endTime = parseTimeToMinutes(range.endTime);
        return daySum + (endTime - startTime);
      }, 0);
    }, 0);

    // Calculate slots and multiply by panel count
    const slots = Math.floor(totalMinutes / slotDuration) * panelCount;
    setTotalSlots(slots);
  };

  const parseTimeToMinutes = (timeString: string): number => {
    if (!timeString) return 0;
    const [hours, minutes] = timeString.split(':').map(Number);
    return hours * 60 + minutes;
  };

  const handleAddDate = (): void => {
    if (!newDate) return;

    // Check if date already exists
    if (dates.some(d => d.date === newDate)) {
      alert('This date is already added');
      return;
    }

    setDates([...dates, { date: newDate, timeRanges: [{ id: Date.now(), startTime: '', endTime: '' }] }]);
    setNewDate('');
  };

  const handleRemoveDate = (dateToRemove: string): void => {
    setDates(dates.filter(date => date.date !== dateToRemove));
  };

  const handleAddTimeRange = (dateIndex: number): void => {
    const updatedDates = [...dates];
    updatedDates[dateIndex].timeRanges.push({ id: Date.now(), startTime: '', endTime: '' });
    setDates(updatedDates);
  };

  const handleRemoveTimeRange = (dateIndex: number, rangeId: number): void => {
    const updatedDates = [...dates];
    updatedDates[dateIndex].timeRanges = updatedDates[dateIndex].timeRanges.filter(range => range.id !== rangeId);
    setDates(updatedDates);
  };

  const handleTimeRangeChange = (dateIndex: number, rangeId: number, field: 'startTime' | 'endTime', value: string): void => {
    const updatedDates = [...dates];
    const rangeIndex = updatedDates[dateIndex].timeRanges.findIndex(range => range.id === rangeId);
    updatedDates[dateIndex].timeRanges[rangeIndex][field] = value;
    setDates(updatedDates);
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
    e.preventDefault();

    // Validate form
    if (!dates.length) {
      alert('Please add at least one interview date');
      return;
    }

    if (slotDuration <= 0) {
      alert('Interview slot duration must be greater than 0');
      return;
    }

    if (panelCount <= 0) {
      alert('Number of panels must be greater than 0');
      return;
    }

    // Check if all time ranges are filled
    for (const date of dates) {
      for (const range of date.timeRanges) {
        if (!range.startTime || !range.endTime) {
          alert('Please fill in all time ranges');
          return;
        }

        // Verify end time is after start time
        if (parseTimeToMinutes(range.endTime) <= parseTimeToMinutes(range.startTime)) {
          alert('End time must be after start time');
          return;
        }
      }
    }

    // Create final JSON data
    const formattedData: ScheduleInterviewsFormResponse = {
      interviewSchedule: {
        slotDurationMinutes: slotDuration,
        interviewPanelCount: panelCount,
        dates: dates.map(date => ({
          date: date.date,
          timeRanges: date.timeRanges.map(range => ({
            startTime: range.startTime,
            endTime: range.endTime
          }))
        })),
        totalInterviewSlots: totalSlots
      }
    };

    console.log('Form submitted:', formattedData);
    fetch('/api/interviews/schedule_interviews', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formattedData),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Success:', data);
      })
      .catch(error => {
        console.error('Error:', error);
      });

  };

  return (
    <div className="schedule-container">
      <h1 className="page-title">Schedule Interviews</h1>

      <form onSubmit={handleSubmit} className="schedule-form">
        {/* Interview Slot Duration */}
        <div className="form-group">
          <label className="form-label">
            Interview Slot Duration (minutes):
          </label>
          <input
            type="number"
            min="1"
            value={slotDuration}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setSlotDuration(parseInt(e.target.value) || 0)}
            className="form-input"
            required
          />
        </div>

        {/* Interview Panel Count */}
        <div className="form-group">
          <label className="form-label">
            Number of Interview Panels:
          </label>
          <input
            type="number"
            min="1"
            value={panelCount}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setPanelCount(parseInt(e.target.value) || 0)}
            className="form-input"
            required
          />
        </div>

        {/* Interview Dates Section */}
        <div className="dates-section">
          <h2 className="section-title">Interview Dates</h2>

          {/* Add New Date */}
          <div className="add-date-container">
            <input
              type="date"
              value={newDate}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setNewDate(e.target.value)}
              className="date-input"
            />
            <button
              type="button"
              onClick={handleAddDate}
              className="add-date-button"
            >
              Add Date
            </button>
          </div>

          {/* List of Added Dates */}
          {dates.length > 0 ? (
            <div className="dates-list">
              {dates.map((date, dateIndex) => (
                <div key={date.date} className="date-item">
                  <div className="date-header">
                    <h3 className="date-title">
                      {new Date(date.date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </h3>
                    <button
                      type="button"
                      onClick={() => handleRemoveDate(date.date)}
                      className="remove-date-button"
                    >
                      Remove Date
                    </button>
                  </div>

                  {/* Time Ranges for this Date */}
                  <div className="time-ranges-container">
                    <h4 className="time-ranges-title">Time Ranges:</h4>

                    {date.timeRanges.map((range) => (
                      <div key={range.id} className="time-range-item">
                        <input
                          type="time"
                          value={range.startTime}
                          onChange={(e: ChangeEvent<HTMLInputElement>) =>
                            handleTimeRangeChange(dateIndex, range.id, 'startTime', e.target.value)
                          }
                          className="time-input"
                          required
                        />
                        <span className="time-separator">to</span>
                        <input
                          type="time"
                          value={range.endTime}
                          onChange={(e: ChangeEvent<HTMLInputElement>) =>
                            handleTimeRangeChange(dateIndex, range.id, 'endTime', e.target.value)
                          }
                          className="time-input"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => handleRemoveTimeRange(dateIndex, range.id)}
                          className="remove-time-button"
                        >
                          Remove
                        </button>
                      </div>
                    ))}

                    <button
                      type="button"
                      onClick={() => handleAddTimeRange(dateIndex)}
                      className="add-time-button"
                    >
                      + Add Another Time Range
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-dates-message">No dates added yet.</p>
          )}
        </div>

        {/* Total Slots Calculation */}
        <div className="summary-container">
          <h3 className="summary-title">Interview Capacity Summary</h3>
          <p className="total-slots">
            Total interview slots available: <span className="slots-count">{totalSlots}</span>
          </p>
          <p className="slots-description">
            (Based on {panelCount} panel{panelCount !== 1 ? 's' : ''} and {slotDuration}-minute slots)
          </p>
        </div>

        <button
          type="submit"
          className="submit-button"
        >
          Save Interview Schedule
        </button>
      </form>

      {/* Display submitted data for demonstration */}
      {/* {formData && (
        <div className="submitted-data-container">
          <h3 className="submitted-data-title">Submitted Data:</h3>
          <pre className="json-display">
            {JSON.stringify(formData, null, 2)}
          </pre>
        </div>
      )} */}
    </div>
  );
};

export default ScheduleInterviews;