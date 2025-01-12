from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

import re

from itsdangerous import URLSafeTimedSerializer

from datetime import datetime, time

from fastapi import Request
import os

from dotenv import load_dotenv


load_dotenv()


# Vars

latitude_regex = r"^(\+|-)?(90(\.0+)?|[1-8]?\d(\.\d+)?)$"
longitude_regex = r"^(\+|-)?(180(\.0+)?|((1[0-7]\d)|(\d{1,2}))(\.\d+)?)$"
time_regex = r"^(?:[01]?[0-9]|2[0-3]):[0-5]?[0-9](?::[0-5]?[0-9])?$"
link_regex = r"^https:\/\/(www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(\/[^\s]*)?$"

event_types = ["theatre", "concert", "exhibition", "book_fare",
        "seminar","festival","dance"]

venue_types = ["museum", "theatre", "library", "cinema",
        "comedy_club","monument","cultural_space"]

serializer = URLSafeTimedSerializer(
    secret_key=os.getenv("SECRET"), salt="email-configuration"
)

# Functions

def get_country_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        address = location.raw['address']

        country = address.get('country')
        city = address.get('city') or address.get('town') or address.get('village')

        return country, city
    except GeocoderTimedOut:
        return None
    

def is_past_date(input_date_str):
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        input_date = datetime.strptime(input_date_str, date_format)
    except ValueError:
        return True
    
    # Get the current date and time
    current_date = datetime.now()
    
    # Compare dates
    if input_date >= current_date:
        return False
    else:
        return True


def remove_domain(email):
    # Split the email at the '@' symbol and take the first part
    return email.split("@")[0]


def is_secure_password(password):
    # Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number, and one special character
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."

    return True, "Password is secure."


def create_url_safe_token(data: dict):
    
    token = serializer.dumps(data)

    return token


def get_redis(request: Request):
    return request.app.state.redis
