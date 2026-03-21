from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
import streamlit as st


def check_state():
    if 'advanced' not in st.session_state:
        st.session_state.advanced = False
    if 'Eval' not in st.session_state:
        st.session_state.Eval = 0.8
    if 'Ival' not in st.session_state:
        st.session_state.Eval = 0.8
    if 'Pval' not in st.session_state:
        st.session_state.Eval = 0.8

# Init session_state variables 
check_state()

def set_advanced():
    if advanced_options.open == False:
        st.session_state.advanced = True
    elif advanced_options.open == True:
        st.session_state.advanced = False

def set_default_values():
    st.session_state.Eval = 0.8
    st.session_state.Ival = 0.8
    st.session_state.Pval = 0.8

def biorhythm_high_res(birth_date, target_date):
    # Calculate age in days
    delta = (target_date - birth_date).days

    # Calculate biorhythm phases with higher accuracy
    physical = (delta % 23.5) / 23.5  # Updated cycle length
    emotional = (delta % 28.8) / 28.8  # Updated cycle length
    intellectual = (delta % 33.4) / 33.4  # Updated cycle length
    
    return physical, emotional, intellectual

def biorhythm(birth_date, target_date):
    # Calculate age in days
    delta = (target_date - birth_date).days
    
    # Calculate biorhythm phases
    physical = (delta % 23) / 23
    emotional = (delta % 28) / 28
    intellectual = (delta % 33) / 33
    
    return physical, emotional, intellectual

@st.cache_data
def bio_compat(your_birth, other_birth):
    T = {'Physical':23, 'Emotional':28, 'Intellectual':33}
    t = your_birth - other_birth
    cycle_data = {}
    for cycle, value in T.items():
        form = np.cos(np.pi * t.days / value)
        cycle_data[cycle] = abs(form)
        form_final = form * 100
        #print(f"Cycle {cycle}: Percent Compatibility {abs(form_final):.2f}")
    cycle_data['Overall'] = np.array([*cycle_data.values()]).mean()
    return cycle_data

def compatibility_score(physical, emotional, intellectual):
    # Simple scoring system where 1 is strong compatibility
    return (1 - abs(physical-0.5)) + (1 - abs(emotional-0.5)) + (1 - abs(intellectual-0.5))

#print(f"Biorhythm Compatibility Score: {score}")

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
                    if not (abs(form) >= .8 - tol):
                        all_perfect = False
                        break
                if all_perfect:
                    if other_date == birth_date:
                        pass
                    else:
                        #physical, emotional, intellectual = biorhythm(birth_date, other_date)
                        score =  bio_compat(birth_date,other_date)[1]#compatibility_score(physical, emotional, intellectual)
                        perfect_dates.add((other_date, get_birth_sign(other_date), score))
            except ValueError:
                continue  # skip invalid dates
    perfect_dates = list(perfect_dates)
    # Sort by compatibility score (highest first)
    perfect_dates.sort(key=lambda x: x[2],reverse=True)
    return perfect_dates

@st.cache_data
def find_good_compat_dates(birth_date, years=4, threshold=0.8, thresholds=None):
    """
    birth_date:     date()
    years:         int 
    threshold:     float
    thresholds:    dict()
    """
    
    T = {'Physical': 23, 'Emotional': 28, 'Intellectual': 33}
    good_dates = []
    min_delta = -years * 366
    max_delta = years * 366

    # Determine thresholds for each cycle
    if st.session_state.advanced is True and thresholds is not None:
        # Use manual thresholds if advanced mode is True and thresholds provided
        cycle_thresholds = {
            'Physical': thresholds.get('Physical', threshold),
            'Emotional': thresholds.get('Emotional', threshold),
            'Intellectual': thresholds.get('Intellectual', threshold)
        }
    else:
        # Use the same threshold for all cycles
        cycle_thresholds = {
            'Physical': threshold,
            'Emotional': threshold,
            'Intellectual': threshold
        }

    for delta in range(min_delta, max_delta + 1):
        other_ord = birth_date.toordinal() + delta
        try:
            other_date = date.fromordinal(other_ord)
            compat = [abs(np.cos(np.pi * delta / period)) for period in T.values()]
            # Derivatives for both people
            dir1 = [-np.pi / period * np.sin(np.pi * delta / period) for period in T.values()]
            dir2 = [-np.pi / period * np.sin(0) for period in T.values()]  # reference person at t=0

            # Check value threshold and same direction
            compat_pass = all(
                c >= cycle_thresholds[cycle]
                for c, cycle in zip(compat, T.keys())
            )
            direction_pass = all(d1 * d2 >= 0 for d1, d2 in zip(dir1, dir2))

            if compat_pass and direction_pass:
                good_dates.append((
                    other_date,
                    np.mean(compat) * 100,
                    *compat,
                    get_birth_sign(other_date)
                ))
                good_dates.sort(key=lambda x: x[1], reverse=True)
        except ValueError:
            continue
    return good_dates


def show_details():
    try:
        st.write(df.iloc[a.get('selection')['rows'][0]][0])
        st.write(birth_date)
    except IndexError:
        pass


## -- MAIN DISPLAY CODE -- ##
st.info(st.session_state.disclaimer)
st.title('Perfect Compatibility Finder')

## User Input widgets ##
birth_date = st.date_input('Select your birthdate',
                           #value=date(2000,1,1),
                           min_value=date(1900,1,1),
                           max_value=date.today(),
                           key='birth_date',
                           format='YYYY-MM-DD')

nyears = st.number_input('How many years difference to display:',
                         min_value=1,
                         max_value=100,
                         value=4,
                         key='nyears')

## Advanced expander section ##
with st.expander('Advanced Options', on_change=set_advanced) as advanced_options:
    st.write('Select Cycle Thresholds')
    E = st.slider('Emotional',
                  value=0.8,
                  format='percent',
                  min_value=0.0,
                  max_value=1.0,
                  step=0.01,
                  key='Eval')
    I = st.slider('Intellectual',
                  value=0.8,
                  format='percent',
                  min_value=0.0,
                  max_value=1.0,
                  step=0.01,
                  key='Ival')
    P = st.slider('Physical',
                  value=0.8,
                  format='percent',
                  min_value=0.0,
                  max_value=1.0,
                  step=0.01,
                  key='Pval')
    st.button('Reset', on_click=set_default_values)
    
st.session_state.advanced_values = {'Emotional':E,
                                    'Intellectual':I,
                                    'Physical':P}
 
# Testing displaying advanced state and values
#advanced_options.open
#st.session_state.advanced
#st.session_state.advanced_values

## DataFrame setup ##
columns = ['Compatible Dates',
           'Overall Compatibility',
           'Physical',
           'Emotional',
           'Intellectual',
           'Birth Sign'
           ]
good_order = ['Compatible Dates',
           'Overall Compatibility',
           'Emotional',
           'Intellectual',
           'Physical',
           'Birth Sign'
           ]
# Checks if advanced options expander is open or closed
good_compat_dates = find_good_compat_dates(
        birth_date,
        years=nyears,
        thresholds=st.session_state.advanced_values)

gdf = pd.DataFrame(good_compat_dates, columns=columns)
gdf = gdf.astype({'Birth Sign':'category'})
a_col_config = {
    'Physical':st.column_config.NumberColumn(format='percent'),
    'Emotional':st.column_config.NumberColumn(format='percent'),
    'Intellectual':st.column_config.NumberColumn(format='percent')#,
    #'Overall Compatibility':st.column_config.NumberColumn(format='percent')
    }



# Write total number of matches from current dataframe
st.write(f'Found {gdf.shape[0]} matches')

## DataFrame display ##
a = st.dataframe(gdf[good_order],
             selection_mode='single-row',
             column_config=a_col_config,
             on_select='rerun')


# Static Table
#st.table(gdf.set_index(columns[0]).style.format({columns[2]: '{:.2f}'}))

## Bar chart setup and display ##
try:
    #st.write()
    other_date = gdf.iloc[a.get('selection')['rows'][0]].iloc[0]
    b = bio_compat(birth_date, other_date)
    bdf = pd.DataFrame([b],columns=['Physical','Emotional','Intellectual','Overall'])
    # Setting index to display on static table of selected match
    #bdf.index = ['Compatibility on Day of Birth']
    bdf.index = [other_date]
    bdf.index.name = 'Result Date'
    # To get percentage
    bdf = bdf.mul(100)
    #bvals = np.array([x for x in b.values()])
    bdfd = bdf.copy()
    bdfd['Overall'] = bdfd.mean(axis=1, numeric_only=True)
    order = ['Emotional', 'Intellectual', 'Physical', 'Overall']
    
    st.table(bdfd[order])
    # Blanking index because it shows funny on the screen
    bdf.index = ['']
    st.bar_chart(bdf, sort=False,
                 stack=False,
                 x=None,
                 y_label='Percent Compatible',
                 x_label='Compatibility on Day of Birth',
                 horizontal=False,
                 color=['blue','green','red', 'violet'],
                 height='content')
    #st.table(b)
except IndexError:
    pass

st.write('*Dates are in YEAR-MONTH-DAY format')
