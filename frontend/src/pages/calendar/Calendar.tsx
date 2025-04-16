import { useEffect, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import { EventContentArg, EventInput } from '@fullcalendar/core';
import './Calendar.css';

// Type for calendar event data
interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end?: Date;
  color?: string;
}
1
// Calendar component props
interface CalendarProps {
  events: EventInput[];
}

// Calendar display component
const CalendarComponent = ({ events }: CalendarProps) => {
  return (
    <div className="calendar-container">
      <FullCalendar
        plugins={[dayGridPlugin]}
        initialView="dayGridMonth"
        events={events}
        eventContent={(eventInfo: EventContentArg) => (
          <div>
            <b>{eventInfo.timeText}</b>
            <i>{eventInfo.event.title}</i>
          </div>
        )}
      />
    </div>
  );
};

// Event loader component that fetches and manages state
export const CalendarLoader = () => {
  const [events, setEvents] = useState<EventInput[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch('/api/calendar/events', {
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: CalendarEvent[] = await response.json();

        // Transform data to FullCalendar's EventInput format
        const formattedEvents: EventInput[] = data.map(event => ({
          id: event.id,
          title: event.title,
          start: event.start,
          end: event.end,
          color: event.color,
        }));

        setEvents(formattedEvents);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch events');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  if (loading) {
    return <div className="loading">Loading calendar events...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return <CalendarComponent events={events} />;
};

export default CalendarLoader;