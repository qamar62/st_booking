import streamlit as st
import requests
from datetime import datetime

# Constants
TEST_TOKEN_URL = st.secerts['TEST_TOKEN_URL']
TEST_API_URL = st.secerts['TEST_API_URL']
USERNAME = st.secerts['UERNAME']
PASSWORD = st.secerts['PASSWORD']


def get_jwt_token():
    """
    Obtain JWT token using username and password.
    """
    payload = {'username': USERNAME, 'password': PASSWORD}
    response = requests.post(TEST_TOKEN_URL, data=payload)

    if response.status_code == 200:
        return response.json().get('access')
    else:
        st.error("Failed to get JWT token.")
        return None


def make_api_request(url, headers):
    """
    Generic function to make GET requests with error handling.
    """
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def get_tours_from_api():
    """
    Fetch tours from the API using JWT token for authentication.
    """
    token = get_jwt_token()
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        return make_api_request(TEST_API_URL, headers)
    return []


def get_tour_details(tour_id):
    """
    Get specific tour details by ID.
    """
    tours = get_tours_from_api()
    return next((tour for tour in tours if tour['id'] == tour_id), None)


def check_availability_and_price(tour_id, selected_date, service_type):
    """
    Check if the tour is available on the selected date and calculate the price based on service type and discount.
    """
    try:
        tour_details = get_tour_details(tour_id)
        if not tour_details:
            return None

        # Check availability
        for available in tour_details['availability_tours']:
            exclude_dates = [exclude['date'] for exclude in available['exclude_dates']]
            if selected_date.strftime("%Y-%m-%d") in exclude_dates:
                return None  # Not available on this date

        # Get price details for the selected service type
        price = next((p for p in tour_details['price'] if p['service_type'] == service_type), None)
        if price:
            discount_start = datetime.strptime(price['discount_start_date'], "%Y-%m-%d").date()
            discount_end = datetime.strptime(price['discount_end_date'], "%Y-%m-%d").date()

            # Apply discount if valid
            if discount_start <= selected_date <= discount_end:
                discount_percent = price.get('discount', 0)
                discount_multiplier = 1 - (discount_percent / 100)

                price['adult_price'] *= discount_multiplier
                price['child_price'] *= discount_multiplier
                price['infant_price'] *= discount_multiplier

            return price  # Return price with or without discount
    except Exception as e:
        st.error(f"Error while checking availability and price: {e}")
    return None
