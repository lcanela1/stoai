import streamlit as st
import openai
import ast, json, os
openai.api_key = st.secrets.oai.key

st.set_page_config(layout="wide")

hide_streamlit_style = """
<style>
.st-au{
border-radius: 30px !important;
background: white !important
}
    p {
    font-size: 1.2em
    }
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    header {visibility: hidden;}
    .stApp {
    background: #f0f9ff
    }
    .st-bf, textarea{
    background: #fff !important;

    border-radius: 30px
    }
    .stButton>button {
        # color: #4F8BF9;
        background: #fafafa;
        width: 100%;
    border-radius: 16px
    }

    button > div > p {
        font-weight: 700 !important;
    }

    h3 {
    padding-bottom: 2px;
    }

    div > div:nth-child(2) > div > div > p {
    background: #f1f5f9;
    padding: 1rem;  
    border-radius: 16px;
    border: 1px solid #333
    }
    #explain-my-chest-x-ray-app > div > span {
    margin-top: -15px;
    }
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

title_container = st.container()
col1a, col2a = st.columns([1, 20])
with title_container:
    with col1a:
        st.image('./leaf-icon.png', width=54)
    with col2a:
        st.title('Explain my Chest X-Ray App')

summaries = {
    'Normal':
    """Your chest x-ray results are clear - this is great news. The radiologist didn't find anything unusual in your lungs or any other parts of the chest area that were examined. This includes your heart, blood vessels in the lung region, bones surrounding the chest, and the upper abdomen. Areas between the bottom of your lungs and your chest wall (called costophrenic angles) are also clear. In a nutshell, everything looks as it should, and there are no signs of disease or health problems in the examined area. Remember, though, standard follow-up and routine health exams are crucial for staying healthy.""",
    'Pneumonia':
    """Your chest X-ray shows signs that you might have pneumonia, which is an infection in the lungs. The lower part of your right lung seems to be affected. This might be causing your symptoms of cough and fever. Don't worry, pneumonia can be treated with medications. Discuss your results with your doctor to start the right treatment plan for you.""",
    'Lung Cancer':
    """
    Based on your chest x-ray, an abnormal area was found in the upper section of your right lung. This area displays an unusual pattern and its size measures roughly about 4 cm. An additional noted detail is a prominence in an area adjacent to your lungs. Yet, it's necessary to conduct a further specialized scan (CT scan) to have a clearer understanding. Apart from this, your lungs and surrounding structures show signs which might point towards a chronic lung disease. However, this conclusion is not definitive and might require further examinations. I would strongly suggest arranging an appointment with your doctor to discuss these findings in detail.
    """
}

reports = {
    'Normal': """Clinical Information: Routine examination

Technique: PA and Lateral

Comparison: None

Findings: 

- The lungs are clear bilaterally. Specifically, no evidence of focal consolidation, pleural effusion, or pneumothorax.
- The cardiac silhouette size is within normal limits.
- The mediastinum and hila are unremarkable.
- The pulmonary vasculature is normal.
- No acute bony abnormality observed. 
- Both costophrenic angles are clear. 
- The diaphragm, pleural spaces, and upper abdomen are unremarkable.


Impression: 
Normal chest x-ray.
""",
    'Pneumonia': """
Clinical Information: Cough and fever for the past week. Suspected pneumonia

Radiological Procedure: Chest X-ray PA view

Findings:

The examination was carried out and the images were reviewed. 

There is an increased opacity noted in the right lower lobe, extending towards the mid-zone. This opacity is not well circumscribed and seems to be spreading along the bronchovascular bundles with air bronchogram within, suggestive of bronchopneumonia. There is likely consolidation in the affected areas, further supporting the possibility of pneumonia. 

No significant hilar lymphadenopathy is appreciated. There are no visible masses, cavitations or pleural effusion. Heart size and mediastinal contours appear within normal limits. The trachea and main bronchi appear unremarkable. Pulmonary vascularity remains preserved. The cardio-diaphragmatic and costophrenic angles are clear. Bony structures show no visible lesions or fractures.

Impression: 

Findings are highly suggestive of bronchopneumonia in the right lower to mid lungs.""",

    'Lung Cancer': """
Clinical History: A 70 year old patient with a chronic cough.

Technique: Frontal and lateral views of the chest were obtained. 

Findings: 

The lung volumes are normal. There is a distinct 4 cm opacity noted in the right upper lung field. The mass is irregularly shaped with well circumscripted margins. There is also hilar prominence noted on the right side, suggestive of possible hilar lymphadenopathy, however, better defined with a CT scan of the chest.

The remaining lungs and pleural spaces are clear with no evidence of consolidation, pneumothorax, or pleural effusion. However, there are diffuse interstitial reticular markings which may represent a pattern of underlying chronic lung disease. 

The soft tissues and bony thorax are unremarkable with no fractures or lytic lesions.

Impression:
1. Right upper lobe lung mass, 4 cm in size, with associated hilar prominence.
2. Diffuse interstitial markings suggestive of chronic lung disease. 
"""
}

if "summary" not in st.session_state:
    st.session_state.summary = """ 
    Your chest x-ray results are clear - this is great news. The radiologist didn't find anything unusual in your lungs or any other parts of the chest area that were examined. This includes your heart, blood vessels in the lung region, bones surrounding the chest, and the upper abdomen. Areas between the bottom of your lungs and your chest wall (called costophrenic angles) are also clear. In a nutshell, everything looks as it should, and there are no signs of disease or health problems in the examined area. Remember, though, standard follow-up and routine health exams are crucial for staying healthy."""
    

col1, col2 = st.columns(2)

def get_key_by_value(my_dict, value):
    return next((k for k, v in my_dict.items() if v == value), "Custom")

def handle_inference():
    if False:#seport_txt in reports[option]:
        st.session_state.summary=summaries[option]
    else:

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": """I will send you a diagnostic report os chest x-ray. Classify them in one of the following classes:
        1. Pneumonia
        2. Chronic obstructive pulmonary disease (COPD)
        3. Lung cancer
        4. Pulmonary edema
        5. Pneumothorax
        6. Heart failure
        7. Tuberculosis
        8. Pleural effusion
        9. Rib fractures
        10. Not possible to determine diagnosis.
        Write an easy-to-understand paragraph for the patient the will receive this radiologic report so that he understands well. Be concise. If is there a finding suggestive of cancer, category 3, you should not say that to a patient and tell him to go see his doctor instead. 
        Return a valid JSON everytime. As response, use this format:
        {classification: one of the 10 classes;
        explanation: the patient explanation}"""},
                {"role": "user", "content": st.session_state.report_txt.strip()},
            ]
        ,
        max_tokens=2048,
        temperature=.5
    )
        summary_dict=response['choices'][0].message.content
        try:
            try:
                response = ast.literal_eval(summary_dict) ## .strip
            except:
                summary_dict = summary_dict.replace('explanation', '"explanation"').replace('classification', '"classification"')
                response = json.loads(summary_dict)
        except:
            response = {'explanation': 'Failed to fetch'}
        st.session_state.summary=response['explanation'].strip()

with col1:
   
    option = st.selectbox(
        'Report Type',
        ('Normal', 'Pneumonia', 'Lung Cancer'),
        )

    st.session_state.report_txt=st.text_area(label='Report Text', value=reports[option], height=400)

    st.button('Generate Patient Summary', on_click=handle_inference)

with col2:
    st.subheader("Patient Summary")
    summary_text=st.write(st.session_state.summary)
