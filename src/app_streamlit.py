"""
Streamlit UI for Northwind Support Co-pilot.
"""

import streamlit as st
import json
from pathlib import Path

from src.llm_client import get_llm_client
from src.pipeline import run_pipeline


def main():
    st.set_page_config(
        page_title="Northwind Support Co-pilot",
        page_icon="🤖",
        layout="wide",
    )

    st.title("🤖 Northwind Support Co-pilot")
    st.markdown(
        """
    A 4-stage prompt pipeline that turns support tickets into policy-grounded replies.
    """
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Ticket Input")
        ticket_id = st.text_input("Ticket ID", value="manual-1", key="ticket_id")
        raw_ticket = st.text_area(
            "Paste ticket text",
            height=150,
            placeholder="Customer name: John\nOrder ID: ORD-123\nIssue: Refund requested...",
        )

    with col2:
        st.subheader("⚙️ Settings")
        use_api = st.checkbox("Use OpenAI API", value=False)
        run_button = st.button("🚀 Process Ticket", key="run_btn")

    if run_button and raw_ticket:
        st.info("Processing ticket through 4-stage pipeline...")

        try:
            # Get LLM client
            if use_api:
                from src.llm_client import OpenAIClient
                llm_client = OpenAIClient()
            else:
                from src.llm_client import ManualClient
                llm_client = ManualClient()

            # Run pipeline
            result = run_pipeline(
                ticket_id,
                raw_ticket,
                llm_client,
                save_output=False,  # Don't save to file in UI
            )

            # Display results
            st.success("✅ Pipeline completed!")

            # Stage 1
            with st.expander("Stage 1: Classify", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("Category", result.stage1_output.category)
                col2.metric("Confidence", f"{result.stage1_output.confidence:.2f}")
                col3.write(f"**Reason:** {result.stage1_output.reason}")

            # Stage 2
            with st.expander("Stage 2: Extract", expanded=True):
                st.json(result.stage2_output.dict())

            # Stage 3
            with st.expander("Stage 3: Ground in Policy", expanded=True):
                col1, col2 = st.columns([1, 2])
                col1.metric("Behavior", result.stage3_output.behavior)
                col2.write(f"**Citations:** {', '.join(result.stage3_output.citations)}")
                st.markdown("**Reply:**")
                st.write(result.stage3_output.reply_text)

            # Stage 4
            with st.expander("Stage 4: Critique", expanded=True):
                if result.stage4_output.issues_found:
                    st.warning("⚠️ Issues found:")
                    for issue in result.stage4_output.issues_found:
                        st.write(f"• {issue}")
                else:
                    st.success("✅ No issues found")
                st.markdown("**Final Reply:**")
                st.write(result.stage4_output.final_reply)

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Test set selector
    st.divider()
    st.subheader("📊 Quick Test")

    test_set_path = Path("data/test_set.json")
    if test_set_path.exists():
        test_data = json.loads(test_set_path.read_text())
        tickets = test_data.get("tickets", [])

        ticket_options = {
            f"#{t['id']} - {t['raw_ticket'][:50]}...": t for t in tickets
        }

        selected = st.selectbox("Load a test ticket:", list(ticket_options.keys()))
        if selected:
            test_ticket = ticket_options[selected]
            st.text_area(
                "Loaded ticket:",
                value=test_ticket["raw_ticket"],
                disabled=True,
                height=100,
            )


if __name__ == "__main__":
    main()
