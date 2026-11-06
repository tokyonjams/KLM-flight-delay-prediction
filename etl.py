import pandas as pd 
from sqlalchemy import create_engine 
import datetime as dt 
import requests 
import re 
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

url = "https://api.airfranceklm.com/opendata/flightstatus"

headers = {
    "Accept-Language": "",
    "API-Key": os.getenv("API_KEY"),
    "Accept": "application/hal+json"
}

def extract_day(date):

    startRange = f"{date}T00:00:00.000Z"
    endRange = f"{date}T23:59:59.000Z"

    all_flights = []
    page = 1

    while True:

        params = {
            "origin": "AMS",
            "operatingAirlineCode": "KL",
            "startRange": startRange,
            "endRange": endRange,
            "pageNumber": page
        }

        resp = requests.get(
            url,
            headers=headers,
            params=params
        )

        # 416 = no data for this date/page — treat as end of pagination
        if resp.status_code == 416:
            break

        # 403 = API key has hit a pagination/access limit — save what we have
        if resp.status_code == 403:
            print(f"Warning: Access forbidden on page {page} — API key may have a page limit. Stopping here.")
            break

        resp.raise_for_status()

        data = resp.json()

        flights = data.get("operationalFlights", [])

        if not flights:
            break

        all_flights.extend(flights)

        print(f"{date} | Page {page} | {len(flights)} flights")

        page += 1

    return {
        "operationalFlights": all_flights
    }



def transform_flights(data):

    flight_status = []

    for status in data.get('operationalFlights', []):

        airline_info = status.get('airline', {}) or {}

        airline_code = airline_info.get('code')
        airline_name = airline_info.get('name')
        flight_number = status.get('flightNumber')
        flight_status_public = status.get('flightStatusPublic')
        flight_date = status.get('flightScheduleDate')
        haul = status.get('haul')

        # Codeshare
        codeshare_code = None
        codeshare_name = None
        codeshare_date = None
        codeshare_number = None

        for codeshare in status.get('codeShareRelations', []):
            airline_info = codeshare.get('airline', {}) or {}

            codeshare_code = airline_info.get('code')
            codeshare_name = airline_info.get('name')
            codeshare_date = codeshare.get('flightScheduleDate')
            codeshare_number = codeshare.get('marketingFlightNumber')

            break   # Only keeps the first codeshare flights

        # Flight relations
        relations = status.get('flightRelations', {}) or {}

        onward = relations.get('onwardFlightData', {}) or {}
        previous = relations.get('previousFlightData', {}) or {}

        onward_code = onward.get('airlineCode')
        onward_number = onward.get('flightNumber')
        onward_schedule = onward.get('flightScheduleDate')

        previous_code = previous.get('airlineCode')
        previous_number = previous.get('flightNumber')
        previous_schedule = previous.get('flightScheduleDate')

        # Flight legs
        for leg in status.get('flightLegs', []):

            completion_percentage = leg.get('completionPercentage')
            time_difference = leg.get('departureDateTimeDifference')

            # Aircraft
            aircraft = leg.get('aircraft', {}) or {}

            config = aircraft.get('operationalConfiguration')
            owner_airline = aircraft.get('ownerAirlineName')
            registration = aircraft.get('registration')
            wifi = aircraft.get('wifiEnabled')
            aircraft_code = aircraft.get('typeCode')

            # Arrival
            arrival_airport = (
                leg.get('arrivalInformation', {})
                   .get('airport', {}) or {}
            )

            arrival_airport_code = arrival_airport.get('code')
            arrival_airport_name = arrival_airport.get('name')

            # Departure
            departure_airport = (
                leg.get('departureInformation', {})
                   .get('airport', {}) or {}
            )

            departure_airport_code = departure_airport.get('code')
            departure_airport_name = departure_airport.get('name')

            # Places
            places = (
                leg.get('departureInformation', {})
                   .get('airport', {})
                   .get('places', {}) or {}
            )

            gate_number = places.get('gateNumber')
            boarding_contact_type = places.get('boardingContactType')
            parking_position_type = places.get('parkingPositionType')
            pier_code = places.get('pierCode')
            terminal_code = places.get('terminalCode')

            # Scheduled departure
            times = (
                leg.get('departureInformation', {})
                   .get('times', {}) or {}
            )

            scheduled_time = times.get('scheduled')

            flight_status.append({
                "date": flight_date,
                "airline_code": airline_code,
                "airline_name": airline_name,
                "flight_number": flight_number,
                "flight_status_public": flight_status_public,

                "haul": haul,

                "codeshare_code": codeshare_code,
                "codeshare_name": codeshare_name,
                "codeshare_date": codeshare_date,
                "codeshare_number": codeshare_number,

                "onward_code": onward_code,
                "onward_number": onward_number,
                "onward_schedule": onward_schedule,

                "previous_code": previous_code,
                "previous_number": previous_number,
                "previous_schedule": previous_schedule,

                "completion_percentage": completion_percentage,
                "time_difference": time_difference,

                "arrival_airport_code": arrival_airport_code,
                "arrival_airport_name": arrival_airport_name,

                "departure_airport_code": departure_airport_code,
                "departure_airport_name": departure_airport_name,

                "configuration": config,
                "owner_airline": owner_airline,
                "registration": registration,
                "wifi": wifi,
                "aircraft_code": aircraft_code,

                "gate_number": gate_number,
                "boarding_contact_type": boarding_contact_type,
                "parking_position_type": parking_position_type,
                "pier_code": pier_code,
                "terminal_code": terminal_code,

                "scheduled_departure_time": scheduled_time
            })

    return pd.DataFrame(flight_status)


def parse_duration(iso_str):
    if not isinstance(iso_str, str):
        return None
    match = re.match(r"(-)?PT(?:(\d+)H)?(?:(\d+)M)?", iso_str)
    if not match:
        return None
    sign = -1 if match.group(1) else 1
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    return sign * (hours * 60 + minutes)

def clean_gate(val):
    if isinstance(val, list):
        return val[0] if len(val) > 0 else None
    return None 

def delay_label(minutes): 
    if minutes is None: 
        return None
    if minutes <= 15: 
        return 0
    else: 
        return 1

def clean_flights(flight_df):
    flight_df["time_difference"] = flight_df["time_difference"].apply(parse_duration)
    flight_df['haul'] = flight_df['haul'].apply(lambda x: 'UNKNOWN' if x == {} else x)
    flight_df['gate_number'] = flight_df['gate_number'].apply(clean_gate)
    flight_df = flight_df.drop(columns=['unnamed:0'], errors='ignore')
    flight_df = flight_df.drop(columns = ['codeshare_date'], errors='ignore')
    flight_df['delay_label'] = flight_df['time_difference'].apply(delay_label)
    flight_df = flight_df[flight_df["departure_airport_code"] == "AMS"].copy()
    flight_df['scheduled_departure_hour'] = (
        flight_df['scheduled_departure_time']
        .str.extract(r'T(\d{2}):')[0]
        .astype("Int64")  # nullable int — handles missing departure times safely
    )
    return flight_df

def load_data(flight_df): 
    flight_df.to_sql( 
        name='flights', 
        con=engine, 
        if_exists="append",  # adds new rows daily without wiping the table
        index=False
    )
    return flight_df


def main(): 
    date = dt.date(2026, 6, 24)
    data = extract_day(date) 
    flight_df = transform_flights(data) 
    flight_df = clean_flights(flight_df)
    flight_df = load_data(flight_df)
    print(flight_df.head())

if __name__ == "__main__":
    main()


