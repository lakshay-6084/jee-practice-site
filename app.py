import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="JEE Practice Portal", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "questions_db" not in st.session_state:
    st.session_state.questions_db = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "status" not in st.session_state:
    st.session_state.status = {}
if "test_started" not in st.session_state:
    st.session_state.test_started = False

st.title("JEE-Style Practice Portal")

tab1, tab2 = st.tabs(["Add Questions (Admin)", "Take Test (Student)"])

# ==========================================
# TAB 1: ADD QUESTIONS (Aapka Dashboard)
# ==========================================
with tab1:
    st.header("Add a New Question")
    with st.form("add_question_form", clear_on_submit=True):
        q_text = st.text_area("Question Text")

        col1, col2 = st.columns(2)
        with col1:
            opt_A = st.text_input("Option (A)")
            opt_B = st.text_input("Option (B)")
        with col2:
            opt_C = st.text_input("Option (C)")
            opt_D = st.text_input("Option (D)")

        correct_answer = st.selectbox("Correct Answer", ["(A)", "(B)", "(C)", "(D)"])
        submitted = st.form_submit_button("Add Question to Test")

        if submitted:
            if q_text and opt_A and opt_B and opt_C and opt_D:
                new_q = {
                    "text": q_text,
                    "options": [f"(A) {opt_A}", f"(B) {opt_B}", f"(C) {opt_C}", f"(D) {opt_D}"],
                    "correct": correct_answer
                }
                st.session_state.questions_db.append(new_q)
                idx = len(st.session_state.questions_db) - 1
                st.session_state.status[idx] = 'unanswered'
                st.success("Question added!")

# ==========================================
# TAB 2: TAKE TEST (JEE UI)
# ==========================================
with tab2:
    if len(st.session_state.questions_db) == 0:
        st.warning("Please add some questions in the 'Add Questions' tab first.")
    else:
        col_main, col_sidebar = st.columns([3, 1])

        with col_sidebar:
            st.markdown("### Question Palette")
            st.markdown("**Colors:** 🟢 Answered | 🟣 Review | ⚪ Not Visited | 🔴 Current")

            grid_cols = st.columns(4)
            for i in range(len(st.session_state.questions_db)):
                c_idx = i % 4
                status = st.session_state.status.get(i, 'unanswered')

                marker = "⚪"
                if status == 'answered':
                    marker = "🟢"
                elif status == 'review':
                    marker = "🟣"
                elif status == 'unanswered' and i == st.session_state.current_q:
                    marker = "🔴"

                with grid_cols[c_idx]:
                    if st.button(f"{marker} {i + 1}", key=f"nav_{i}"):
                        st.session_state.current_q = i
                        st.rerun()

            st.markdown("---")
            if st.button("Submit Test", type="primary"):
                st.session_state.test_started = "finished"
                st.rerun()

        with col_main:
            if st.session_state.test_started == "finished":
                st.header("Test Results")
                score = 0
                for i, q in enumerate(st.session_state.questions_db):
                    user_ans_full = st.session_state.responses.get(i, "")
                    user_ans = user_ans_full[:3] if user_ans_full else "Not Attempted"
                    correct_ans = q["correct"]

                    if user_ans == correct_ans:
                        score += 4
                        st.success(f"Q{i + 1}: Correct (+4)")
                    elif user_ans == "Not Attempted":
                        st.info(f"Q{i + 1}: Not Attempted (0)")
                    else:
                        score -= 1
                        st.error(f"Q{i + 1}: Incorrect (-1). You marked {user_ans}, Correct was {correct_ans}")

                st.subheader(f"Total Score: {score}")

                if st.button("Start New Test"):
                    st.session_state.responses = {}
                    for i in range(len(st.session_state.questions_db)):
                        st.session_state.status[i] = 'unanswered'
                    st.session_state.current_q = 0
                    st.session_state.test_started = False
                    st.rerun()

            else:
                curr = st.session_state.current_q
                q_data = st.session_state.questions_db[curr]

                st.subheader(f"Question {curr + 1}")
                st.write(q_data["text"])

                current_response = st.session_state.responses.get(curr, None)
                try:
                    index = q_data["options"].index(current_response) if current_response else None
                except ValueError:
                    index = None

                selected_option = st.radio(
                    "Select an option:",
                    q_data["options"],
                    index=index,
                    key=f"radio_{curr}"
                )

                b_col1, b_col2, b_col3 = st.columns(3)
                with b_col1:
                    if st.button("Save & Next", use_container_width=True, type="secondary"):
                        if selected_option:
                            st.session_state.responses[curr] = selected_option
                            st.session_state.status[curr] = 'answered'
                        if curr < len(st.session_state.questions_db) - 1:
                            st.session_state.current_q += 1
                        st.rerun()
                with b_col2:
                    if st.button("Clear Response", use_container_width=True):
                        if curr in st.session_state.responses:
                            del st.session_state.responses[curr]
                        st.session_state.status[curr] = 'unanswered'
                        st.rerun()
                with b_col3:
                    if st.button("Mark for Review & Next", use_container_width=True):
                        if selected_option:
                            st.session_state.responses[curr] = selected_option
                        st.session_state.status[curr] = 'review'
                        if curr < len(st.session_state.questions_db) - 1:
                            st.session_state.current_q += 1
                        st.rerun()