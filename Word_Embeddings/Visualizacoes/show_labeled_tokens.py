import os
import streamlit as st
import pandas as pd
import ast
import uuid

UPLOADED_DATA_FOLDER = 'uploaded_data'
LABELING_FOLDER = 'labeled_data'

if 'current_phrase' not in st.session_state:
    st.session_state.current_phrase = 0

def get_prev_index(csv_path):
    # use the logging file to extract the last index stored for this user and csv file
    full_path = os.path.join(LABELING_FOLDER, csv_path)
    if os.path.exists(full_path):
        print(f'File exists: {full_path}')
        df = pd.read_csv(os.path.join(LABELING_FOLDER, csv_path))
        # filter by the user
        df = df[df['user'] == st.session_state.username]
        # get the last index
        if not df.empty:
            last_index = df['current_phrase'].iloc[-2]
            return last_index
    return 0


def labeling_logic(frame_text, frame, words, metaphors, df, csv_path):
    # empty the frame
    frame.empty()
    frame_text.markdown('Current phrase:'+ ''.join(words), unsafe_allow_html=True)

    # transform the words into a dataframe
    words_df = pd.DataFrame(metaphors, columns=['metaphors'])
    words_df['Correct'] = False
    words_df['Correct'] = words_df['Correct'].astype(bool)

    words_df['Presentism'] = False
    words_df['Presentism'] = words_df['Presentism'].astype(bool)

    words_df['Futurism'] = False
    words_df['Futurism'] = words_df['Futurism'].astype(bool)

    words_df['Pastism'] = False
    words_df['Pastism'] = words_df['Pastism'].astype(bool)

    words_df['Linear'] = False
    words_df['Linear'] = words_df['Linear'].astype(bool)

    words_df['Cyclic'] = False
    words_df['Cyclic'] = words_df['Cyclic'].astype(bool)

    CURRENT_PHRASE = st.session_state.get('current_phrase')

    col_1, col_2, col_3 = frame.columns(3)
    # let the user select the correct or incorrect words
    new_df = col_2.data_editor(words_df, use_container_width=True, key=f'words_df_{CURRENT_PHRASE}')

    # save the dataframe with the correct words
    correct_words = new_df[new_df['Correct'] == True]['metaphors'].tolist()
    incorrect_words = new_df[new_df['Correct'] == False]['metaphors'].tolist()

    logging_info = {
        'filename': csv_path,
        'user': st.session_state.username,
        'date': pd.Timestamp.utcnow(),
        'correct_words': correct_words,
        'incorrect_words': incorrect_words,
        'current_phrase': CURRENT_PHRASE
    }
    # save the logging info to a csv file
    path_to_save = os.path.join(LABELING_FOLDER, csv_path)
    os.makedirs(os.path.dirname(path_to_save), exist_ok=True)
    if not os.path.exists(path_to_save):
        pd.DataFrame.from_dict(logging_info, orient='index').T.to_csv(path_to_save, index=True)
    else:
        pd.DataFrame.from_dict(logging_info, orient='index').T.to_csv(path_to_save, mode='a', header=False, index=True)

    # button_id = uuid.uuid4()
    button_id = CURRENT_PHRASE
    # st.write(f'Current Phrase: {CURRENT_PHRASE}')
    # go to the next phrase
    if col_3.button('Next Phrase', use_container_width=True, key=f'next_phrase_{button_id}'):
        CURRENT_PHRASE = st.session_state.get('current_phrase')
        # st.write(f'{CURRENT_PHRASE=}')
        CURRENT_PHRASE += 1
        st.session_state.current_phrase = CURRENT_PHRASE
        paragraph = df.iloc[CURRENT_PHRASE]
        words, metaphors = do_coloring(paragraph)
        labeling_logic(frame_text, frame, words, metaphors, df, csv_path)

    if col_1.button('Back', use_container_width=True, key=f'back_phrase_{button_id}'):
        CURRENT_PHRASE = st.session_state.get('current_phrase')
        CURRENT_PHRASE -= 1
        st.session_state.current_phrase = CURRENT_PHRASE
        paragraph = df.iloc[CURRENT_PHRASE]
        words, metaphors = do_coloring(paragraph)
        labeling_logic(frame_text, frame, words, metaphors, df, csv_path)

def do_coloring(paragraph):
    add_colour = lambda word, label: f'<span style="color: red">{word}</span>' if label == 'LABEL_1' else f'<span style="color: green">{word}</span>'
    add_grey = lambda word, label: f'<span style="color: grey">{word}</span>'
    metaphors = [ast.literal_eval(x)['word'].replace('Ġ', ' ') for x in paragraph if x != 'nan' and x != '' and type(x) == str and
                 ast.literal_eval(x)['score'] > .95 and ast.literal_eval(x)['entity'] == 'LABEL_1']

    words = [add_colour(
        ast.literal_eval(x)['word'].replace('Ġ', ' '),
        ast.literal_eval(x)['entity']
    ) if ast.literal_eval(x)['score'] > .95 else add_grey(
        ast.literal_eval(x)['word'].replace('Ġ', ' '),
        ast.literal_eval(x)['entity']) for x in paragraph if x != 'nan' and x != '' and type(x) == str]

    return words, metaphors


def main():
    st.title('Data Labelling')
    # let the user select from a list of csv files from 'uploaded_data' folder
    if os.path.exists(UPLOADED_DATA_FOLDER):
        csv_files = os.listdir(UPLOADED_DATA_FOLDER)
        csv_path = st.selectbox('Select a csv file', csv_files)
    else:
        st.warning('No txt files uploaded until now')

    df = pd.read_csv(os.path.join(UPLOADED_DATA_FOLDER, csv_path))
    df = df.iloc[:100]
    # st.write(df)

    if 'current_phrase' not in st.session_state:
        st.session_state.current_phrase = 0
    CURRENT_PHRASE = st.session_state.get('current_phrase')
    paragraph = df.iloc[CURRENT_PHRASE]

    words, metaphors = do_coloring(paragraph)

    # labeling frame
    frame = st.empty()
    frame_text = st.empty()
    prev_index = get_prev_index(csv_path)
    st.markdown('Your previous index was: ' + str(prev_index))
    # set the state of the current phrase
    st.session_state.current_phrase = prev_index

    labeling_logic(frame_text, frame, words, metaphors, df, csv_path)
