import streamlit as st
import segno
import io


@st.dialog("Share Class Link")
def share_dailog_button(subject_name,subject_code):
    app_domain = "https://smart-snapclass.streamlit.app"
    join_url = f"{app_domain}/?join-code={subject_code}"


    qr = segno.make(join_url)

    out= io.BytesIO()

    qr.save(out,kind='png',scale=10,border=1)

    col1,col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Copy link")
        st.code(join_url,language="text")
        st.code(subject_code,language="text")
        st.info(f"Copy this link to share on Whatapp or Email")

    with col2:
        st.markdown("#### Scan to Join")
        st.image(out.getvalue(),use_container_width=True,caption="QRCODE for class joining")


