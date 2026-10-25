import streamlit as st
from rag import ask

st.title("Linux Command Line Q&A")
st.caption("Answers come only from the book, with page citations.")

q = st.chat_input("Ask a question about Linux...")
if q:
    st.chat_message("user").write(q)
    with st.spinner("Thinking..."):
        answer, sources = ask(q)
    st.chat_message("assistant").write(answer)
    with st.expander("Sources"):
        for doc, meta in sources:
            st.markdown(f"**Page {meta['page']}**")
            st.text(doc[:300])