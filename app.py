import os
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

BANK_ID = "oncall"
MODEL = "openai/gpt-oss-120b"

st.set_page_config(page_title="On-Call Memory Agent", page_icon="🚨", layout="wide")


@st.cache_resource
def get_clients():
    hs = Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY"),
    )
    gq = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return hs, gq


hindsight, groq_client = get_clients()


def ask_llm(alert, memories):
    if memories:
        mem_text = "\n\n".join(
            f"[Memory {i + 1}]\n{m}" for i, m in enumerate(memories[:8])
        )
        system = (
            "You are an expert on-call incident response assistant. "
            "You are given a new alert and memories of similar past incidents "
            "from this company. Use them. Say which past incident "
            "(by ID, date and service) this resembles, what the root cause was, "
            "what did NOT work last time so we avoid repeating it, and the exact "
            "fix that worked. Then give clear next steps for this alert. "
            "Be specific and concise. If the memories are not relevant, say so."
        )
        user = f"NEW ALERT:\n{alert}\n\nPAST INCIDENT MEMORIES:\n{mem_text}"
    else:
        system = (
            "You are an on-call incident response assistant. "
            "Give a diagnosis and suggested fix for the alert. "
            "Be concise."
        )
        user = f"NEW ALERT:\n{alert}"

    resp = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content


# ---------- Page ----------
st.title("🚨 On-Call Memory Agent")
st.caption("An incident response agent that remembers every past outage and how it was fixed.")

with st.sidebar:
    st.header("Settings")
    use_memory = st.toggle("Use Hindsight memory", value=True)
    st.write("Memory is **ON**" if use_memory else "Memory is **OFF** (generic AI only)")
    st.markdown("---")
    st.write("Bank:", BANK_ID)

alert = st.text_area(
    "Paste the alert or error log",
    height=160,
    placeholder="e.g. notifications-svc: FATAL: remaining connection slots are reserved ...",
)

if st.button("Analyze", type="primary"):
    if not alert.strip():
        st.warning("Please paste an alert first.")
    else:
        memories = []
        if use_memory:
            with st.spinner("Searching Hindsight memory..."):
                try:
                    res = hindsight.recall(bank_id=BANK_ID, query=alert)
                    memories = [r.text for r in res.results]
                except Exception as e:
                    st.error(f"Memory lookup failed: {e}")
        with st.spinner("Thinking..."):
            try:
                answer = ask_llm(alert, memories)
            except Exception as e:
                answer = f"AI call failed: {e}"
        st.session_state["result"] = {
            "alert": alert,
            "answer": answer,
            "memories": memories,
            "used_memory": use_memory,
        }
        st.session_state["saved"] = False

result = st.session_state.get("result")
if result:
    col1, col2 = st.columns([3, 2])
    with col1:
        label = "with memory" if result["used_memory"] else "no memory"
        st.subheader(f"Suggested fix ({label})")
        st.markdown(result["answer"])
    with col2:
        st.subheader("🧠 Memories used")
        if not result["used_memory"]:
            st.info("Memory is off, so nothing was recalled.")
        elif not result["memories"]:
            st.info("No related memories found.")
        else:
            st.success(f"{len(result['memories'])} memories recalled")
            for i, m in enumerate(result["memories"][:8]):
                with st.expander(f"Memory {i + 1}"):
                    st.write(m)

    st.markdown("---")
    st.subheader("✅ Mark as resolved (teach the agent)")
    resolution = st.text_area(
        "How was it actually fixed? What didn't work?",
        key="resolution_box",
        height=100,
    )
    if st.button("Save to memory"):
        if not resolution.strip():
            st.warning("Please describe the fix first.")
        else:
            now = datetime.now(timezone.utc)
            content = (
                f"Incident on {now.strftime('%Y-%m-%d')}\n"
                f"Alert / symptoms: {result['alert']}\n"
                f"Resolution and lessons: {resolution}"
            )
            try:
                hindsight.retain(
                    bank_id=BANK_ID,
                    content=content,
                    context="new production incident and how it was resolved",
                    timestamp=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
                st.success("Saved! The agent will remember this next time.")
            except Exception as e:
                st.error(f"Could not save: {e}")
                