from datetime import date
import numpy as np
import streamlit as st

def get_birth_sign(dt):
    # Zodiac sign date ranges (month, day): (start, end)
    zodiac_dates = [
        ((1, 20), (2, 18), "Aquarius"),
        ((2, 19), (3, 20), "Pisces"),
        ((3, 21), (4, 19), "Aries"),
        ((4, 20), (5, 20), "Taurus"),
        ((5, 21), (6, 20), "Gemini"),
        ((6, 21), (7, 22), "Cancer"),
        ((7, 23), (8, 22), "Leo"),
        ((8, 23), (9, 22), "Virgo"),
        ((9, 23), (10, 22), "Libra"),
        ((10, 23), (11, 21), "Scorpio"),
        ((11, 22), (12, 21), "Sagittarius"),
        ((12, 22), (1, 19), "Capricorn"),
    ]
    for start, end, sign in zodiac_dates:
        start_month, start_day = start
        end_month, end_day = end
        if (dt.month == start_month and dt.day >= start_day) or \
           (dt.month == end_month and dt.day <= end_day) or \
           (start_month > end_month and ((dt.month == start_month and dt.day >= start_day) or (dt.month == end_month and dt.day <= end_day))):
            return sign
    return "Capricorn"  # fallback

def find_perfect_compat_dates(birth_date, years=25, tol=0.01):
    """
    Returns all birthdates within +/- `years` from `birth_date` that are at least 99% compatible
    for all cycles in Bio.T (Physical, Emotional, Intellectual).
    This version finds all dates where the absolute value of cos(pi * t.days / T) is close to 1
    for all cycles, i.e., at every integer multiple of each cycle, not just the LCM.
    Returns a list of tuples: (date, birthsign)
    """
    T = {'Physical': 23, 'Emotional': 28, 'Intellectual': 33}
    perfect_dates = set()
    # For each cycle, find all deltas where cos(pi * t.days / T) is close to ±1
    # That is, t.days / T is integer, but allow for small deviation

    min_delta = -years * 366
    max_delta = years * 366

    for cycle, value in T.items():
        k_start = (min_delta) // value
        k_end = (max_delta) // value
        for k in range(k_start, k_end + 1):
            delta = k * value
            other_ord = birth_date.toordinal() + delta
            try:
                other_date = date.fromordinal(other_ord)
                # Check all cycles for near-perfect compatibility (>=99%)
                all_perfect = True
                for c2, v2 in T.items():
                    form = np.cos(np.pi * delta / v2)
                    if not (abs(form) >= 0.99 - tol):
                        all_perfect = False
                        break
                if all_perfect:
                    perfect_dates.add(other_date)
            except ValueError:
                continue  # skip invalid dates

    perfect_dates = list(perfect_dates)
    perfect_dates.sort()
    # Add birth sign to each date
    perfect_dates_with_sign = [(dt, get_birth_sign(dt)) for dt in perfect_dates]
    return perfect_dates_with_sign

st.title('Perfect Compatibility Finder')

byear = st.number_input('Enter your birth year:', min_value=1900, max_value=date.today().year, value=2000)
bmonth = st.number_input('Enter your birth month:', min_value=1, max_value=12, value=1)
bday = st.number_input('Enter your birth day:', min_value=1, max_value=31, value=1)

if st.button('Find Perfect Compatibility Dates'):
    birth_date = date(byear, bmonth, bday)
    compat_dates = find_perfect_compat_dates(birth_date)
    st.dataframe(data=compat_dates)
    #for dt, sign in compat_dates:
    #    st.write(f"{dt}: {sign}")
