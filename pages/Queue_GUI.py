# FILESTATUS: mostly done, but still needs testing and feature implementations. Last updated v0.1.2-pre4
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.scheduler import *
from streamlit_sortables import sort_items

# FUNCTIONS ---------------------------------------------------------------------------------

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("Compute Job Scheduler")

def update_active():
    st.session_state["active"] = get_scheduler().is_active()

st.write("The current state of the job scheduler is shown below.")

update_active()
st.write(st.session_state["active"])

if st.button("Toggle Compute Job Scheduler", on_click=get_scheduler().toggle):
    # callback and update have to be in a very specific order for them to work
    update_active()
    st.rerun() 

if st.button("Terminate Current Job", on_click=get_scheduler().send_termination_signal):
    # callback and update have to be in a very specific order for them to work
    update_active()
    st.rerun()

# functionality you need:
# TODO support download tasks when you write the new download scheduler
# TODO be able to queue later jobs for files that don't yet exist (i.e. convert then quantize) and handle errors in ordering

st.write('----')
st.write('Reorder the job list as you like, then click "Save Changes" to save your changes to the queue. If the drag-and-drop field bugs out, try going to another page and coming back.')

def update_jobs():
    st.session_state["jobs"] = [item.strip() for item in get_scheduler().get_queue()]

update_jobs()
sorted_items = sort_items(st.session_state["jobs"], direction="vertical")
st.write(sorted_items)

if st.button("Refresh Job List", on_click=update_jobs):
    # callback and update have to be in a very specific order for them to work
    update_jobs()

st.write("You can only write changes when the scheduler is paused.")

if st.button("Save Changes", disabled=st.session_state["active"], on_click=lambda: get_scheduler().write_jobs(sorted_items)):
    # callback and update have to be in a very specific order for them to work
    update_jobs()

if st.button("Clear Job List", disabled=st.session_state["active"], on_click=get_scheduler().clear_queue):
    # callback and update have to be in a very specific order for them to work
    update_jobs()

delete_idx = st.number_input("Delete Job at Index", min_value=0, max_value=(len(st.session_state["jobs"])-1), value=0)
if st.button("Delete Job", disabled=st.session_state["active"], on_click=lambda: get_scheduler().remove_job(delete_idx)):
    # callback and update have to be in a very specific order for them to work
    update_jobs()

st.write('----')
st.title("Completed Jobs")
st.write('Completed jobs in plaintext:')

def update_completed():
    st.session_state["completed"] = '\n'.join(get_scheduler().get_completed())

update_completed()
st.code(st.session_state["completed"])

st.button("Refresh Completed Jobs", on_click=update_completed)

if st.button("Clear Completed Jobs", on_click=get_scheduler().clear_completed):
    # callback and update have to be in a very specific order for them to work
    update_completed()