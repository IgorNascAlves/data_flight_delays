import pandas
import random
from scipy.stats import norm
import numpy as np

AIRLINE_COUNT=3
DAILY_FLIGHT_COUNT=15
ORIGIN_COUNT=10
AIRCRAFT_TYPES = ['Boeing 737', 'Airbus A320', 'Boeing 777', 'Airbus A330', 'Boeing 787', 'Embraer E175']
HOLIDAY_COUNT = 20
YEAR_FROM=2010
YEAR_TO=2022

def mixture_rvs(size, w1, mu1, var1, mu2, var2):
    w2 = 1 - w1
    # Draw uniform random numbers to decide which distribution to sample from
    mixture_component = np.random.choice([0, 1], p=[w1, w2], size=size)

    # Sample from the appropriate normal distribution for each component
    samples = np.where(
        mixture_component == 0,
        norm.rvs(loc=mu1, scale=np.sqrt(var1), size=size),
        norm.rvs(loc=mu2, scale=np.sqrt(var2), size=size)
    )

    return samples

class Airline:
    def __init__(self, code):
        self.code = code
        self.seeds = [random.random() for i in range(6)]
        # delay center between -30 and 30
        self.delay_center = random.randint(-30, 30)

    def __str__(self):
        return self.code

    def __repr__(self):
        return self.code



def generate_origin(current):
    while True:
        # creates a random two letter airline code
        origin = []
        origin.append(chr(random.randint(65, 90)))
        origin.append(chr(random.randint(65, 90)))
        origin.append(chr(random.randint(65, 90)))
        origin = ''.join(origin)
        # checks if the airline code is already in use
        if origin not in current:
            return origin


# 'flight_id'
# 'scheduled_time'
# 'airline' OK 
# 'aircraft_type' OK
# 'operation_type' ARRIVE/DEPART/TURNAROUND?????????
# 'origin'
# 'destination' OK
# 'home_airport'
# 'takeoff_timestamp'
# 'landing_timestamp'
# 'is_cancelled'

# Flight data: example columns
# flight_id: String
# scheduled_time: datetime
# airline: string (iata code)
# aircraft_type: string
# operation_type: “arrival”, “departure” or “turnaround”
# Information about the origin, destination and home airport
# Timestamps for different legs of the flight, e.g. takeoff
# Is_cancelled: bool

#  Flight type and number OK
# - Origin and destination airport OK
# - schengen/non-schengen, EU/non-EU OK
# - Airline
# - Aircraft type
# - Month, day, weekday
# - time of day OK
# - Holiday, holiday during adjacent days OK



def generate_flight(airlines, k, origins):
    flight = []

    # flight k
    flight.append(k)

    # flight id (LL3050)
    airline = random.choice(airlines)
    flight.append(airline)

    # weighted for aircraft type
    aircraft_type = random.choices(AIRCRAFT_TYPES, weights=[
            10 * airline.seeds[0],
            10 * airline.seeds[1],
            5 * airline.seeds[2],
            5 * airline.seeds[3],
            5 * airline.seeds[4],
            5 * airline.seeds[5]])[0]
    flight.append(aircraft_type)

    # 80% is schengen
    flight.append(random.choices(['schengen', 'non-schengen'], weights=[8, 2])[0])

    # random origin
    flight.append(random.choice(origins))

    # arrival time
    # using a normal distribution centered at 9:00 and another centered at 17 with a standard deviation of 2 hours
    # create a normal centered on 9, var 2
    arrival_time = mixture_rvs(1, 0.5, 9, 2, 17, 2)[0]
    flight.append(arrival_time)

    # staying time is normal mu=3, var=1, minimum should be 1h
    staying_time = max(2, int(norm.rvs(loc=3.5, scale=1, size=1)[0]))
    departure_time = arrival_time + staying_time
    flight.append(departure_time)

    return flight


def generate_airline(current):
    while True:
        # creates a random two letter airline code
        airline = []
        airline.append(chr(random.randint(65, 90)))
        airline.append(chr(random.randint(65, 90)))
        airline = ''.join(airline)
        # checks if the airline code is already in use
        if airline not in current:
            return Airline(airline)


def generate_holiday(current):
    while True:
        # picks a random number between 1 and 365
        holiday = random.randint(1, 365)
        # checks if the holiday is already in use
        if holiday not in current:
            return holiday


def generate_real_flight(base_flight, year, day):
    flight = []
    flight.extend(base_flight)

    delay_center = base_flight[1].delay_center
    # delay is normal on the center with 15 var
    delay = norm.rvs(loc=delay_center, scale=15, size=1)[0]

    # in holiday delay center is worse in plus between 10 and 60
    is_holiday = day in holidays
    if is_holiday:
        # use a normal
        delay += norm.rvs(loc=35, scale=10, size=1)[0]

    flight.append(day)
    flight.append(year)
    flight.append(is_holiday)
    flight.append(delay)

    return flight
    

airlines = []
for i in range(AIRLINE_COUNT):
    airlines.append(generate_airline(airlines))
print(airlines)

origins = []
for i in range(ORIGIN_COUNT):
    origins.append(generate_origin(origins))
print(origins)

holidays = set()
for i in range(HOLIDAY_COUNT):
    h = generate_holiday(holidays)
    holidays.add(h)
print(holidays)

daily_flights = []
for i in range(1, DAILY_FLIGHT_COUNT + 1):
    daily_flights.append(generate_flight(airlines, i, origins))
print(daily_flights)

flights = []
for year in range(YEAR_FROM, YEAR_TO+1):
    # TODO voos de dias especificos
    # voos de natal
    for day in range(365):
        for base_flight in daily_flights:
            flights.append(generate_real_flight(base_flight, year, day))


# output das colunas
# is_holiday
# cia_area
# deveria ser capaz de prever o delay

print(len(flights))
print(flights[:10])