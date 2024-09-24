import streamlit as st
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt
from lime.lime_tabular import LimeTabularExplainer
import xgboost
# 加载模型和数据
model=joblib.load('XGBoost.pkl')
X_test = pd.read_csv('X_test.csv')

# Streamlit 用户界面
st.title("Differentiating Histological Subtypes")

# 用户输入
ITH_score = st.number_input("ITH score:", min_value=0.0, max_value=1.0, value=0.41, step=0.01)
Size = st.number_input("Tumor size:", min_value=0.0, max_value=30.0, value=7.62, step=0.01)
Mean_CT_value = st.number_input("Mean CT value:", min_value=-800.0, max_value=0.0, value=-480.66, step=1.0)
Pleural_indentation = st.selectbox("Pleural indentation:", options=[0, 1], format_func=lambda x: "Absent" if x == 0 else "Present")
Age = st.number_input("Age:", min_value=21.0, max_value=100.0, value=64.0, step=1.0)
Location = st.selectbox("Location:", options=[1, 2, 3, 4, 5], format_func=lambda x: "RUL" if x == 1 else ("RLL" if x == 2 else ("RML" if x == 3 else ("LUL" if x == 4 else "LLL"))))
Shape = st.selectbox("Shape:", options=[0, 1], format_func=lambda x: "Regular" if x == 1 else "Irregular")

# 特征名称
feature_names = ["ITH_score", "Size", "Mean_CT_value", "Pleural_indentation", "Age", "Location", "Shape"]

# 处理输入并进行预测
feature_values = [ITH_score, Size, Mean_CT_value, Pleural_indentation, Age, Location, Shape]
features = np.array([feature_values])

if st.button("Predict"):
    predicted_class = model.predict(features)[0]
    predicted_proba = model.predict_proba(features)[0]

    st.write(f"**Predicted Label**: {predicted_class} (1: Others, 0: LPA)")
    st.write(f"**Predicted Probability**: {predicted_proba}")

    probability = predicted_proba[predicted_class] * 100
    if predicted_class == 1:
        advice = (
            f"根据我们的模型，您有高风险心脏病。"
            f"模型预测您患心脏病的概率为 {probability:.1f}%。"
            "建议您咨询医疗服务提供者以进一步评估和可能的干预。"
        )
    else:
        advice = (
            f"根据我们的模型，您有低风险心脏病。"
            f"模型预测您没有心脏病的概率为 {probability:.1f}%。"
            "但是，保持健康的生活方式仍然很重要。请继续定期检查。"
        )  # 根据预测结果生成建议
    st.write(advice)

    # SHAP 解释
    # st.subheader("SHAP Force Plot Explanation")
    # explainer_shap = shap.TreeExplainer(model)
    # shap_values = explainer_shap.shap_values(pd.DataFrame([feature_values], columns=feature_names))

    # 绘图
    shap.initjs()  # 初始化 SHAP
    
    # shap.force_plot(explainer_shap.expected_value[predicted_class], shap_values[predicted_class], pd.DataFrame([feature_values], columns=feature_names))
    # LIME 解释
    st.subheader("LIME Explanation")
    lime_explainer = LimeTabularExplainer(X_test.values, feature_names=feature_names, class_names=['LPA', 'Others'], mode='classification')
    lime_exp = lime_explainer.explain_instance(features.flatten(), predict_fn=model.predict_proba)
    lime_html = lime_exp.as_html(show_table=False)
    st.components.v1.html(lime_html, height=800, scrolling=True)
