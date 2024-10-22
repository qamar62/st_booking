import streamlit as st
import datetime
import phonenumbers
from api import get_tours_from_api, check_availability_and_price, get_tour_details

# Fetch tours from API and create a dictionary for selectbox
tours = get_tours_from_api()
tour_options = {tour['name']: tour['id'] for tour in tours}

# Phone number validation function
def validate_phone_number(phone):
    try:
        parsed_number = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

# Dynamic content based on tour selection
tour_name = st.selectbox("Select Tour", options=list(tour_options.keys()))
tour_id = tour_options[tour_name]

# Fetch selected tour details
selected_tour = get_tour_details(tour_id)
if selected_tour:
    # Display the selected tour thumbnail and name dynamically
    st.image(selected_tour['thumbnail'], caption=selected_tour['name'], use_column_width=True)

# Tour booking form
with st.form(key='booking_form'):
    name = st.text_input("Full Name")
    pickup_location = st.text_input("Pick-up Location")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number (International Format)")

    today = datetime.date.today()
    next_year = today + datetime.timedelta(days=365)
    date = st.date_input("Select Tour Date", min_value=today, max_value=next_year)

    # Radio button for service type
    service_type = st.radio("Service Type", options=['Private', 'Sharing'])

    # Number of passengers
    num_adults = st.number_input("Number of Adults", min_value=0, value=1)
    num_children = st.number_input("Number of Children", min_value=0, value=0)
    num_infants = st.number_input("Number of Infants", min_value=0, value=0)

    # Submit button
    submit_button = st.form_submit_button(label='Book Tour')

# Form submission handling
if submit_button:
    if not all([name, pickup_location, email, phone_number]):
        st.error("Please fill all the fields.")
    elif not validate_phone_number(phone_number):
        st.error("Invalid phone number format.")
    else:
        price_details = check_availability_and_price(tour_id, date, service_type)
        if price_details is None:
            st.error("The selected tour is not available on this date.")
        else:
            # Calculate total price
            total_price = (
                price_details['adult_price'] * num_adults +
                price_details['child_price'] * num_children +
                price_details['infant_price'] * num_infants
            ) if service_type == 'Private' else price_details['base_Price'] * (num_adults + num_children)

            # Check and apply discount
            discount_start = datetime.datetime.strptime(price_details['discount_start_date'], "%Y-%m-%d").date()
            discount_end = datetime.datetime.strptime(price_details['discount_end_date'], "%Y-%m-%d").date()
            if discount_start <= date <= discount_end:
                discount = price_details.get('discount', 0)
                discount_multiplier = 1 - (discount / 100)
                total_price *= discount_multiplier

            st.success(f"Tour booked for {name}. Tour: {tour_name} on {date} with {service_type} service.")
            st.info(f"Total Price: ${total_price:.2f}")
            st.info(f"Pick-up Location: {pickup_location}")
            st.info(f"Confirmation will be sent to: {email}")
