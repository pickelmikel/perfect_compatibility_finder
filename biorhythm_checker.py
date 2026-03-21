import numpy as np
from datetime import date, timedelta
import plotly.graph_objects as go
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

@st.cache_data
def day_compat(your_birth, other_birth, base_date=date.today()):
    T = st.session_state.T
    t1 = (base_date - your_birth).days
    t2 = (base_date - other_birth).days
    phase_dict = {}
    compat_dict = {}
    
    for cycle, value in T.items():
        val1 = np.sin(2 * np.pi * t1 / value)
        val2 = np.sin(2 * np.pi * t2 / value)
        phase_diff = (val1 - val2) / 2
        compat = 1 - abs(val1 - val2) / 2
        
        phase_dict[cycle] = phase_diff
        compat_dict[cycle] = compat
    compat_dict['Overall'] = np.array([*compat_dict.values()]).mean()
    return phase_dict, compat_dict

def set_limit_date(birth_date,other_date):
    if birth_date > other_date:
        limit_date = other_date
    elif birth_date < other_date:
        limit_date = birth_date
    else:
        limit_date = date(1900,1,1)
    return limit_date

def update_base_date():
    pass
def update_base_slider():
    pass

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
# Sets lower date limit to earlier date
limit_date = set_limit_date(birth_date,other_date)

st.write('Compatibility at Birth')
bio_compat(birth_date,other_date)
st.divider()

chart_min_value=date.today() - timedelta(days=90)
chart_max_value=date.today() + timedelta(days=90)

st.write('Select date below to see your compatibility on that date')
base_date = st.date_input('Compatibility Date',
          min_value=chart_min_value,
          max_value=chart_max_value,
          format='YYYY-MM-DD',
          key='base_date')

base_date_slider = """st.slider('Compatibility Date',
          value=date.today(),
          min_value=chart_min_value,
          max_value=chart_max_value,
          format='YYYY-MM-DD',
          step=timedelta(days=1),
          key='base_date_slider',
          disabled=False)"""


phase_dict, compat_dict = day_compat(birth_date,other_date,base_date)
#st.write(f'Compatibility for: {base_date}')
for cycle,value in compat_dict.items():
    st.write(f'{cycle} Cycle:  {value*100:.2f} %')
    #st.write(f'{cycle} Cycle: phase_difference: {phase_diff:.3f}, compatiblity_score: {compat:.3f}')

## Chart Config ##
#st.write(compat_dict)

# Generate a list of dates for the slider and animation
start_date = date.today()
num_days = 91
before_dates = [start_date - timedelta(days=i) for i in range(num_days)]
after_dates = [start_date + timedelta(days=i) for i in range(num_days+1)]  # include today
before_dates.reverse()
dates = before_dates + after_dates  # chronological order

categories = ['Emotional', 'Intellectual', 'Physical', 'Overall']

# Precompute all scores for all dates for efficiency
all_scores = []
for d in dates:
    scores = day_compat(birth_date, other_date, d)[1]
    values = [scores[cat] for cat in categories] + [scores['Emotional']]
    all_scores.append(values)

# Initial values for the current base_date
if base_date in dates:
    init_idx = dates.index(base_date)
else:
    init_idx = len(dates)//2  # fallback to today

init_values = all_scores[init_idx]

# Create frames for animation
frames = [
    go.Frame(
        data=[go.Scatterpolar(r=all_scores[i], theta=categories + [categories[0]], fill='toself')],
        name=str(dates[i])
    )
    for i in range(len(dates))
]

# Create steps for the slider
steps = []
for i, d in enumerate(dates):
    step = dict(
        method="animate",
        args=[
            [str(d)],
            {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}
        ],
        label=str(d)
    )
    steps.append(step)

# Set the initial slider position to today's date (middle of the range)
today_str = str(date.today())
if today_str in [str(d) for d in dates]:
    slider_init_idx = [str(d) for d in dates].index(today_str)
else:
    slider_init_idx = len(dates)//2



fig = go.Figure(
    data=[
        go.Scatterpolar(r=all_scores[slider_init_idx],
            theta=categories + [categories[0]],
            fill='toself',
            #text=text_labels,
            #textposition='top center',
            #mode='lines+markers+text'
        )
    ],
    frames=frames
)



fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        buttons=[
            dict(label="Play", method="animate", args=[None, {"frame": {"duration": 200, "redraw": True}, "fromcurrent": True}]),
            dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
        ],
        x=0.1, y=1.15
    )],
    sliders=[dict(
        steps=steps,
        transition=dict(duration=0),
        x=0.1, y=0, len=0.8,
        currentvalue=dict(prefix="Date: ", visible=True, xanchor='right'),
        active=slider_init_idx  # This sets the initial slider position to today
    )],
    title=f'Biorhythm Compatibility Radar Chart (Use slider to change dates. You can spin the Radar Wheel)',
    template='plotly_dark'
)
#st.write(all_scores)

st.plotly_chart(fig, use_container_width=True)
