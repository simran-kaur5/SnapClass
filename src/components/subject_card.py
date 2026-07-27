import streamlit as st


def subject_card(name, code, section, state, footer_callback=None):

    stats = {}

    for item in state:
        key, value = list(item.items())[0]
        stats[key] = value


    html_code = f"""
<div style="
background-color:white;
padding:20px;
border-radius:16px;
margin-bottom:20px;
color:#111827;
">

<h3 style="color:#1f2937;">
{name}
</h3>

<p>Code: {code}</p>

<p>Sec: {section}</p>

<hr>

<div style="
display:flex;
justify-content:space-around;
text-align:center;
">

<div>
<b>Total</b>
<br>
{stats.get("Total",0)}
</div>

<div>
<b>Attended</b>
<br>
{stats.get("Attended",0)}
</div>

<div>
<b>Absent</b>
<br>
{stats.get("Absent",0)}
</div>

<div>
<b>Attendance</b>
<br>
{stats.get("Attendance","0%")}
</div>

</div>

</div>
"""


    st.markdown(
        html_code,
        unsafe_allow_html=True
    )


    if footer_callback:
        footer_callback()

