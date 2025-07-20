# python -m pip install streamlit boto3 pandas openpyxl Pillow
# python -m pip install streamlit
# streamlit --version
# aws configure
# python -m streamlit run app.py
#https://<your-studio-domain>.studio.<region>.sagemaker.aws/jupyter/default/proxy/8501/
# "p1.jpg", "p2.jpg", "p3.jpg", "p4.jpg", "p5.jpg", "p7.jpg", "p7.jpg", "p8.jpg"
import streamlit as st
import pandas as pd
import boto3
import uuid
import base64

from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from datetime import datetime, timedelta
from PIL import UnidentifiedImageError

# Set page config
st.set_page_config(page_title="Olive Garden Restaurants", layout="wide")

# Define the olive theme CSS and footer HTML
olive_theme_css = """
<style>
body {
    background-color: #006400;
    color: white;
}
.sidebar .sidebar-content {
    background-color: #8B0000;
    color: white;
}
footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #556B2F;
    color: white;
    text-align: center;    
    font-size: 14px;
}
</style>
"""

footer_html = """
<div class="footer" text-align="center">
    <footer>AI AgentZone @2025</footer>
</div>
"""

# Inject the olive theme CSS and footer into the Streamlit app
st.markdown(olive_theme_css, unsafe_allow_html=True)
st.markdown(footer_html, unsafe_allow_html=True)

# Display header image (p7.jpg) at the top of the page
try:
    with open("p7.jpg", "rb") as header_image_file:
        header_image_bytes = header_image_file.read()
        encoded_header_image = base64.b64encode(header_image_bytes).decode()
        header_html = f"""
        <div style="width:100%;height:10%;text-align:center;">
            <img src="data:image/jpg;base64,{encoded_header_image}" style="width:100%;height:10%;" />
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Header image 'p7.jpg' not found.")

# Sidebar navigation
st.sidebar.title("Olive Garden Restaurants")
menu = st.sidebar.radio("", ["Home", "About Us", "Gallery", "Reservations", "Call Agent"])

# Home Page
if menu == "Home":
    st.markdown("## <h3>🍽️ Welcome to Olive Garden Restaurants</h3>", unsafe_allow_html=True)
    st.markdown("""
#### The Olive Green Zone Restaurant, Milwaukee
Welcome to The Olive Green Zone Restaurant, Milwaukee - a haven of culinary delight
and elegant ambiance. Our restaurant offers a serene and stylish environment perfect
for any occasion. Guests can enjoy a variety of seating options tailored to their
preferences:
- Banquette Seating: Cozy and intimate, ideal for small groups and romantic dinners.
- Window View Seating: Enjoy your meal with a scenic view, perfect for a relaxing dining
experience.
- Bar Seating: A vibrant and social setting, great for casual dining and drinks.
Our amenities include complimentary Wi-Fi, valet parking, and a curated menu of
gourmet dishes. We are open for breakfast, lunch, and dinner, with check-in available
from 8:00 AM and last seating at 10:00 PM.
We look forward to welcoming you to The Olive Green Zone Restaurant, where every
meal is a memorable experience.
""", unsafe_allow_html=True)

# About Us
elif menu == "About Us":
    st.markdown("### About Us", unsafe_allow_html=True)
    st.write("Olive Garden Restaurants is a futuristic dining experience where artificial intelligence helps manage reservations, seating, and customer interactions seamlessly.")

# Gallery
elif menu == "Gallery":
    st.markdown("### Gallery", unsafe_allow_html=True)
    image_files = ["p1.jpg", "p2.jpg", "p3.jpg", "p4.jpg", "p5.jpg", "p7.jpg", "p8.jpg"]
    num_columns = 3
    rows = (len(image_files) + num_columns - 1) // num_columns
    for row in range(rows):
        cols = st.columns(num_columns)
        for col_idx in range(num_columns):
            img_idx = row * num_columns + col_idx
            if img_idx < len(image_files):
                img_file = image_files[img_idx]
                try:
                    with open(img_file, "rb") as img:
                        cols[col_idx].image(img.read(), use_container_width=True)
                except (FileNotFoundError, UnidentifiedImageError, Exception) as e:
                    cols[col_idx].warning(f"Could not load image {img_file}: {e}")

# Reservations
elif menu == "Reservations":
    st.markdown("### Reservations", unsafe_allow_html=True)
    excel_file = "olivegarden inventory Seating .xlsx"
    try:
        table_allocation_df = pd.read_excel(excel_file, sheet_name="Table allocation", engine="openpyxl")
        seating_df = pd.read_excel(excel_file, sheet_name="Seating", engine="openpyxl")
        st.markdown("### 🛑 Table Allocation View", unsafe_allow_html=True)
        st.dataframe(table_allocation_df, use_container_width=True)
        st.markdown("### 📋 Seating Summary", unsafe_allow_html=True)
        st.dataframe(seating_df, use_container_width=True)
    except FileNotFoundError:
        st.error(f"Excel file '{excel_file}' not found.")
    except Exception as e:
        st.error(f"Error loading Excel data: {e}")

# Helper function to format time difference
def format_relative_time(iso_timestamp):
    now = datetime.now()
    past = datetime.fromisoformat(iso_timestamp)
    diff = now - past

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        return past.strftime("%Y-%m-%d %H:%M")

# Call Agent
if menu == "Call Agent":
    st.markdown("### 💬 Chat with AWS Bedrock Agent", unsafe_allow_html=True)

    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = "90813a89-e0c3-4908-be12-d46a7554d0c5"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Clear chat button
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")

    # Debug toggle
    show_debug = st.checkbox("Show debug info")

    # Display chat history
    for entry in st.session_state.chat_history:
        role = entry["role"]
        message = entry["message"]
        timestamp = entry["timestamp"]
        relative_time = format_relative_time(timestamp)
        if role == "user":
            st.markdown(f"**🧑 You ({relative_time}):** {message}")
        else:
            st.markdown(f"**🤖 Agent ({relative_time}):** {message}")

    # User input
    user_input = st.text_input("Ask your question:")

    # AWS Bedrock Agent configuration
    AGENT_ID = "8XAWF2A0JI"
    AGENT_ALIAS_ID = "XOSBDAEQQN"
    REGION = "us-east-1"

    if st.button("Send") and user_input:
        try:
            timestamp = datetime.now().isoformat()
            st.session_state.chat_history.append({
                "role": "user",
                "message": user_input,
                "timestamp": timestamp
            })

            # Initialize Bedrock Agent client
            session = boto3.Session()
            client = session.client("bedrock-agent-runtime", region_name=REGION)

            # Invoke the agent
            response_stream = client.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId=st.session_state.session_id,
                inputText=user_input
            )

            # Read streaming response
            completion = ""
            if show_debug:
                st.markdown("📥 **Raw Response Stream:**")
            for event in response_stream:
                if show_debug:
                    st.code(event)
                if "chunk" in event:
                    text = event["chunk"].get("text", "")
                    completion += text

            if show_debug:
                st.markdown("🧾 **Final Completion:**")
                st.code(completion)

            if completion.strip():
                st.session_state.chat_history.append({
                    "role": "agent",
                    "message": completion,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                st.warning("⚠️ Agent returned an empty response. Try rephrasing your question.")

        except (NoCredentialsError, PartialCredentialsError):
            st.error("❌ AWS credentials not found or incomplete. Please run `aws configure` or refresh your session.")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ExpiredTokenException":
                st.error("🔐 Your AWS session token has expired. Please refresh your credentials (e.g., run `aws sso login` or re-authenticate).")
            else:
                st.error(f"❌ AWS ClientError: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected Error: {e}")
#streamlit: for the web app interface
#boto3: for AWS Bedrock Agent integration
#pandas, openpyxl: for Excel file handling
#Pillow: for image processing