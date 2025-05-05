from src.read_data import read_availability_data

def lower_availability(park_name, target_date = None):
    planned_availability, actual_availability = read_availability_data(park_name, target_date, json = False)
    suspect_hours = []
    for planned, actual, hour in zip(planned_availability, actual_availability, range(24)):
        if planned!=actual:
            suspect_hours.append(hour)
    return suspect_hours