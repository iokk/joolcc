import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 应用标题
st.title("宇宙无敌智能订单处理系统PLUS尊享版")

# 初始化全局变量
uploaded_file1 = st.file_uploader("上传天美物流表格1", type=["csv", "xlsx"])
uploaded_file2 = st.file_uploader("上传TEMU待发货表格2", type=["csv", "xlsx"])
df1, df2, df3 = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# 上传天美物流表格1
if uploaded_file1 is not None:
    df1 = pd.read_csv(uploaded_file1) if uploaded_file1.name.endswith('.csv') else pd.read_excel(uploaded_file1)
    st.subheader("天美物流表速查")
    
    # 统计信息
    unshipped_orders_df1 = df1[df1['跟踪号'].isnull()]['三方订单号'].count()
    st.markdown(f"<h3 style='color: #FF4B4B;'>天美未出单号共计 {unshipped_orders_df1} 订单</h3>", unsafe_allow_html=True)

    # 展示原始物流表格
    if st.button("查看天美物流表"):
        st.dataframe(df1[['平台', '卖家账号', '跟踪号', '三方订单号', '状态']])

# 上传TEMU待发货表格2
if uploaded_file2 is not None:
    df2 = pd.read_csv(uploaded_file2) if uploaded_file2.name.endswith('.csv') else pd.read_excel(uploaded_file2)
    st.subheader("TEMU待发货表")

    # 去除列名中的空格
    df2.columns = df2.columns.str.strip()

    # 打印列名用于调试
    st.write("TEMU待发货表的列名:", df2.columns.tolist())

    # 统计信息
    total_orders_df2 = len(df2)
    total_items_df2 = df2['商品件数'].sum()
    st.markdown(f"<h3 style='color: #4CAF50;'>TEMU待发货共计 {total_orders_df2} 订单</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #4CAF50;'>TEMU待发货共计 {total_items_df2} 商品数量</h3>", unsafe_allow_html=True)

    # 展示TEMU待发货表格
    st.dataframe(df2.head())

# 当两个表格都上传后进行匹配
if uploaded_file1 is not None and uploaded_file2 is not None:
    st.header("匹配处理结果")
    result = []
    progress_bar = st.progress(0)

    for index, order in df2.iterrows():
        order_number = order.get('订单号')  # 使用 get 方法避免 KeyError
        matched_row = df1[df1['参考编号'] == order_number]
        
        if not matched_row.empty:
            matched_row = matched_row.iloc[0]
            # 确保使用正确的列名
            sku_id = order.get('货品SKU ID', None)  # 使用 get 方法避免 KeyError
            result.append({
                '订单号': order_number,
                '子订单号': order.get('子订单号', ''),  # 使用 get 方法避免 KeyError
                '商品SKUID': sku_id,  # 从表格2中获取货品SKU ID
                '商品件数': order.get('商品件数', 0),  # 使用 get 方法避免 KeyError
                '跟踪单号': matched_row.get('跟踪号', ''),  # 从表格1中获取跟踪号
                '物流承运商': 'USPS'
            })
        progress_bar.progress((index + 1) / len(df2))

    df3 = pd.DataFrame(result)
    st.subheader("新表格3：匹配后的订单信息")
    
    if not df3.empty:
        st.markdown(f"<h3 style='color: #4CAF50;'>TEMU转化表：本次已经匹配到单号共计 {len(df3)} 订单</h3>", unsafe_allow_html=True)
        st.dataframe(df3[['订单号', '跟踪单号', '商品件数', '商品SKUID']])

        # 提供下载新表格3的选项
        export_count = len([f for f in os.listdir('.') if f.startswith('TEMU发货表')])
        export_filename = f"TEMU发货表{datetime.now().strftime('%m%d')}_{export_count + 1:03d}.xlsx"
        
        # 将 DataFrame 转换为 Excel 格式并提供下载
        df3.to_excel(export_filename, index=False)
        with open(export_filename, 'rb') as f:
            st.download_button(
                label="下载匹配后的订单表格3",
                data=f,
                file_name=export_filename,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
    else:
        st.markdown("<h3 style='color: #FF4B4B;'>没有匹配到任何订单</h3>", unsafe_allow_html=True)

# 页脚
st.markdown("---")
current_year = datetime.now().year
st.markdown("**注意**: 请确保上传的文件格式正确，并包含必要的列，以确保程序正常运行。")
st.markdown(f"**版权 ©️ {current_year} JOOLHOME LLC 好大儿版V2.0**")
