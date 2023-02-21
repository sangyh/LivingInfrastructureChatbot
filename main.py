"""Python file to serve as the frontend"""
import streamlit as st
from streamlit_chat import message
import sys
import os
from gpt_index import GPTPineconeIndex
import openai
import pinecone
import json

ROOT_DIR = os.path.abspath('/Users/sangyhanumasagar/Desktop/Freelancing/Spherical/')

if (os.environ.get("OPENAI_API_KEY") == None):
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, 'config', '.env')) #UPDATE PATH

openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))

# load from disk
pc_index = pinecone.Index("livinginfra")
index_new = GPTPineconeIndex.load_from_disk('data/indices/sample_index_pinecone.json', pinecone_index=pc_index)

# From here down is all the StreamLit UI.
st.set_page_config(page_title="Living Infrastructure QA Bot", page_icon=":robot:")
st.header("Ask me about Living Infrastructure")
st.subheader('')

st.markdown(
"""PS: I am currently only trained on these 5 documents:
1. [The Care Manifesto: The Politics of Interdependence](https://sphericalstudio.notion.site/The-Care-Manifesto-The-Politics-of-Interdependence-b7434508615d4ef6b12794b6f2dc49a0)
2. [Systems thinking for the sustainability transformation of urban water systems](https://sphericalstudio.notion.site/Systems-thinking-for-the-sustainability-transformation-of-urban-water-systems-24f9eb50b946404191e7e0c397686e77)
3. [Opportunities to Accelerate Nature-Based Solutions- A Roadmap for Climate Progress, Thriving Nature, Equity, & Prosperity. A Report to the National Climate Task Force](https://sphericalstudio.notion.site/Opportunities-to-Accelerate-Nature-Based-Solutions-A-Roadmap-for-Climate-Progress-Thriving-Nature--42b574a9c0984c78ae5765e2b2173d41)
4. [FACT SHEET: Biden-⁠Harris Administration Announces Roadmap for Nature-Based Solutions to Fight Climate Change, Strengthen Communities, and Support Local Economies](https://sphericalstudio.notion.site/FACT-SHEET-Biden-Harris-Administration-Announces-Roadmap-for-Nature-Based-Solutions-to-Fight-Clima-9002a81aac62484eaafeb69b6d2b9853)
5. [The Nature-Based Solutions Roadmap for the United States](https://sphericalstudio.notion.site/The-Nature-Based-Solutions-Roadmap-for-the-United-States-6114b40df08242f09c70037ced265af4)
\nStay tuned for more..."""
)
message("Hi I am Mr.Bot. I will share what I know along with sources for all my answers :).")
st.markdown("_Try asking: What is the Care Manifesto?_")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []
    
if "generated" not in st.session_state and "past" not in st.session_state:
    st.session_state = dict.fromkeys(["generated","past"],[]) 

def get_text():
    input_text = st.text_input("You: ", "Hello, how are you?", key="input")
    return input_text

user_input = st.text_input("You: ") 

if user_input:
    query = f"""You are a chatbot designed to answer questions by retrieving relevant information from the provided documents. If you are not able to find the answer in the provided information, say I don't know.
With this information, answer the following question: {user_input}"""

    response = index_new.query(query)
    
    if response.source_nodes:
        source_info = response.source_nodes[0].source_text.split('\n')
        doc_id = source_info[0]
        page_id = source_info[1].split(' ')[-1]
        url = 'https://sphericalstudio.notion.site/'+ page_id.replace('-','')
        
        output = f"Answer: {response.response}\nSources: {url}"
    else:
        output = f"Answer: {response.response}\nSources: None found."
    
   
    st.session_state['past'].append(user_input)
    st.session_state['generated'].append(output)

if st.session_state["generated"]:

    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
