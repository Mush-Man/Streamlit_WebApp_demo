import streamlit as st

from forms.contact import contact_form


@st.dialog("Contact Me")
def show_contact_form():
    contact_form()


# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/MALANGE LOGO2.png", width=230)

with col2:
    st.title("Mélange", anchor=False)
    st.write(
        "A rising startup aimed at creating new technologies to address some of the nation's growing needs."
    )
    if st.button("✉️ Contact Us"):
        show_contact_form()


# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Who We Are", anchor=False)
st.write(
    """
Carl Sagan once said, “Human beings are like butterflies that flutter for a day and think it’s 
forever.” It’s true that, compared to the lifespan of the universe, our lives begin and end in the 
blink of an eye. Yet, the impact we make can transcend time. This desire to leave a lasting mark 
is what led to the inception of Magneto, a startup in the early stages of its development, driven 
by four former university students who are passionate about creating innovative solutions to 
address todays challenges.

The world is progressing rapidly, with the fourth industrial revolution currently underway. 
New technologies such as Artificial Intelligence, robotics, space travel, electric vehicles, smart 
agriculture, 5G, and maglev trains are being introduced to improve lives. Meanwhile, Zambia 
seems to be lagging behind, facing challenges like power outages, poor crop yields, diesel powered trains, 
and limited internet access, among others. At this rate, when will we catch up with the rest of the world
    
As Magneto, we envision Zambia advancing at the same pace as 
the rest of the world. Our current slogan, “The Next Tomorrow,” reflects our ambition to bring 
ground breaking technological advancements to the country, we are currently working on three 
projects to help address some of the challenges being faced.

"""
)

# --- SKILLS ---
st.write("\n")
st.subheader("OUR TEAM", anchor=False)
st.write(
    """
MUSHILI PRIDE MUBANGA - CIVIL ENGINEER

PETER MWANAMWENGE - ELECTRICAL AND ELECTRONICS ENGINEER

    """
)
