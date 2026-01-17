import streamlit as st
import requests
import time
import streamlit.components.v1 as components

# -----------------------------
# CONFIG
# -----------------------------
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8000")
TOTAL_INTERVIEW_MINUTES = 20
THINKING_TIME_SECONDS = 60
MAX_QUESTIONS = 5

st.set_page_config(page_title="AI Interview", layout="centered")

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
}
.user-bubble {
    background: #dcfce7;
    padding: 14px 18px;
    border-radius: 16px;
    align-self: flex-end;
    max-width: 85%;
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
st.markdown("<p style='text-align:center;color:gray;'>You may speak or type your answer.</p>", unsafe_allow_html=True)

# -----------------------------
# GET candidate_id
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
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.start_time = time.time()
    st.session_state.question = ""
    st.session_state.round = 0
    st.session_state.answer = ""
    st.session_state.chat = []
    st.session_state.spoken = False
    st.session_state.thinking_done = False

# -----------------------------
# TOTAL TIME LIMIT
# -----------------------------
if (time.time() - st.session_state.start_time) / 60 > TOTAL_INTERVIEW_MINUTES:
    st.error("⏰ Interview time limit exceeded")
    st.stop()

# -----------------------------
# START INTERVIEW
# -----------------------------
if not st.session_state.started:
    if st.button("🚀 Start Interview"):
        r = requests.post(
            f"{BACKEND_URL}/candidates/{candidate_id}/start-interview",
            timeout=60
        )
        data = r.json()

        st.session_state.started = True
        st.session_state.question = data["question"]
        st.session_state.round = 1
        st.session_state.chat.append(("ai", data["question"]))
        st.session_state.spoken = False
        st.rerun()

# -----------------------------
# PROGRESS
# -----------------------------
if st.session_state.started:
    st.progress(st.session_state.round / MAX_QUESTIONS)

# -----------------------------
# CHAT UI
# -----------------------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for role, msg in st.session_state.chat:
    if role == "ai":
        st.markdown(f"<div class='ai-bubble'><b>AI:</b><br>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='user-bubble'><b>You:</b><br>{msg}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# TTS (SPEAK ONLY ONCE)
# -----------------------------
if st.session_state.started and not st.session_state.spoken:
    components.html(f"""
    <script>
      const msg = new SpeechSynthesisUtterance("{st.session_state.question}");
      msg.lang = 'en-US';
      speechSynthesis.cancel();
      speechSynthesis.speak(msg);
    </script>
    """, height=0)
    st.session_state.spoken = True

# -----------------------------
# THINKING TIMER
# -----------------------------
if not st.session_state.thinking_done:
    timer = st.empty()
    for i in range(THINKING_TIME_SECONDS, 0, -1):
        timer.markdown(f"<div class='timer-box'>⏳ Think: {i}s</div>", unsafe_allow_html=True)
        time.sleep(1)
    timer.empty()
    st.session_state.thinking_done = True

# -----------------------------
# STT – MIC
# -----------------------------
components.html("""
<script>
function startMic() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Speech Recognition not supported in this browser.");
    return;
  }
  const recognition = new webkitSpeechRecognition();
  recognition.lang = "en-US";
  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    window.parent.postMessage({type: "speech", text}, "*");
  };
  recognition.start();
}
</script>
<button class="mic-btn" onclick="startMic()">🎤 Speak Answer</button>
""", height=80)

# Receive STT text
speech = st.experimental_get_query_params()
if "speech" in speech:
    st.session_state.answer += " " + speech["speech"][0]

# -----------------------------
# ANSWER INPUT
# -----------------------------
st.session_state.answer = st.text_area(
    "Your Answer",
    value=st.session_state.answer,
    height=120
)

# -----------------------------
# SUBMIT ANSWER
# -----------------------------
if st.button("Submit Answer"):
    if not st.session_state.answer.strip():
        st.warning("Please answer before submitting")
        st.stop()

    st.session_state.chat.append(("user", st.session_state.answer))

    r = requests.post(
        f"{BACKEND_URL}/candidates/{candidate_id}/answer",
        data={"answer": st.session_state.answer},
        timeout=120
    )

    data = r.json()

    if "evaluation" in data:
        st.success("✅ Interview Completed")
        st.markdown(f"""
        <div class='ai-bubble'>
        <b>Final Score:</b> {data['evaluation']['final_score']}<br><br>
        <b>Recommendation:</b> {data['evaluation']['recommendation']}<br><br>
        <b>Feedback:</b><br>{data['evaluation']['feedback']}
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Next question
    st.session_state.question = data["question"]
    st.session_state.round += 1
    st.session_state.chat.append(("ai", data["question"]))
    st.session_state.answer = ""
    st.session_state.spoken = False
    st.session_state.thinking_done = False
    st.rerun()
