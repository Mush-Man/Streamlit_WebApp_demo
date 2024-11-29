import streamlit as st


# Run the main banner display
def run():

    st.markdown(
        """
        <style>
        .banner-text {
            font-size: 4rem; /* Adjust font size as needed */
            font-weight: bold;
            color: white;
            text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.7);
            text-align: center;
        }
        </style>
        <div class="full-screen-banner">
            <div class="banner-text">Welcome to The Next Tomorrow</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# About the AI Model Section
def about_model():
    st.markdown(
        """
        <style>
        .about-section {
            background-color: #002b36;
            border-color: white;
            padding: 50px;
            text-align: center;
            border-radius: 10px;
        }
        </style>
        <div class='about-section'>
            <h2>About Terminus AI</h2>
            <p>Terminus AI is an advanced object detection model designed to revolutionize infrastructure management.
            With the ability to detect structural defects such as cracks, potholes, spalling, and rebar exposure, Terminus AI empowers engineers and organizations with actionable insights for sustainable development.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Features Section
def features():
    st.markdown(
        """
        <style>
        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
        }
        .feature-box {
            background-color: #002b36;
            border: 1px solid #F5F5F5;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            text-color: #002b36;
            transition: transform 0.2s;
        }
        .feature-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        .feature-icon {
            font-size: 40px;
            color: #4CAF50;
            margin-bottom: 15px;
        }
        </style>
        <h2>Features</h2>
        <div class="features-grid">
            <div class="feature-box">
                <div class="feature-icon">🔍</div>
                <h3>Real-Time Detection</h3>
                <p>Analyze structural defects in real-time using live camera inputs.</p>
            </div>
            <div class="feature-box">
                <div class="feature-icon">📊</div>
                <h3>Detailed Reports</h3>
                <p>Generate comprehensive reports for informed decision-making.</p>
            </div>
            <div class="feature-box">
                <div class="feature-icon">🌍</div>
                <h3>Global Impact</h3>
                <p>Enhancing infrastructure management for a better tomorrow.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Footer Section
def footer():
    st.markdown(
        """
        <style>
        .footer {
            background-color: #222;
            color: white;
            text-align: center;
            padding: 10px;
            margin-top: 50px;
            font-size: 14px;
        }
        </style>
        <div class='footer'>
            <p>&copy; 2024 Terminus AI. All rights reserved.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


run()
st.markdown("<hr>", unsafe_allow_html=True)
about_model()
st.markdown("<hr>", unsafe_allow_html=True)
features()
footer()
