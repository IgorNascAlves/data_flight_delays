import random
from scipy.stats import norm
import numpy as np
import csv

AIRLINE_COUNT=3
DAILY_FLIGHT_COUNT=15
DAILY_FLIGHT_OPTIONS = 30
ORIGIN_COUNT=10
AIRCRAFT_TYPES = ['Boeing 737', 'Airbus A320', 'Boeing 777', 'Airbus A330', 'Boeing 787', 'Embraer E175']
HOLIDAY_COUNT = 20
YEAR_FROM=2010
YEAR_TO=2022
SEED = 41
AIRCRAFT_WEIGHTS_DELAY = {'Boeing 737':15, 'Airbus A320':5, 'Boeing 777':5, 'Airbus A330':-5, 'Boeing 787':-5, 'Embraer E175':-10}

# set seed for reproducibility
#random.seed(SEED)

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
        self.delay_center = random.randint(-20, 35)

    def __str__(self):
        return self.code

    def __repr__(self):
        return self.code

def generate_origin(current):
    while True:
        # creates a random tree letter origin code
        origin = []
        origin.append(chr(random.randint(65, 90)))
        origin.append(chr(random.randint(65, 90)))
        origin.append(chr(random.randint(65, 90)))
        origin = ''.join(origin)
        # checks if the origin code is already in use
        if origin not in current:
            return origin

def generate_flight(airlines, k, origins):
    flight = []

    # flight k
    flight.append(k)

    # flight id (LL3050)
    airline = random.choices(airlines, weights=[6,3,1])[0]
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
    flight.append(random.choices(origins, weights=[
            random.randint(1,10) * airline.seeds[0],
            random.randint(1,10) * airline.seeds[1],
            random.randint(1,10) * airline.seeds[2],
            random.randint(1,10) * airline.seeds[3],
            random.randint(1,10) * airline.seeds[4],
            random.randint(1,10) * airline.seeds[5],
            random.randint(1,10) * airline.seeds[2],
            random.randint(1,10) * airline.seeds[3],
            random.randint(1,10) * airline.seeds[4],
            random.randint(1,10) * airline.seeds[5]])[0])

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

    # in weekend delay center is worse in plus between 10 and 30
    is_weekend = day % 7 == 0 or day % 7 == 6
    if is_weekend:
        # use a normal
        delay += norm.rvs(loc=20, scale=5, size=1)[0]

    delay += norm.rvs(loc=AIRCRAFT_WEIGHTS_DELAY[base_flight[2]], scale=8, size=1)[0]

    delay += norm.rvs(loc=origins_weights[base_flight[4]], scale=5, size=1)[0]

    # # in some airlines delay center is worse in plus between 10 and 30
    # is_worse_airline = base_flight[1].code in worse_airlines
    # if is_worse_airline:
    #     # use a normal
    #     delay += norm.rvs(loc=20, scale=5, size=1)[0]

    flight.append(day)
    flight.append(year)
    flight.append(is_holiday)
    flight.append(delay)

    return flight


airlines = []
for i in range(AIRLINE_COUNT):
    airlines.append(generate_airline(airlines))
print(airlines)

# airlines with worse delays
# worse_airlines = [airline.code for airline in random.choices(airlines, k=5)]

origins = []
for i in range(ORIGIN_COUNT):
    origins.append(generate_origin(origins))
print(origins)

origins_weights = {origem:random.randint(-15,15) for origem in origins}

#dentro da função generate_holiday, verificar se o if já não garante a condição de não repetição então não precisa ser set pode ser list
holidays = set()
for i in range(HOLIDAY_COUNT):
    h = generate_holiday(holidays)
    holidays.add(h)
print(holidays)

daily_flights_options = []
for i in range(1, DAILY_FLIGHT_OPTIONS + 1):
    daily_flights_options.append(generate_flight(airlines, i, origins))
print(daily_flights_options)

flights = []
for year in range(YEAR_FROM, YEAR_TO+1):
    # TODO voos de dias especificos
    # voos de natal
    for day in range(365):
        daily_flights = random.choices(daily_flights_options, k = DAILY_FLIGHT_COUNT)
        for base_flight in daily_flights:
            flights.append(generate_real_flight(base_flight, year, day))

#function thats saves flights on a csv file
def save_flights(flights):
    with open(r'data\flights4.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["flight_id", "airline", "aircraft_type", "schengen", "origin", "arrival_time", "departure_time", "day", "year", "is_holiday", "delay"])
        for flight in flights:
            writer.writerow(flight)

save_flights(flights)