import streamlit as st

st.title("🎯 Ứng Dụng Phân Tích Baccarat")
st.write("Hệ thống soi cầu và dự đoán thông minh.")

# Khởi tạo lịch sử
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

# Thuật toán phân tích dự đoán đơn giản dựa trên cầu gần nhất
st.subheader("🔔 Thông Báo Kết Quả Dự Đoán")
history = st.session_state.history

if len(history) >= 2:
    last_two = history[-2:]
    # Phân tích cầu 1-1 (đảo chiều liên tục)
    if history[-1] != history[-2]:
        prediction = "B" if history[-1] == "P" else "P"
        pattern_name = "Cầu 1-1 (Đảo chiều)"
    # Phân tích cầu bệt (đi theo kết quả gần nhất)
    else:
        prediction = history[-1]
        pattern_name = "Cầu Bệt (Theo chuỗi)"
        
        # Hiển thị thông báo kết quả nổi bật
    if prediction == "P":
        st.error(f"👉 Dự đoán ván tiếp theo: **PLAYER (P)** (Dựa theo {pattern_name})")
    else:
        st.info(f"👉 Dự đoán ván tiếp theo: **BANKER (B)** (Dựa theo {pattern_name})")
else:
    st.warning("⚠️ Vui lòng nhập ít nhất 2 ván để hệ thống bắt đầu nhận diện mẫu cầu.")

st.markdown("---")
st.subheader("📊 Lịch sử các ván:")
if history:
    st.write(" ".join(history))
    
    if st.button("🔄 Xóa lịch sử"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("Chưa có dữ liệu lịch sử.")
