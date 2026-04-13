import numpy as np
from datetime import date, timedelta
import plotly.graph_objects as go
import streamlit as st

def check_state():
    if 'T' not in st.session_state:
        st.session_state.T = {'Emotional':28,
                              'Intellectual':33,
                              'Physical':23}
    
    #if 'base_date' not in st.session_state:
        #st.session_state.base_date = date.today()
    #if "birth_date" not in st.session_state:
    #   st.session_state.birth_date = date.today() 

check_state()
#st.write(st.session_state.your_birthdate)
@st.cache_data
def bio_compat(your_birth, other_birth):
    T = st.session_state.T
    t = your_birth - other_birth
    cycle_data = {}
    for cycle, value in T.items():
        form = np.cos(np.pi * t.days / value)
        cycle_data[cycle] = abs(form)
        form_final = form * 100
        #st.write(f"{cycle} Cycle Percent Compatibility: {abs(form_final):.2f}")
    cycle_data['Overall'] = round(np.array([*cycle_data.values()]).mean() * 100,3)
    return cycle_data

@st.cache_data
def day_compat(your_birth, other_birth, base_date):
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

def update_radar():
    fig, key = radar_display(st.session_state.base_date)
    st.plotly_chart(fig, width='stretch', key=key)

def update_base_slider():
    pass

def reset_to_today():
    st.session_state.base_date = date.today()

def radar_display(start_date):
    ## Chart Config ##
    #st.write(compat_dict)#test display

    # Generate a list of dates for the slider and animation
    num_days = 91
    before_dates = [start_date - timedelta(days=i) for i in range(num_days)]
    after_dates = [start_date + timedelta(days=i) for i in range(num_days+1)]  # include today
    before_dates.reverse()
    dates = before_dates + after_dates  # chronological order
    categories = ['Emotional', 'Intellectual', 'Physical', 'Overall']

    # Precompute all scores for all dates for efficiency
    all_scores = []
    for d in dates:
        scores = day_compat(st.session_state.your_birthdate,
                            st.session_state.other_birthdate, d)[1]
        values = [scores[cat] * 100 for cat in categories] + [scores['Emotional']*100]
        all_scores.append(values)

    # Initial values for the current base_date
    if start_date in dates:
        init_idx = dates.index(start_date)
    
    #if st.session_state.base_date in dates:
    #    init_idx = dates.index(st.session_state.base_date)
    #else:st.write("🔎 AFTER widget :", dict(st.session_state)) 
    #    init_idx = len(dates)//2  # fallback to today

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
    today_str = str(start_date)
    if today_str in [str(d) for d in dates]:
        slider_init_idx = [str(d) for d in dates].index(today_str)
    else:
        slider_init_idx = len(dates)//2



    fig = go.Figure(
        data=[
            go.Scatterpolar(r=all_scores[slider_init_idx],
                theta=categories + [categories[0]],
                fill='toself'
                #text=text_labels,
                #textposition='top center',
                #mode='lines+markers+text'
            )
        ],
        frames=frames
    )



    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
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
        title=f'Biorhythm Compatibility Radar for Previous and Future 90 days from {start_date}',
        template='plotly_dark'
    )
    #st.write(all_scores)
    key = np.random.rand()    
    return fig, key
    
    

## -- MAIN DISPLAY CODE -- ##
st.info(st.session_state.disclaimer)
st.title('Biorhythm Compatibility Checker')


# Birthday selection for two individuals
#st.write("🔎 BEFORE widget:", dict(st.session_state))
st.date_input('Select your birthdate',
                           value=st.session_state.bd,
                           min_value=date(1900,1,1),
                           max_value=date.today(),
                           key='your_birthdate',
                           format='YYYY-MM-DD')
#st.write("🔎 AFTER widget :", dict(st.session_state)) 
st.date_input('Select other birthdate',
                           value=st.session_state.ob,
                           min_value=date(1900,1,1),
                           max_value=date.today(),
                           key='other_birthdate',
                           format='YYYY-MM-DD')
st.session_state.ob = st.session_state.other_birthdate
# Sets lower date limit to earlier date
#limit_date = set_limit_date(st.session_state.your_birthdate,
                            #st.session_state.other_birthdate)#may be removed

# Shows your overall average compatibility for each cycle
st.write('Compatibility at Birth')
bio_compat_result = bio_compat(st.session_state.your_birthdate,
                               st.session_state.other_birthdate)
#radar_display(False,None)

st.markdown(
        f":blue-badge[Emotional {round(bio_compat_result.get('Emotional')*100,2)}%]\
        :green-badge[Intellectual {round(bio_compat_result.get('Intellectual')*100,2)}%]\
        :red-badge[Physical {round(bio_compat_result.get('Physical')*100,2)}%]\
        :yellow-badge[Overall {round(bio_compat_result.get('Overall'),2)}%]",
        unsafe_allow_html=True
    )


st.divider()

# Sets max and min values for chart display
chart_min_value=date.today() - timedelta(days=190)
chart_max_value=date.today() + timedelta(days=90)

# Check specific date compatibility
#st.session_state.bio_check_date = st.expander(label='Expand to see \
#compatibility for a specific date', expanded=False, on_change='rerun')
#with st.session_state.bio_check_date:
st.date_input('Compatibility Date',
          #min_value=chart_min_value,
          #max_value=chart_max_value,
          format='YYYY-MM-DD',
          on_change=update_radar,
          key='base_date')
phase_dict, compat_dict = day_compat(st.session_state.your_birthdate,
                                        st.session_state.other_birthdate,
                                        st.session_state.base_date)

st.markdown(
        f":blue-badge[Emotional {round(compat_dict.get('Emotional')*100,2)}%]\
        :green-badge[Intellectual {round(compat_dict.get('Intellectual')*100,2)}%]\
        :red-badge[Physical {round(compat_dict.get('Physical')*100,2)}%]\
        :yellow-badge[Overall {round(compat_dict.get('Overall')*100,2)}%]",
        unsafe_allow_html=True
    )

st.button(label='Reset to Today',
          key='reset_to_today',
          on_click=reset_to_today
          )
    
    #st.write(f'{cycle} Cycle:  {value*100:.2f} %')
    #st.write(f'{cycle} Cycle: phase_difference: {phase_diff:.3f}, compatiblity_score: {compat:.3f}')
update_radar()
    
  

#st.write(    "🔎 session_state:",    {k: str(v) for k, v in st.session_state.items()})
