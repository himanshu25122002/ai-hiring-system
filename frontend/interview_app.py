import streamlit as st
import requests
import time
import streamlit.components.v1 as components

# -----------------------------
# CONFIG
# -----------------------------
BACKEND_URL = "http://127.0.0.1:8000"
TOTAL_INTERVIEW_MINUTES = 20
THINKING_TIME_SECONDS = 60
MAX_QUESTIONS = 5

st.set_page_config(
    page_title="AI Interview",
    layout="centered"
)

# -----------------------------
# GLOBAL STYLES (CHAT UI)
# -----------------------------
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.ai-bubble {
    background: #eef2ff;
    padding: 14px 18px;
    border-radius: 16px;
    max-width: 85%;
    animation: fadeIn 0.5s ease-in;
}

.user-bubble {
    background: #dcfce7;
    padding: 14px 18px;
    border-radius: 16px;
    align-self: flex-end;
    max-width: 85%;
    animation: slideIn 0.4s ease-in;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(-5px);}
    to {opacity: 1; transform: translateY(0);}
}

@keyframes slideIn {
    from {opacity: 0; transform: translateX(10px);}
    to {opacity: 1; transform: translateX(0);}
}

.timer-box {
    background: #fff7ed;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
}

.mic-btn {
    padding: 10px 18px;
    font-size: 16px;
    border-radius: 25px;
    background: #4f46e5;
    color: white;
    border: none;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown("<h2 style='text-align:center;'>🎤 AI Interview</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Answer naturally — speak or type.</p>", unsafe_allow_html=True)

# -----------------------------
# READ candidate_id
# -----------------------------
candidate_id = st.query_params.get("candidate_id")
if isinstance(candidate_id, list):
    candidate_id = candidate_id[0]

if not candidate_id:
    st.error("Invalid interview link")
    st.stop()

# -----------------------------
# SESSION STATE
# -----------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
    st.session_state.question = None
    st.session_state.q_count = 0
    st.session_state.answer = ""
    st.session_state.thinking_done = False
    st.session_state.chat = []

# -----------------------------
# TOTAL TIME LIMIT (20 MIN)
# -----------------------------
elapsed = (time.time() - st.session_state.start_time) / 60
if elapsed > TOTAL_INTERVIEW_MINUTES:
    st.error("⏰ Interview time limit exceeded")
    st.stop()

# -----------------------------
# START INTERVIEW
# -----------------------------
if st.session_state.question is None:
    res = requests.post(f"{BACKEND_URL}/candidates/{candidate_id}/start-interview")
    st.session_state.question = res.json()["question"]
    st.session_state.q_count = 1
    st.session_state.chat.append(("ai", st.session_state.question))

# -----------------------------
# PROGRESS BAR
# -----------------------------
st.progress(st.session_state.q_count / MAX_QUESTIONS)

# -----------------------------
# CHAT DISPLAY
# -----------------------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for role, msg in st.session_state.chat:
    if role == "ai":
        st.markdown(f"<div class='ai-bubble'><b>AI:</b><br>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='user-bubble'><b>You:</b><br>{msg}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# TTS – AI SPEAKS
# -----------------------------
components.html(
    f"""
    <script>
      const msg = new SpeechSynthesisUtterance(`{st.session_state.question}`);
      msg.lang = 'en-US';
      speechSynthesis.cancel();
      speechSynthesis.speak(msg);
    </script>
    """,
    height=0
)

# -----------------------------
# THINKING TIMER
# -----------------------------
if not st.session_state.thinking_done:
    timer = st.empty()
    for i in range(THINKING_TIME_SECONDS, 0, -1):
        timer.markdown(f"<div class='timer-box'>⏳ Thinking time: {i}s</div>", unsafe_allow_html=True)
        time.sleep(1)
    timer.empty()
    st.session_state.thinking_done = True

# -----------------------------
# STT – MIC BUTTON
# -----------------------------
components.html(
    """
    <script>
    let recognition;
    function startMic() {
        recognition = new webkitSpeechRecognition();
        recognition.lang = "en-US";
        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            window.parent.postMessage({ answer: text }, "*");
        };
        recognition.start();
    }
    </script>

    <button class="mic-btn" onclick="startMic()">🎤 Speak Answer</button>
    """,
    height=80
)

# -----------------------------
# ANSWER INPUT
# -----------------------------
answer = st.text_area(
    "Your Answer",
    value=st.session_state.answer,
    height=120
)
st.session_state.answer = answer

# -----------------------------
# SUBMIT ANSWER
# -----------------------------
if st.button("Submit Answer"):
    if not answer.strip():
        st.warning("Please provide an answer.")
        st.stop()

    st.session_state.chat.append(("user", answer))

    res = requests.post(
        f"{BACKEND_URL}/candidates/{candidate_id}/answer",
        params={"answer": answer}
    )

    data = res.json()

    if "next_question" in data:
        st.session_state.question = data["next_question"]
        st.session_state.q_count += 1
        st.session_state.chat.append(("ai", st.session_state.question))
        st.session_state.answer = ""
        st.session_state.thinking_done = False
        st.rerun()
    else:
        st.success("✅ Interview Completed")
        st.markdown(
            f"""
            <div class='ai-bubble'>
            <b>Final Score:</b> {data.get("score")}<br><br>
            <b>Feedback:</b><br>{data.get("feedback")}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.stop()
