import streamlit as st

# --- PAGE SETUP ---
Home = st.Page(
    "Views/Home.py",
    title="Home",
    icon=":material/home:",
    default=True,
)
project_1_page = st.Page(
    "Views/about_us.py",
    title="About Us",
    icon=":material/groups:",
)
project_2_page = st.Page(
    "Views/System.py",
    title="Photo Upload",
    icon=":material/smart_toy:",
)
project_3_page = st.Page(
    "Views/Video.py",
    title="Video and Real Time",
    icon=":material/smart_toy:",
)
# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Main": [Home, project_1_page],
        "Projects": [project_2_page, project_3_page],
    }
)


# --- SHARED ON ALL PAGES ---
st.logo("assets/Terminus logo.png")
st.sidebar.markdown("Made with ❤️ by [Mushili](https://mubangamushili.p@gmail.com)")


# --- RUN NAVIGATION ---
pg.run()
