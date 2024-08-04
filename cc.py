import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 应用标题
st.title("订单匹配系统")

# 初始化全局变量
uploaded_file1 = st.file_uploader("上传天美物流表格1", type=["csv", "xlsx"])
uploaded_file2 = st.file_uploader("上传TEMU待发货表格2", type=["csv", "xlsx"])
df1, df2, df3 = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# 上传天美物流表格1
if uploaded_file1 is not None:
    df1 = pd.read_csv(uploaded_file1) if uploaded_file1.name.endswith('.csv') else pd.read_excel(uploaded_file1)
    st.subheader("天美物流表速查")
    
    if st.checkbox("查看全部数据", key="checkbox_df1"):
        page_size = st.number_input("每页显示行数", min_value=1, value=5, step=1)
        total_pages = (len(df1) // page_size) + (len(df1) % page_size > 0)
        page_number = st.number_input("选择页码", min_value=1, max_value=total_pages, value=1)
        start, end = (page_number - 1) * page_size, (page_number - 1) * page_size + page_size
        st.dataframe(df1[['平台', '卖家账号', '跟踪号', '三方订单号', '状态']].iloc[start:end])

    # 统计信息
    unshipped_orders_df1 = df1[df1['跟踪号'].isnull()]['三方订单号'].count()
    st.markdown(f"<h3 style='color: #FF4B4B;'>天美未出单号共计 {unshipped_orders_df1} 订单</h3>", unsafe_allow_html=True)

# 上传TEMU待发货表格2
if uploaded_file2 is not None:
    df2 = pd.read_csv(uploaded_file2) if uploaded_file2.name.endswith('.csv') else pd.read_excel(uploaded_file2)
    st.subheader("TEMU待发货表")
    st.dataframe(df2.head())

    if st.checkbox("查看全部数据", key="checkbox_df2"):
        page_size = st.number_input("每页显示行数", min_value=1, value=5, step=1)
        total_pages = (len(df2) // page_size) + (len(df2) % page_size > 0)
        page_number = st.number_input("选择页码", min_value=1, max_value=total_pages, value=1)
        start, end = (page_number - 1) * page_size, (page_number - 1) * page_size + page_size
        st.dataframe(df2.iloc[start:end])

    # 统计信息
    total_orders_df2 = len(df2)
    total_items_df2 = df2['商品件数'].sum()
    st.markdown(f"<h3 style='color: #4CAF50;'>TEMU待发货共计 {total_orders_df2} 订单</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #4CAF50;'>TEMU待发货共计 {total_items_df2} 商品数量</h3>", unsafe_allow_html=True)

# 当两个表格都上传后进行匹配
if uploaded_file1 is not None and uploaded_file2 is not None:
    st.header("匹配处理结果")
    result = []
    progress_bar = st.progress(0)

    for index, order in df2.iterrows():
        matched_row = df1[df1['参考编号'] == order['订单号']]
        if not matched_row.empty:
            matched_row = matched_row.iloc[0]
            result.append({
                '订单号': order['订单号'],
                '子订单号': order['子订单号'],
                '商品件数': order['商品件数'],
                '跟踪单号': matched_row['跟踪号'],
                '物流承运商': 'USPS'
            })
        progress_bar.progress((index + 1) / len(df2))

    df3 = pd.DataFrame(result)
    st.subheader("新表格3：匹配后的订单信息")
    st.dataframe(df3)

    if st.checkbox("查看匹配结果全部数据", key="checkbox_df3"):
        page_size = st.number_input("每页显示行数", min_value=1, value=5, step=1)
        total_pages = (len(df3) // page_size) + (len(df3) % page_size > 0)
        page_number = st.number_input("选择页码", min_value=1, max_value=total_pages, value=1)
        start, end = (page_number - 1) * page_size, (page_number - 1) * page_size + page_size
        st.dataframe(df3.iloc[start:end])

    # 提供下载新表格3的选项
    export_count = len([f for f in os.listdir('.') if f.startswith('TEMU发货表')])
    export_filename = f"TEMU发货表{datetime.now().strftime('%m%d')}_{export_count+1:03d}.csv"
    csv = df3.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="下载匹配后的订单表格3",
        data=csv,
        file_name=export_filename,
        mime='text/csv',
    )

    # 统计信息
    st.markdown(f"<h3 style='color: #4CAF50;'>TEMU转化表：本次已经匹配到单号共计 {len(df3)} 订单</h3>", unsafe_allow_html=True)
    st.dataframe(df3[['订单号', '跟踪单号', '商品件数']])

# 当只上传表格1时，提供转化按钮
if uploaded_file1 is not None and uploaded_file2 is None:
    if st.button("天美物流表速查"):
        st.subheader("天美物流表速查")
        st.dataframe(df1[['平台', '卖家账号', '跟踪号', '三方订单号', '状态']])

# 页脚
st.markdown("---")
current_year = datetime.now().year
st.markdown("**注意**: 请确保上传的文件格式正确，并包含必要的列，以确保程序正常运行。")
st.markdown(f"**版权 ©️ {current_year} JOOLHOME LLC 好大儿版V1.0**")
