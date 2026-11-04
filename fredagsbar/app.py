import os

import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:5000")


def call_api(method, path, json=None):
    """Kalder API'en. Returnerer (data, None) ved succes eller (None, fejlbesked) ved fejl."""
    try:
        response = httpx.request(method, API_URL + path, json=json, timeout=2)
        response.raise_for_status()
    except httpx.ConnectError:
        return None, "Kan ikke forbinde til API'en. Kører den?"
    except httpx.TimeoutException:
        return None, "API'en svarer for langsomt. Prøv igen om lidt."
    except httpx.HTTPStatusError as e:
        message = e.response.json().get("error", "Ukendt fejl")
        return None, f"Fejl {e.response.status_code}: {message}"

    if response.status_code == 204:  # 204 har ingen body
        return None, None
    return response.json(), None


def done(message):
    """Gem en besked og kør scriptet forfra, så data hentes på ny fra API'en."""
    st.session_state.message = message
    st.rerun()


st.title("Fredagsbarens events")

# Navnet gemmes automatisk i st.session_state["name"] via key=
st.sidebar.text_input("Dit navn", key="name")
name = st.session_state.name

# Besked fra sidste handling (overlever st.rerun)
if "message" in st.session_state:
    st.success(st.session_state.pop("message"))

# Hent data hver gang scriptet kører, så oversigten altid er opdateret
events, error = call_api("GET", "/events")
if error:
    st.error(error)
    st.stop()

# 1. Oversigt
st.header("Oversigt")
rows = [
    {
        "Titel": e["title"],
        "Dato": e["date"],
        "Tilmeldte": len(e["participants"]),
        "Ledige pladser": e["capacity"] - len(e["participants"]),
    }
    for e in events
]
st.dataframe(rows, hide_index=True)

# 2. Tilmeld og afmeld
st.header("Tilmeld / afmeld")
if events:
    # Vælg på id og slå op i de friske data (ellers viser Streamlit et gammelt event-dict)
    events_by_id = {e["id"]: e for e in events}
    event_id = st.selectbox(
        "Vælg event",
        events_by_id,
        format_func=lambda i: f"{events_by_id[i]['title']} ({events_by_id[i]['date']})",
    )
    event = events_by_id[event_id]
    st.write("Deltagere:", ", ".join(event["participants"]) or "Ingen endnu")

    is_full = len(event["participants"]) >= event["capacity"]
    col1, col2 = st.columns(2)

    if not name:
        st.warning("Skriv dit navn i sidebaren for at tilmelde dig.")

    if col1.button("Tilmeld mig", disabled=is_full or not name):
        _, error = call_api("POST", f"/events/{event['id']}/signups", json={"name": name})
        if error:
            st.error(error)
        else:
            done(f"{name} er tilmeldt {event['title']}")

    if col2.button("Afmeld mig", disabled=not name):
        _, error = call_api("DELETE", f"/events/{event['id']}/signups/{name}")
        if error:
            st.error(error)
        else:
            done(f"{name} er afmeldt {event['title']}")

    if is_full:
        st.info("Eventet er fuldt.")
else:
    st.info("Der er ingen events endnu.")

# 3. Opret event
st.header("Opret event")
with st.form("create_event", clear_on_submit=True):
    title = st.text_input("Titel")
    date = st.date_input("Dato")
    capacity = st.number_input("Antal pladser", min_value=1, step=1, value=10)
    submitted = st.form_submit_button("Opret")

if submitted:
    new_event = {"title": title, "date": date.isoformat(), "capacity": int(capacity)}
    _, error = call_api("POST", "/events", json=new_event)
    if error:
        st.error(error)
    else:
        done(f"Eventet '{title}' er oprettet")
