import streamlit as st

st.title("🎯 Ứng Dụng Phân Tích Baccarat")
st.write("Chào mừng bạn đến với công cụ phân tích mẫu Baccarat.")

# Khởi tạo lưu trữ lịch sử các ván chơi trong phiên làm việc
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔴 Player (P)", use_container_width=True):
        st.session_state.history.append("P")
with col2:
    if st.button("🔵 Banker (B)", use_container_width=True):
        st.session_state.history.append("B")
with col3:
    if st.button("⚪ Tie (T)", use_container_width=True):
        st.session_state.history.append("T")

st.markdown("---")
st.subheader("📊 Lịch sử các ván:")
if st.session_state.history:
    st.write(" ".join(st.session_state.history))
    
    if st.button("🔄 Xóa lịch sử"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("Chưa có dữ liệu. Hãy bấm chọn kết quả ở trên để bắt đầu ghi nhận.")
