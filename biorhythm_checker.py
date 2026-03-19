from datetime import date, timedelta
import numpy as np
import streamlit as st

def check_state():
    if 'T' not in st.session_state:
        st.session_state.T = {'Emotional':28,
                              'Intellectual':33,
                              'Physical':23}
check_state()

@st.cache_data
def bio_compat(your_birth, other_birth):
    T = st.session_state.T
    t = your_birth - other_birth
    cycle_data = {}
    for cycle, value in T.items():
        form = np.cos(np.pi * t.days / value)
        cycle_data[cycle] = abs(form)
        form_final = form * 100
        st.write(f"{cycle} Cycle Percent Compatibility: {abs(form_final):.2f}")
    #return cycle_data, np.array([*cycle_data.values()]).mean() * 100
    cycle_mean = round(np.array([*cycle_data.values()]).mean() * 100,2)
    st.write(f'Overall Compatibility: {cycle_mean} Percent')


def day_compat(your_birth, other_birth, base_date=date.today()):
    T = st.session_state.T
    t1 = (base_date - your_birth).days
    t2 = (base_date - other_birth).days
    st.write(f'Compatibility for {base_date}')
    for cycle, value in T.items():
        val1 = np.sin(2 * np.pi * t1 / value)
        val2 = np.sin(2 * np.pi * t2 / value)
        phase_diff = (val1 - val2) / 2
        compat = 1 - abs(val1 - val2) / 2
        st.write(f'{cycle} Cycle: phase_difference: {phase_diff:.3f}, compatiblity_score: {compat:.3f}')


## -- MAIN DISPLAY CODE -- ##
st.info(st.session_state.disclaimer)
st.title('Biorhythm Compatibility Checker')

birth_date = st.date_input('Select your birthdate',
                           #value=date(2000,1,1),
                           min_value=date(1900,1,1),
                           max_value=date.today(),
                           key='your_birhdate',
                           format='YYYY-MM-DD')
other_date = st.date_input('Select other birthdate',
                           #value=date(2000,1,1),
                           min_value=date(1900,1,1),
                           max_value=date.today(),
                           key='other_birthdate',
                           format='YYYY-MM-DD')
if birth_date > other_date:
    limit_date = other_date
elif birth_date < other_date:
    limit_date = birth_date
else:
    limit_date = date(1900,1,1)

st.write('Compatibility at Birth')
bio_compat(birth_date,other_date)
st.divider()
base_date = st.date_input('Compatibility Date',
          min_value=limit_date,
          max_value=date.today(),
          format='YYYY-MM-DD',
          key='base_date')

base_date_slider = """st.slider('Compatibility Date',
          value=base_date,
          min_value=limit_date,
          max_value=date.today(),
          format='YYYY-MM-DD',
          step=timedelta(days=1),
          key='base_date_slider',
          disabled=False)"""

day_compat(birth_date,other_date,base_date)
