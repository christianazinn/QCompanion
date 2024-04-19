TODO allow gpu offload for certain tasks
TODO Lilac integration?
TODO be able to handle errors in ordering in the megaqueuer
TODO README creation from template/from original model template
TODO upload whole directory at once with megaqueuer
TODO allow the user to select which files to upload in the megaqueuer?

# ON DECK
TODO HF token for download?
TODO LLaMA-Factory integration

# NEXT TESTS
TODO fix the weird bug where you have to refresh the page on toggling on the job scheduler

# CONTINUALLY
TODO keep install scripts and requirements.txt as up to date as you physically can
TODO remake docs and page descriptions
TODO TEST TEST TEST!!!

# WATCH OUT FOR/NOTES
TODO keep an eye on streamlit-process-manager

the way @st.cache_resources works is that you apply it to a function and then that function's return value is cached
every time you mutate the function's return value you mutate the object in cache
https://docs.streamlit.io/develop/concepts/architecture/caching

subprocess.run is blocking!