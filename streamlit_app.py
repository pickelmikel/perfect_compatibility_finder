import streamlit as st

st.session_state.disclaimer = ""

perfect_compat_finder = st.Page('perfect_compatibility_finder.py',
    title='Perfect Compatibility Finder')
biorhythm_checker = st.Page('biorhythm_checker.py',
    title='Biorhythm Compatibility Checker')
pg = st.navigation(
    pages=[perfect_compat_finder, biorhythm_checker],
    position='top',
    expanded=True)
pg.run()
