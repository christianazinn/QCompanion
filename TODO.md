TODO allow gpu offload for certain tasks
TODO be able to change output directories and stuff
TODO be able to queue later jobs for files that don't yet exist (i.e. convert then quantize) and handle errors in ordering
TODO add a page that allows you to make one great big queued op for download/convert/quantize/(imatrix)/upload/etc
TODO LLaMA-Factory integration
TODO Lilac integration?
TODO support further cli options for relevant commands/pages
TODO readme creation!

# ON DECK
TODO create new download scheduler
TODO imatrix creation
TODO imatrix quantization support

# NEXT TESTS
done for now

# CONTINUALLY
TODO keep install scripts and requirements.txt as up to date as you physically can
TODO remake docs and page descriptions
TODO follow page FILESTATUSes and also rework the scripts in the main directory
TODO TEST TEST TEST!!!

# WATCH OUT FOR/NOTES
TODO keep an eye on streamlit-process-manager
TODO thread safety? threading.Thread(target=process_queue, daemon=True).start()

the way @st.cache_resources works is that you apply it to a function and then that function's return value is cached
every time you mutate the function's return value you mutate the object in cache
https://docs.streamlit.io/develop/concepts/architecture/caching

subprocess.run is blocking!