import streamlit as st
import pandas as pd
import os
from io import BytesIO

# 创建上传和下载目录
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

st.title('Excel Converter')

# 上传文件
uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # 保存上传的文件
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 读取Excel文件
        df = pd.read_excel(file_path)

        # 处理数据
        df_converted = pd.DataFrame({
            "订单号": df["跟踪号"],
            "子订单号": df["参考编号"].str.replace("PO-", ""),
            "商品SKUID": "",
            "商品件数": "",
            "跟踪单号": df["跟踪号"],
            "物流承运商": "USPS"
        })

        # 将处理后的数据转换为Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_converted.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.save()
        processed_file = output.getvalue()

        # 提供下载
        st.download_button(
            label="Download Converted Excel",
            data=processed_file,
            file_name='converted_orders.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.success('File processed successfully!')

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info('Please upload an Excel file.')
