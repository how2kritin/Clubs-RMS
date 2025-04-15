# Interviews

## frontend stuff

- page for admin to create schedule (fancy form)
- calendar view for all users


## explaining

calendar is basically a set of events

we decided on a global calendar, and specific users will be able to see specific events
- club admins and members can see all events for their club
- applicants can see the slots assigned to them

so i need a table to store calendar events


now, when a form has accepted all responses, the club admin will  click on a button that alows them to 
create a interview schedule
- they will enter the days they will take interviews
- the times on each day they will take interviews (start_time, end_time) pairs to allow breaks
- they will give slot length so system can autimatically create, well, slots
- so if you dont understand what a slot is, it is a chunk of time in which one interview will be held (or > 1 if >1 panels are there)

Now a club assigns multiple people to take intervies, so mutiple "panels" can exist in the same slot
We assume that the same number of panels will be present for all slots, and so the club admin enters the number of panels and maybe interview names too


With all this info, the system will now create calendar events for all applicants

So the logical hierarchy for ownership (think like ER diagram idk how else to explain this)

CalendarEvent (1..N) --> (1) InterviewSlot (1..N) --> (1) InterviewSchedule (1) --> (1) Form
CalendarEvent (1) --- (1) InterviewPanel


### backend tables

- CalendarEvent (user-specific event)
- InterviewSlot (all slots for a schedule, created by club admin)
- InterviewPanel (assigned by clun admin)
- InterviewSchedule (schedule for a recuritment form)

### Relationships b/w the tables
(left refers to (->) right)

CalendarEvent -> InterviewSchedule
CalendarEvent -> InterviewPanel
CalendarEvent -> InterviewSlot (ownership)
CalendarEvent -> User (visibility)
CalendarEvent -> Club (efficiency? may improve search efficiency)

InterviewSlot -> InterviewSchedule (ownership)
InterviewSlot -> Club (efficiency?)

InterviewPanel -> InterviewSchedule (ownership)

InterviewSchedule -> Form (ownership)
InterviewSchedule -> Club (ownership)

Form -> Club (ownership) (varun)
Application -> Form (aggregate/ownership) (varun)
Form -> Application (aggregate/ownership) (varun)
