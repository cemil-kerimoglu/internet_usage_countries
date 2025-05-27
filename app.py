# app.py
import streamlit as st
from PIL import Image
import os

# Page config for a polished look
st.set_page_config(
    page_title="Global Internet Usage (2015)",
    layout="wide",
    initial_sidebar_state="auto"
)

def load_map_image(path: str):
    return Image.open(path)

def main():
    # Title and description
    st.title("🌐 Global Internet Usage by Country, 2015")
    st.markdown(
        """
        This dashboard shows the share of individuals using the Internet 
        in each country for the year 2015. Data source: Our World in Data.
        """
    )

    # Display the map
    img_path = os.path.join("images", "Internet_Usage.png")
    map_img = load_map_image(img_path)
    st.image(
        map_img,
        use_container_width=True,
        caption="Percentage of individuals using the Internet, by country (2015)"
    )

    # Sidebar for future controls
    # st.sidebar.header("About")
    # st.sidebar.info(
    #     "Built with Streamlit."
    # )

if __name__ == "__main__":
    main()
