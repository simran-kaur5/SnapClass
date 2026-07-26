import streamlit as st

def subject_card(name, code, section, state, footer_callback=None):

    with st.container():

        st.markdown(
    f"""
    <h4 style="
        margin:0;
        color:#1f2937;
        font-weight:600;
    ">
        📘 {name}
    </h4>
    """,
    unsafe_allow_html=True,
)

        c1, c2 = st.columns(2)

        with c1:
            st.write(f"Code: {code}")

        with c2:
            st.write(f"Sec: {section}")

        st.divider()

        cols = st.columns(2)

        for i, item in enumerate(state):
            key, value = list(item.items())[0]

            with cols[i % 2]:
                st.metric(key, value)

            if i % 2 == 1 and i != len(state) - 1:
                cols = st.columns(2)

        if footer_callback:
            st.divider()
            footer_callback()