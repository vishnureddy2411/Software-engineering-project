from calendar import HTMLCalendar
from datetime import date

class AvailabilityHTMLCalendar(HTMLCalendar):
    def __init__(self, availability, location_id, sport_id):
        super().__init__()
        self.availability = availability
        self.location_id = location_id
        self.sport_id = sport_id

    def formatday(self, day, weekday):
        """ Format a day inside the calendar table """
        if day == 0:
            return '<td class="noday"></td>'  # Empty cell

        day_str = f"{self.year}-{self.month:02d}-{day:02d}"
        available = self.availability.get(day_str, False)

        if available:
            return f'<td class="available" data-date="{day_str}"><a href="#" onclick="selectDate(\'{day_str}\')">{day}</a></td>'
        else:
            return f'<td class="unavailable">{day}</td>'

    def formatmonth(self, year, month, withyear=True):
        """ Override formatmonth to properly set the year and month """
        self.year = year
        self.month = month
        return super().formatmonth(year, month, withyear)

