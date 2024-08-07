import streamlit as st
import json
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap
from datetime import datetime
from datetime import timedelta

import config

def plot_case2():
    # Load the data
    with open('data/streamlit/case_2_data.json', 'r') as f:
        all_data = json.load(f)

    # Create a DataFrame for the time series plot
    df = pd.DataFrame([d['fractions'] for d in all_data])
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    # Plot each image with its land type distribution
    for data in all_data[0:4]:
        date_obj = datetime.fromisoformat(data['date'].rstrip("Z"))
        formatted_date = date_obj.strftime("%B %d, %Y")
        st.subheader(f"Date: {formatted_date}")
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Plot the predicted image
            fig, ax = plt.subplots()
            im = ax.imshow(data['predicted_image'], cmap=cmap, vmin=0, vmax=10)

            plt.title("Predicted Land Types")
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_ticks(midpoints)
            cbar.set_ticklabels(config.short_class_mapping.values())
            st.pyplot(fig)
        
        with col2:
            # Plot the land type distribution
            plot_fractions = {k: v for k, v in data['fractions'].items() if k not in ['Unknown', 'Date'] and v > 0}
            sorted_fractions = dict(sorted(plot_fractions.items(), key=lambda x: int(x[0])))
            labels = [f"{config.short_class_mapping[int(k)]} ({v*100:.1f}%)" for k, v in sorted_fractions.items()]
            colors = [config.value_to_color_maps[int(k)] for k in sorted_fractions.keys()]
            
            fig, ax = plt.subplots()
            wedges, _ = ax.pie(sorted_fractions.values(), labels=None, colors=colors, autopct=None, startangle=90)
            plt.title("Land Type Distribution")
            ax.legend(wedges, labels, title="Land Type", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            st.pyplot(fig)

    # Plot the time series
    st.subheader("Land Type Distribution Over Time")
    fig, ax = plt.subplots(figsize=(10, 5))
    for c in df.columns:
        if c not in ['Unknown', '-1']:
            df[c] = df[c].astype(float)
            plt.plot(df.index[0:4], df[c][0:4], c=config.value_to_color_maps[int(c)], lw=2, label=config.short_class_mapping[int(c)])

    plt.vlines(df.index[1] + timedelta(hours=21), 0, 0.5, color='black', linestyle='dashed', alpha=0.5)
    plt.title("Land Type Distribution Over Time")
    plt.xlabel("Date")
    plt.ylabel("Proportion")
    plt.legend(title="Land Type", bbox_to_anchor=(1.05, 1), loc='upper left')
    #plt.tight_layout()
    st.pyplot(fig)

st.set_page_config(layout="wide", page_title="Case Study 2: Seasonal Floods", page_icon=":ocean:",)

colors = list(config.value_to_color_maps.values())
values = list(config.value_to_color_maps.keys())
cmap = ListedColormap(colors)
cmap.set_bad(color='white')

midpoints = [val + 0.5 for val in range(0, 10, 1)]

st.title('Case Study: Seasonal Grasslands')
plot_case2()