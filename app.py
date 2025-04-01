import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from collections import defaultdict
import base64

# === Цветовая схема ===
PAGE_BG_COLOR = "#262123"
PAGE_TEXT_COLOR = "#E8DED3"
SIDEBAR_BG_COLOR = "#262123"
SIDEBAR_LABEL_COLOR = "#E8DED3"
SIDEBAR_TAG_TEXT_COLOR = "#E8DED3"
SIDEBAR_TAG_BG_COLOR = "#6A50FF"
BUTTON_BG_COLOR = "#262123"
BUTTON_TEXT_COLOR = "#4C4646"
BUTTON_CLEAN_TEXT_COLOR = "#E8DED3"
SIDEBAR_HEADER_COLOR = "#E8DED3"
SIDEBAR_TOGGLE_ARROW_COLOR = "#E8DED3"
HEADER_MENU_COLOR = "#262123"
GRAPH_BG_COLOR = "#262123"
GRAPH_LABEL_COLOR = "#E8DED3"
NODE_NAME_COLOR = "#4C4646"
NODE_CITY_COLOR = "#D3DAE8"
NODE_FIELD_COLOR = "#EEC0E7"
NODE_ROLE_COLOR = "#F4C07C"
EDGE_COLOR = "#4C4646"
HIGHLIGHT_EDGE_COLOR = "#6A50FF"
TEXT_FONT = "Lexend"
DEFAULT_PHOTO = "https://static.tildacdn.com/tild3532-6664-4163-b538-663866613835/hosq-design-NEW.png"

def get_google_drive_image_url(url):
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/thumbnail?id={file_id}"
    return url

# === Настройки страницы ===
st.set_page_config(page_title="HOSQ Artist Graph", layout="wide")
st.markdown(f"""
    <style>
    html, body, .stApp, main, section {{
        background-color: {PAGE_BG_COLOR} !important;
        color: {PAGE_TEXT_COLOR} !important;
        font-family: '{TEXT_FONT}', sans-serif;
    }}
    header, footer {{
        background-color: {PAGE_BG_COLOR} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# === Загрузка и обработка CSV ===
df = pd.read_csv("Etudes Lab 1 artistis d3js.csv")
df.fillna('', inplace=True)

category_colors = {
    'artist': NODE_NAME_COLOR,
    'city': NODE_CITY_COLOR,
    'country': NODE_CITY_COLOR,
    'professional field': NODE_FIELD_COLOR,
    'role': NODE_ROLE_COLOR,
    'style': PAGE_TEXT_COLOR,
    'tool': PAGE_TEXT_COLOR,
    'level': PAGE_TEXT_COLOR,
    'seeking for': PAGE_TEXT_COLOR,
}

multi_fields = ['professional field', 'role', 'style', 'tool', 'level', 'seeking for']
nodes, links, artist_info = [], [], {}
node_ids, edge_ids = set(), set()
filter_options = defaultdict(set)

def add_node(id, label, group):
    if id not in node_ids:
        nodes.append({"id": id, "label": label, "group": group, "color": category_colors.get(group, '#888888')})
        node_ids.add(id)

def add_link(source, target):
    key = f"{source}___{target}"
    if key not in edge_ids:
        links.append({"source": source, "target": target})
        edge_ids.add(key)

for _, row in df.iterrows():
    artist_id = f"artist::{row['name']}"
    add_node(artist_id, row['name'], 'artist')

    photo_url = get_google_drive_image_url(row['photo url']) if row['photo url'] else DEFAULT_PHOTO

    artist_info[artist_id] = {
        "name": row['name'],
        "photo": photo_url,
        "telegram": row['telegram nickname'],
        "email": row['email']
    }

    for field in multi_fields:
        values = [v.strip() for v in row[field].split(',')] if row[field] else []
        for val in values:
            if val:
                node_id = f"{field}::{val}"
                add_node(node_id, val, field)
                add_link(artist_id, node_id)
                filter_options[field].add(val)

    if row['country and city']:
        parts = [p.strip() for p in row['country and city'].split(',')]
        if len(parts) == 2:
            country, city = parts
            country_id = f"country::{country}"
            city_id = f"city::{city}"
            add_node(country_id, country, 'country')
            add_node(city_id, city, 'city')
            add_link(artist_id, city_id)
            add_link(city_id, country_id)
            filter_options['country'].add(country)
            filter_options['city'].add(city)
