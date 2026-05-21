import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>🎯 Custom QR Generator</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Generate highly-customizable QR Codes instantly for websites, text payloads, contacts, or Wi-Fi configurations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_inputs, col_preview = st.columns([3, 2])
    
    with col_inputs:
        qr_data = st.text_input("Enter QR Payload Data (URL, text, phone, email, etc.)", "https://google.com")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fill_color = st.color_picker("QR Pattern Color", "#6366f1")
            box_size = st.slider("Module Pixel Size", min_value=5, max_value=25, value=10)
        with col_c2:
            back_color = st.color_picker("QR Background Color", "#ffffff")
            border_size = st.slider("Border Margin (Blocks)", min_value=1, max_value=10, value=4)
            
        error_correction_options = {
            "Low (Approx 7% recovery)": qrcode.constants.ERROR_CORRECT_L,
            "Medium (Approx 15% recovery)": qrcode.constants.ERROR_CORRECT_M,
            "Quartile (Approx 25% recovery)": qrcode.constants.ERROR_CORRECT_Q,
            "High (Approx 30% recovery)": qrcode.constants.ERROR_CORRECT_H
        }
        
        ecc_selection = st.selectbox("Error Correction Capability", list(error_correction_options.keys()))
        ecc_level = error_correction_options[ecc_selection]

    with col_preview:
        if qr_data.strip():
            # Setup qrcode inst
            qr = qrcode.QRCode(
                version=None,
                error_correction=ecc_level,
                box_size=box_size,
                border=border_size,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Generate PIL Image
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Save to BytesIO for Streamlit display and downloading
            buf = BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.image(byte_im, width=280, caption="Generated QR Code")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.download_button(
                label="Download QR Code (PNG)",
                data=byte_im,
                file_name="nexus_qrcode.png",
                mime="image/png"
            )
        else:
            st.info("Input a payload on the left to view the generated QR Code.")
