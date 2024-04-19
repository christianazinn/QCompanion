# Last updated v0.1.3-pre2
# IMPORTS ---------------------------------------------------------------------------------
import streamlit as st
st.set_page_config(layout="wide")
from st_pages import add_indentation
from util.scheduler import *
from streamlit_sortables import sort_items

# UI CODE ---------------------------------------------------------------------------------

add_indentation()

st.title("Scheduler GUI")

def update_active():
    st.session_state["active"] = get_scheduler().is_active()

schcols = st.columns([1,1])

with schcols[0]:
    st.write("The current state of the job scheduler is shown below.")

    update_active()
    st.write(st.session_state["active"])

# TODO haunted bug - you need to refresh via another button when you activate it but not when you deactivate it
with schcols[1]:
    if st.button("Toggle Scheduler", on_click=get_scheduler().toggle):
        # callback and update have to be in a very specific order for them to work
        update_active()
        st.rerun() 

    if st.button("Terminate Current Job and Delete", on_click=get_scheduler().send_termination_signal):
        # callback and update have to be in a very specific order for them to work
        update_active()
        st.rerun()

    if st.button("Terminate Current Job and Requeue", on_click=get_scheduler().send_termination_signal_requeue):
        # callback and update have to be in a very specific order for them to work
        update_active()
        st.rerun()

# functionality you need:
# TODO eventually be able to handle errors if prequeued (Full_Pipeline.py) jobs are deleted and it breaks the chain

st.write('----')

jobcols = st.columns([9,1])
st.write('Reorder the job list as you like, then click "Save Changes" to save your changes to the queue. If the drag-and-drop field bugs out, try going to another page and coming back.')

def update_jobs():
    st.session_state["jobs"] = [item.strip() for item in get_scheduler().get_queue()]

update_jobs()

with jobcols[0]:
    sorted_items = sort_items(st.session_state["jobs"], direction="vertical")
    st.write(sorted_items)

with jobcols[1]:
    st.write("Writeable only when paused.")

    if st.button("Refresh", on_click=update_jobs, key="refresh_jobs"):
        # callback and update have to be in a very specific order for them to work
        update_jobs()

    if st.button("Save", disabled=st.session_state["active"], on_click=lambda: get_scheduler().write_jobs(sorted_items)):
        # callback and update have to be in a very specific order for them to work
        update_jobs()

    if st.button("Clear", disabled=st.session_state["active"], on_click=get_scheduler().clear_queue, key="clear_jobs"):
        # callback and update have to be in a very specific order for them to work
        update_jobs()

    delete_idx = st.number_input("Delete Index", disabled=st.session_state["active"], min_value=0, max_value=(0 if len(st.session_state["jobs"]) == 0 else len(st.session_state["jobs"])-1), value=0)
    if st.button("Delete", disabled=st.session_state["active"], on_click=lambda: get_scheduler().remove_job(delete_idx)):
        # callback and update have to be in a very specific order for them to work
        update_jobs()

st.write('----')
st.title("Completed Jobs")

comcols = st.columns([9,1])

def update_completed():
    st.session_state["completed"] = '\n'.join(get_scheduler().get_completed())

update_completed()

with comcols[0]:
    st.code(st.session_state["completed"])

with comcols[1]:
    st.button("Refresh", on_click=update_completed, key="refresh_completed")

    if st.button("Clear", on_click=get_scheduler().clear_completed, key="clear_completed"):
        # callback and update have to be in a very specific order for them to work
        update_completed()