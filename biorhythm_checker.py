import streamlit as st

st.title('Biorhythm Checker')
st.info('Coming soon...until then push the buttons')

def have_ball():
    st.balloons()

def have_snow():
    st.snow()
    
st.button('Click me!', on_click=have_ball, key='ball')
st.button('Click me!', on_click=have_snow, key='snow')
