TODO support imatrix creation
TODO support imatrix use in quantization
TODO remake docs and page descriptions
TODO allow gpu offload for certain tasks
TODO rewrite install scripts
TODO be able to queue jobs across files and preferably write them to disk + use a background scheduler
TODO be able to reorder and remove tasks in queue in a visualizer - check out streamlit-draggable-list and streamlit-sortables
TODO code your own scheduler and move away from APScheduler, be able to pause/restart (after current task) or even cancel current task
TODO keep a log of completed jobs/read both files with a streamlit ui element

the way @st.cache_resources works is that you apply it to a function and then that function's return value is cached
every time you mutate the function's return value you mutate the object in cache
https://docs.streamlit.io/develop/concepts/architecture/caching

subprocess.run is blocking!

TODO thread safety? threading.Thread(target=process_queue, daemon=True).start()

TODO follow page FILESTATUSes and also rework the scripts in the main directory
TODO rewrite the little page blurbs on all pages
TODO TEST TEST TEST!!!