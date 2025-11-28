from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import deepgram
from livekit.plugins import google

import asyncio
import random

from rag_engine import RAGEngine

load_dotenv(".env")

# init RAG
rag = RAGEngine()

# ======================================================================================
#   Conversation State
# ======================================================================================
class BookingState:
    def __init__(self):
        self.started = False
        self.name = None
        self.property_info_given = False
        self.check_in = None
        self.check_out = None


booking_state = BookingState()


# ======================================================================================
#   Agent With Conversation Logic
# ======================================================================================
class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=
"""
You are a friendly Airbnb booking assistant.

REQUIRED BEHAVIOR:
1. Always start with a greeting.
2. Never ask check-in / check-out immediately.
3. If user wants to book → first ask for their NAME.
4. After getting the name → give apartment details from RAG.
5. Then ask for check-in date, then check-out date.
6. Keep responses short and conversational.
"""
        )

    @function_tool
    async def rag_lookup(self, ctx: RunContext, query: str) -> str:
        """Return knowledge retrieved by RAG."""
        return rag.rag_answer(query)

    # ==========================================================
    #   MAIN LOGIC HOOK → AI sees this before generating reply
    # ==========================================================
    async def on_user_message(self, session: AgentSession, text: str):
        text_lower = text.lower()

        # --- GREETING HANDLED AUTOMATICALLY BY ENTRYPOINT ---
        # User wants to book
        if ("book" in text_lower or "reservation" in text_lower) and not booking_state.started:
            booking_state.started = True
            await session.generate_reply(
                instructions="Great! Before we proceed, may I know your name?"
            )
            return

        # --- Capture name ---
        if booking_state.started and booking_state.name is None:
            booking_state.name = text.strip()
            apt_info = rag.rag_answer("apartment details")
            await session.generate_reply(
                instructions=f"Nice to meet you {booking_state.name}! Here are the details of the apartment:\n{apt_info}\nWhen would you like to check in?"
            )
            booking_state.property_info_given = True
            return

        # --- Capture check-in ---
        if booking_state.property_info_given and booking_state.check_in is None:
            booking_state.check_in = text.strip()
            await session.generate_reply(
                instructions="Got it! What is your check-out date?"
            )
            return

        # --- Capture check-out ---
        if booking_state.check_in is not None and booking_state.check_out is None:
            booking_state.check_out = text.strip()
            await session.generate_reply(
                instructions=f"Perfect! I will book the apartment from {booking_state.check_in} to {booking_state.check_out}. Let me know if you'd like to confirm the reservation."
            )
            return

        # --- Default RAG response ---
        await session.generate_reply(
            instructions=f"Here’s what I found:\n{rag.rag_answer(text)}"
        )


# ======================================================================================
#   Backoff
# ======================================================================================
async def safe_generate_reply_backoff(session: AgentSession, instructions: str):
    for attempt in range(5):
        try:
            await session.generate_reply(instructions=instructions)
            return
        except Exception as e:
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"[Retry] {attempt+1}/5 — Error: {e}, retrying in {delay:.1f}s")
            await asyncio.sleep(delay)


# ======================================================================================
#   Entry point
# ======================================================================================
async def entrypoint(ctx: agents.JobContext):

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=deepgram.TTS(model="aura-asteria-en"),
    )

    assistant = Assistant()
    await session.start(room=ctx.room, agent=assistant)

    # FIRST MESSAGE → GREETING
    await safe_generate_reply_backoff(
        session,
        instructions="Hello! I’m your Airbnb assistant. How can I help you today?"
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
