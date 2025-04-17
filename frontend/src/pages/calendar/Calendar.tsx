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
        eventDidMount={(info) => {
          (info.el as HTMLElement).setAttribute('title', info.event.title);
        }}
        eventTimeFormat={{
          hour: 'numeric',
          minute: '2-digit',
          meridiem: 'short'
        }}
        eventContent={(arg) => {
          return (
            <>
              <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>
                {arg.timeText}
              </div>
              <div style={{ paddingLeft: '0.2rem', fontSize: '0.75rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {arg.event.title}
              </div>
            </>
          );
        }}
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
          color: "#000000", // Optional: Set a default color
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