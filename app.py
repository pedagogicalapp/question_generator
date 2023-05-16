import streamlit as st
import openai as ai
import numpy as np
import pandas as pd
from google.oauth2 import service_account
from gspread_pandas import Spread,Client
import gspread_pandas
import streamlit_analytics
import requests
import json
from htmldocx import HtmlToDocx
import base64
from datetime import datetime

ai.api_key = st.secrets["openai_api_key"]

API_KEY = st.secrets["openai_api_key"]
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
model = 'gpt-4'
#

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def generate_chat_completion(model, prompt, temperature=1, max_tokens=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": f"{prompt}"}],
        "temperature": temperature,
    }

    if max_tokens is not None:
        data["max_tokens"] = max_tokens

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# For Da-Vinci 3
def generate_response(MODEL, PROMPT, MAX_TOKENS=750, TEMP=0.99, TOP_P=0.5, N=1, FREQ_PEN=0.3, PRES_PEN = 0.9):
  response = ai.Completion.create(
          engine = MODEL,
          # engine="text-davinci-002", # OpenAI has made four text completion engines available, named davinci, ada, babbage and curie. We are using davinci, which is the most capable of the four.
          prompt=PROMPT, # The text file we use as input (step 3)
          max_tokens=MAX_TOKENS, # how many maximum characters the text will consists of.
          temperature=TEMP,
          # temperature=int(temperature), # a number between 0 and 1 that determines how many creative risks the engine takes when generating text.,
          top_p=TOP_P, # an alternative way to control the originality and creativity of the generated text.
          n=N, # number of predictions to generate
          frequency_penalty=FREQ_PEN, # a number between 0 and 1. The higher this value the model will make a bigger effort in not repeating itself.
          presence_penalty=PRES_PEN # a number between 0 and 1. The higher this value the model will make a bigger effort in talking about new topics.
      )
  return response['choices'][0]['text']

MODEL = 'text-davinci-003'
streamlit_analytics.start_tracking()

st.header('Exam Question Generator')
st.sidebar.image('pedagogical_18.png')
st.sidebar.markdown("This worksheet generator was created using OpenAI's generative AI. Please use it carefully and check any output before using it with learners as it could be biased or wrong. Send any comments or questions to phil@pedagogical.app. The specifications on which these questions are based can be found [here](https://qualifications.pearson.com/content/dam/pdf/GCSE/History/2016/specification-and-sample-assessments/gcse-9-1-history-specification.pdf) and [here](https://www.aqa.org.uk/subjects/history/gcse/history-8145/assessment-resources) ")
st.markdown("Other Pedagogical apps to check out: [worksheet generator](https://pedagogical.app/) and [knowledge organiser generator](https://pedagogical-knowledge-organiser.streamlit.app/)")

email = st.text_input('Email')
subject = st.radio('Subject', ['History', 'Geography', 'RS', 'Philosophy'])

output_type = st.radio('Generation Type', ['Individual Questions', 'Question Bank'], help="A Question Bank will include a question for all elements of the curriculum.")
if subject == 'History':


    if output_type == 'Individual Questions':


        number_questions = st.slider('Number of Questions', 1, 5)
        q_topic = st.text_input('Question Topic (including country and time period)')

        ### HISTORY ###
        if subject == 'History':
            exam = st.radio('Exam Boards', ['Edexcel GCSE', 'AQA GCSE'])
            if exam == 'Edexcel GCSE':
                question_type = st.radio('Question Type', ['Edexcel 16 Mark', 'Edexcel 12 Mark Explain', 'Edexcel 4 Mark Describe'])
                
                if question_type == 'Edexcel 16 Mark':
                    prompt = f"""
                    Create {number_questions} Edexcel GCSE 16 mark history question on the topic of {q_topic}. Make it in the format of the following questions:

            ‘The role of religion was the main reason why there were changes in the number of accusations of witchcraft in the early modern period (c1500–c1700). \n How far do you agree? Explain your answer. \ You may use the following in your answer: religious beliefs, Matthew Hopkins \n You must also use information of your own. \n (16)

            ‘Financial difficulties were the most significant problem faced by Henry in the years 1520–29.’  \n How far do you agree? Explain your answer. \ You may use the following in your answer: the Amicable Grant, Catherine of Aragon \n You must also use information of your own. \n (16)

            ‘The main consequence of William I’s policy of Normanisation was increased control of the Church in England.’  \n How far do you agree? Explain your answer. \ You may use the following in your answer: bishops,  landholding \n You must also use information of your own. \n (16)
            """

                if question_type == 'Edexcel 12 Mark Explain':
                    prompt = f"""
                    Create {number_questions} question on the topic of {q_topic}. Start the question with 'Explain why' and make it in the format of the following questions:

            Explain why there were changes in the prison system in the period c1700–c1900. \n You may use the following in your answer: \n • John Howard \n
            • hard labour \n You must also use information of your own. \n (12)

            Explain why there was rapid change in the treatment of illness in Britain during the
            twentieth century.  \n  You may use the following in your answer: \n • magic bullets \n • high-tech treatment \n You must also use information of your own. \n (12)

            Explain why there was increased violence in Northern Ireland from 1960-1980.  \n  You may use the following in your answer: \n • Civil Rights Protests \n • IRA \n You must also use information of your own. \n (12)
            """

                if question_type == 'Edexcel 4 Mark Describe':
                    prompt = f"""
                    Create {number_questions} questions on {q_topic}. Use the format below.

            Create 1 question on Crime and Punishement in 19th century london : Describe two features of accommodation for the poorer people in the
            Whitechapel area. \n 
            Feature 1 \n .................................................................................................................................................................................................................................................................................... \n 
            .................................................................................................................................................................................................................................................................................... \n 
            Feature 2 \n 
            .................................................................................................................................................................................................................................................................................... \n
            .................................................................................................................................................................................................................................................................................... (4 Marks)

            Create 1 questions on British History of the Western Front in World War One:
            Describe two features of the support trench system on the Western Front. \n 
            Feature 1 \n .................................................................................................................................................................................................................................................................................... \n 
            .................................................................................................................................................................................................................................................................................... \n 
            Feature 2 \n 
            .................................................................................................................................................................................................................................................................................... \n
            .................................................................................................................................................................................................................................................................................... (4 Marks)

            Create 2 questions on Early Elizabethan England, 1558–88:
            Describe two features of the attempts to colonise Virginia in the 1580s. \n 
            Feature 1 \n .................................................................................................................................................................................................................................................................................... \n 
            .................................................................................................................................................................................................................................................................................... \n 
            Feature 2 \n 
            .................................................................................................................................................................................................................................................................................... \n
            .................................................................................................................................................................................................................................................................................... (4 Marks)

            Describe two features of the nature and extent of the Puritan challenge. \n 
            Feature 1 \n .................................................................................................................................................................................................................................................................................... \n 
            .................................................................................................................................................................................................................................................................................... \n 
            Feature 2 \n 
            .................................................................................................................................................................................................................................................................................... \n
            .................................................................................................................................................................................................................................................................................... (4 Marks)
            """

            if exam == 'AQA GCSE':
                question_type = st.radio('Question Type', ['AQA 4 Mark Describe (Paper 1 Section A)', 'AQA 8 Mark - In what ways (Paper 1 Section A)', 'AQA 8 Marks - explain what was important/ Significant (Paper 2 Section B)', 
                # 8 + 12 markers
                'AQA 8 Marks - Write an account', 'AQA 12 Marks - Which of the Following', # 'AQA 8 Marks - similarity (Paper 2 Section A)',
                # 16 Markers
                'AQA 16 Marks - How far do you agree? (Paper 1 Section B)', 'AQA 16 Marks - Case study', 'AQA 16 Marks - Main factor (Paper 2 Section A)'])
            
            # Generate Questions Button
                if question_type == 'AQA 4 Mark Describe (Paper 1 Section A)':
                    prompt = f"""
                    Create {number_questions} questions on {q_topic}. Use the format below.

            Create 1 question on America, 1840–1895 Expansion and consolidation:
            Describe two problems faced by the American Government in settling the West. [4 Marks]

            Create 1 question on Russia 1894-1945: Tsardom and communism: 
            Describe two problems faced by the Russian people during the First World War. [4 Marks]

            """

                if question_type == 'AQA 8 Mark - In what ways (Paper 1 Section A)':
                    prompt = f"""
                    Create 1 questions on {q_topic}. Use the format below.

            Create 1 question on America, 1840–1895: Expansion and consolidation:
            In what ways were the lives of Americans affected by slavery? \n Explain your answer. [8 marks]

            Create 1 question on Russia 1894-1945:
            In what ways were the lives of people affected by Stalin’s dictatorship? \n  Explain your answer. [8 marks]

            Create 1 question on The Cold War 1960-1970: 
            In what ways were the lives of Cubans affected by the Cuban Missile Crisis? \n  Explain your answer. [8 marks]

                Create 1 question on The Northern Ireland Troubles, 1960-1980:
            In what ways were the lives of English people affected by the IRA bombing campaign? \n  Explain your answer. [8 marks]
            """

                if question_type == 'AQA 8 Marks - explain what was important/ Significant (Paper 2 Section B)':
                    prompt = f"""
                    Create 1 questions on {q_topic}. Use the questions below as a format but do not include the questions below in the response:

            Create 1 question on Elizabethan England, c1568–1603:
            1. Explain what was important about Elizabethan England that made it a ‘Golden Age’. [8 marks]

            Create 2 question on Restoration England, 1660–1685: 
            1. Explain what was important about Charles II’s relationship with Parliament. [8 marks]
            2. Explain what was significant about the Fire of London that impacted the city. [8 marks]

            Create 3 question on 19th century Ireland: 
            1. Explain what was significant about The Great Famine. [8 marks]
            2. Explain what was significant about Gladstone's relationship with Ireland. [8 marks]
            3. Explain what was important about Daniel O'Connell. [8 marks]

            """

                if question_type == 'AQA 8 Marks - similarity (Paper 2 Section A)':
                    prompt = f"""
                Create {number_questions} questions on {q_topic}. Use the format below.

            Create 1 question on Britain: Power and the people: c1170 to the present day:
            Explain two ways in which the Peasants’ Revolt and the American Revolution were similar. [8 marks]

            Create 1 question on Britain: Health and the people: c1000 to the present day
            Explain two ways in which medieval public health and 19th century public health were similar. [8 marks]

            """
                if question_type == 'AQA 8 Marks - Write an account':
                    prompt = f"""
                Create 1 questions on {q_topic}. Use the format below.

            Create 1 question on Conflict and tension in Asia, 1950–1975:
            Write an account of how the media and TV influenced American opinions about the Vietnam War. [8 Marks]

            Create 1 question on Britain Conflict and tension - the inter-war years, 1918–1939
            Write an account of how the Nazi–Soviet Pact led to war [8 marks]
            """

                if question_type == 'AQA 12 Marks - Which of the Following':
                    prompt = f"""
                Create 1 questions on {q_topic}. Use the format below.

            Create 1 question on America, 1840–1895 Expansion and consolidation:
            Which of the following was the more important reason why the Plains Indians were defeated: \n • the destruction of the buffalo \n • the US Army? \n Explain your answer with reference to both bullet points. [12 marks]

            Create 1 question on Germany, 1890-1945:
            Which of the following was the more important reason why the Weimar Republic was in danger in the years 1919–1923: \n • economic problems. \n • political unrest? \n Explain your answer with reference to both bullet points. [12 marks]
            """

                if question_type == 'AQA 16 Marks - How far do you agree? (Paper 1 Section B)':
                    prompt = f"""
                Create {number_questions} questions on {q_topic}. Use the format below.

            Create 1 question on Conflict and tension in Asia, 1950–1975:
            ‘American actions were the main reason for the development of the Korean War.’ \n How far do you agree with this statement? \n Explain your answer. [16 marks] [SPaG 4 marks]

            Create 1 question on Conflict and tension - the First World War,1894–1918:
            ‘The failure of Ludendorff’s Spring Offensive was the main reason for the end of the First World War.’ \n How far do you agree with this statement? \n Explain your answer. [16 marks] [4 SPaG marks]
            """

                if question_type == 'AQA 16 Marks - Case study':
                    prompt = f"""
                Create {number_questions} questions on {q_topic}. Use the format below.

            Create 1 question on Restoration England, 1660–1685:
            ‘The work of Sir Christopher Wren was the main reason for the successful building of St Paul’s Cathedral.’ \n How far does a study of St Paul’s Cathedral support this statement? \n Explain your answer. \n You should refer to St Paul’s Cathedral and your contextual knowledge. [16 marks]

            Create 1 question on Norman England, c1066–c1100: 
            ‘The main reason for castle building during the Norman period was to impress.’ \n How far does a study of the White Tower support this statement? \n Explain your answer. \n You should refer to the White Tower and your contextual knowledge. [16 marks]
            """

                if question_type == 'AQA 16 Marks - Main factor (Paper 2 Section A)':
                    prompt = f"""
                Create {number_questions} questions on {q_topic}. Use the format below.

            Britain - Power and the people - c1170 to the present day:
            Has government been the main factor in improving people’s rights in Britain? \n Explain your answer with reference to government and other factors. \n Use a range of examples from across your study of the topic. [16 marks]

            Britain - Health and the people - c1000 to the present day
            Has war been the main factor in the development of surgery and anatomy? \n Explain your answer with reference to war and other factors.\n  Use a range of examples from across your study of Health and the people: c1000 to the present day. [16 marks]
            """



            
            generate_button = st.button('Generate Qs')
            if generate_button:
                with st.spinner(text="Your questions are in the oven 🧠 ... If you want to work with Pedagogical to improve the app please click [here](https://forms.gle/jDy1WNgrnCTWsDG16) ... Thank you!"):
                    generated_qs = generate_chat_completion(model, prompt)
                    st.markdown(question_type)
                    st.markdown('These Questions were generated using AI and should be treated carefully.')
                    st.markdown(generated_qs)
                
                    credentials = service_account.Credentials.from_service_account_info(
                        st.secrets["gcp_service_account"], scopes = scope)
                    client = Client(scope=scope,creds=credentials)
                    spreadsheetname = st.secrets["private_gsheets_qg_analytics"]
                    spread = Spread(spreadsheetname,client = client)
                    read_df = spread.sheet_to_df(index=False)
                    emails = list(read_df.emails.values)
                    prompts = list(read_df.prompts.values)
                    dates = list(read_df.dates.values)

                    today = datetime.now()
                    emails.append(email)
                    prompts.append(topic)
                    dates.append(today)
                    def update_the_spreadsheet(spreadsheetname,dataframe):
                        spread.df_to_sheet(dataframe,sheet = spreadsheetname,index = False)
                    d = {'emails': emails, 'prompts': prompts, 'dates': dates}
                    df = pd.DataFrame(data=d)
                    update_the_spreadsheet('Sheet1',df)

    else:
    #     exam = st.radio('Exam Boards', ['Edexcel GCSE', 'AQA GCSE'])
    # if exam == 'Edexcel GCSE':
        question_type = st.radio('Question Type', ['Edexcel GCSE 16 Mark', 'Edexcel GCSE 12 Mark Explain'])
        topic = st.radio('Topic', ['crime_and_punishment_in_britain_c1000_present', 'medicine_in_britain_c1250_present', 
        'war_and_british_society_c1250_present', 'migrants_in_britain_c800_present'])
        scope = ['https://spreadsheets.google.com/feeds']

        credentials = service_account.Credentials.from_service_account_info(
                        st.secrets["gcp_service_account"], scopes = scope)
        client = Client(scope=scope,creds=credentials)
        spreadsheetname = st.secrets["gsheets_curricula"]
        spread = Spread(spreadsheetname,client = client)
        df = spread.sheet_to_df(index=False)
        df = df.loc[df['topic'] == topic]
        content = list(df.content.values)
        content_len = len(content)
        pieces = round(content_len/10)
        

        full_question_bank = []
        prompts = []
        
            
        if question_type == 'Edexcel GCSE 12 Mark Explain':
            content_list = split(content, pieces)
            for c in content_list:
                c = " ".join(c)

                prompt = f"""
                The following examples are in the format of topic | Question :

            Changes in medicine and healthcare in Britain in the twentieth century | Explain why there was rapid change in the treatment of illness in Britain during the
                    twentieth century.  \n  You may use the following in your answer: \n 
                    • magic bullets \n 
                    • high-tech treatment \n 
                    You must also use information of your own. \n (12)

            Changes in punishment in 18th to 20th century Britain   |  Explain why there were changes in the prison system in the period c1700–c1900. \n You may use the following in your answer: \n 
            • John Howard \n
            • hard labour \n 
            You must also use information of your own. \n (12)

                Northern Ireland Troubles   |  Explain why the Northern Ireland Troubles had such a significant impact on the lives of ordinary people in the region between 1960 and 1980. You may use the following in your answer: \n 
                • Internment policy \n 
                • British Army presence \n 
                You must also use information of your own. (12) 


            British migration in the 19th and 18th century | Explain why migration to Britain increased during the eighteenth and nineteenth centuries.
            You may use the following in your answer:
            • Industrial Revolution
            • British Empire
            You must also use information of your own. (12)


            Create questions similar to the two examples above but using the following topics. Do not include the topic and begin the questions with 'Explain why':

                {c}
            """
                prompts.append(prompt)

        elif  question_type == 'Edexcel GCSE 16 Mark':
            content_list = split(content, pieces)
            for c in content_list:
                c = " ".join(c)
                prompt = f"""
            The following examples are in the format of topic | Question :

    Witchcraft in Early Modern England | ‘The role of religion was the main reason why there were changes in the number of accusations of witchcraft in the early modern period (c1500–c1700). \n How far do you agree? Explain your answer. \ You may use the following in your answer: 
    - religious beliefs, 
    - Matthew Hopkins \n 
    You must also use information of your own. \n (16)

    Kings in 16th century England | ‘Financial difficulties were the most significant problem faced by Henry in the years 1520–29.’  \n How far do you agree? Explain your answer. \ You may use the following in your answer: 
    - the Amicable Grant 
    - Catherine of Aragon \n 
    You must also use information of your own. \n (16)

    Power in England in the 11th century | ‘The main consequence of William I’s policy of Normanisation was increased control of the Church in England.’  \n How far do you agree? Explain your answer. \ You may use the following in your answer: 
    - bishops
    - landholding \n 
    You must also use information of your own. \n (16)

        Create questions similar to the two examples above but using the following topics. Do not include the topic:

            {c}
        """
                prompts.append(prompt)
        
        generate_button = st.button('Generate Qs')
        if generate_button:
            with st.spinner(text="Your questions are in the oven 🧠 ... This could take several minutes. If you want to work with Pedagogical to improve the app please click [here](https://forms.gle/jDy1WNgrnCTWsDG16) ... Thank you!"):
                for i, prompt_ind in enumerate(prompts):
                    print(i)
                    iteration = i + 1
                    num_prompts = len(prompts)
                    st.text(f"{iteration} of {num_prompts} steps complete")
                    
                    generated_qs = generate_chat_completion(model, prompt_ind)
                    full_question_bank.append(generated_qs)
                st.markdown(question_type)
                st.markdown('These Questions were generated using AI and should be treated carefully.')
                # st.markdown(generated_qs)
                qs_completed = " ".join(full_question_bank)
                st.markdown(qs_completed)
                
                
                # f = open('worksheet.html','w')
                # f.write(qs_completed)
                # f.close()
                # new_parser = HtmlToDocx()
                # new_parser.parse_html_file("worksheet.html", "worksheet")
                # file_path = 'worksheet.docx'
                # with open(file_path,"rb") as f:
                #     base64_word = base64.b64encode(f.read()).decode('utf-8')

                # with open("worksheet.docx", "rb") as word_file:
                #     wordbyte = word_file.read()

                # downloaded = st.download_button(label="Download Word Document", 
                # data=wordbyte,
                # file_name=f"{question_type}_questions.docx",
                # mime='application/octet-stream')

                scope = ['https://spreadsheets.google.com/feeds']

                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"], scopes = scope)
                client = Client(scope=scope,creds=credentials)
                spreadsheetname = st.secrets["private_gsheets_qg_analytics"]
                spread = Spread(spreadsheetname,client = client)
                read_df = spread.sheet_to_df(index=False)
                emails = list(read_df.emails.values)
                prompts = list(read_df.prompts.values)
                dates = list(read_df.dates.values)

                today = datetime.now()
                emails.append(email)
                prompts.append(topic)
                dates.append(today)
                def update_the_spreadsheet(spreadsheetname,dataframe):
                    spread.df_to_sheet(dataframe,sheet = spreadsheetname,index = False)
                d = {'emails': emails, 'prompts': prompts, 'dates': dates}
                df = pd.DataFrame(data=d)
                update_the_spreadsheet('Sheet1',df)

elif subject != 'History':
    st.markdown("This subject is not yet released")

streamlit_analytics.stop_tracking()
