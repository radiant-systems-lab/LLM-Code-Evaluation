# Time and Date Operations
import datetime
import time
import calendar
from dateutil import parser, relativedelta
import pytz
from dateutil.tz import tzlocal

def datetime_operations():
    """Basic datetime operations"""
    now = datetime.datetime.now()
    utc_now = datetime.datetime.utcnow()
    
    # Create specific dates
    birthday = datetime.date(1990, 5, 15)
    meeting_time = datetime.datetime(2024, 1, 1, 14, 30, 0)
    
    # Date arithmetic
    one_week_later = now + datetime.timedelta(weeks=1)
    age = now.date() - birthday
    
    # Format dates
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
    iso_date = now.isoformat()
    
    return {
        'current_time': str(now),
        'age_in_days': age.days,
        'formatted': formatted_date,
        'iso_format': iso_date
    }

def timezone_operations():
    """Timezone handling with pytz"""
    # Define timezones
    utc = pytz.UTC
    eastern = pytz.timezone('US/Eastern')
    pacific = pytz.timezone('US/Pacific')
    tokyo = pytz.timezone('Asia/Tokyo')
    
    # Current time in different zones
    utc_time = datetime.datetime.now(utc)
    eastern_time = utc_time.astimezone(eastern)
    pacific_time = utc_time.astimezone(pacific)
    tokyo_time = utc_time.astimezone(tokyo)
    
    # Local timezone
    local_tz = tzlocal()
    local_time = datetime.datetime.now(local_tz)
    
    return {
        'utc': str(utc_time),
        'eastern': str(eastern_time),
        'pacific': str(pacific_time),
        'tokyo': str(tokyo_time),
        'local': str(local_time)
    }

def date_parsing():
    """Parse various date formats"""
    date_strings = [
        "2024-01-15",
        "January 15, 2024",
        "15/01/2024",
        "2024-01-15T10:30:00",
        "Mon, 15 Jan 2024 10:30:00 GMT"
    ]
    
    parsed_dates = []
    for date_str in date_strings:
        try:
            parsed = parser.parse(date_str)
            parsed_dates.append(str(parsed))
        except Exception as e:
            parsed_dates.append(f"Error: {e}")
    
    return parsed_dates

def calendar_operations():
    """Calendar operations"""
    year = 2024
    month = 2
    
    # Get calendar info
    days_in_month = calendar.monthrange(year, month)[1]
    is_leap = calendar.isleap(year)
    month_name = calendar.month_name[month]
    weekday_names = list(calendar.day_name)
    
    # First day of month
    first_day = datetime.date(year, month, 1)
    first_weekday = first_day.weekday()
    
    return {
        'days_in_february': days_in_month,
        'is_leap_year': is_leap,
        'month_name': month_name,
        'first_day_weekday': weekday_names[first_weekday]
    }

def time_operations():
    """Time measurement and delays"""
    # Measure execution time
    start_time = time.time()
    
    # Simulate some work
    sum_result = sum(i * i for i in range(10000))
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Performance counter (more precise)
    start_perf = time.perf_counter()
    time.sleep(0.1)  # Small delay
    end_perf = time.perf_counter()
    perf_time = end_perf - start_perf
    
    return {
        'sum_result': sum_result,
        'execution_time': execution_time,
        'sleep_time': perf_time
    }

def relative_date_operations():
    """Relative date calculations with dateutil"""
    base_date = datetime.date(2024, 1, 15)
    
    # Add relative time
    next_month = base_date + relativedelta.relativedelta(months=1)
    next_year = base_date + relativedelta.relativedelta(years=1)
    last_friday = base_date + relativedelta.relativedelta(weekday=relativedelta.FR(-1))
    
    # Complex calculations
    same_day_next_month = base_date + relativedelta.relativedelta(months=1, day=base_date.day)
    end_of_month = base_date + relativedelta.relativedelta(day=31)
    
    return {
        'base_date': str(base_date),
        'next_month': str(next_month),
        'next_year': str(next_year),
        'last_friday': str(last_friday),
        'end_of_month': str(end_of_month)
    }

if __name__ == "__main__":
    print("Time and date operations...")
    
    dt_result = datetime_operations()
    print(f"Current time: {dt_result['current_time']}")
    
    tz_result = timezone_operations()
    print(f"UTC time: {tz_result['utc']}")
    
    parsed_result = date_parsing()
    print(f"Parsed {len(parsed_result)} date strings")
    
    cal_result = calendar_operations()
    print(f"February 2024 has {cal_result['days_in_february']} days")
    
    time_result = time_operations()
    print(f"Execution time: {time_result['execution_time']:.6f} seconds")
    
    rel_result = relative_date_operations()
    print(f"Relative dates calculated from {rel_result['base_date']}")