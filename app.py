import base64
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from simulation import MonthlyTumorSimulation


st.set_page_config(
    page_title="نظام سهيل للاختبارات العلاجية",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
        <h1>🧬 نظام سهيل للاختبارات العلاجية</h1>
        <p style='font-size: 1.2em;'>محاكاة استجابة الورم للعلاج الكيميائي والمناعي والغذائي</p>
        <p style='font-size: 0.9em; opacity: 0.8;'>Suhail Therapeutic Testing System v1.0</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.warning("⚠️ هذه المحاكاة لأغراض بحثية/تعليمية فقط وليست أداة تشخيص أو وصف علاج طبي.")


@st.cache_resource
def get_simulator():
    return MonthlyTumorSimulation()


sim = get_simulator()

with st.sidebar:
    st.markdown("## 📊 معاملات الورم")
    st.markdown("### القيم الابتدائية")

    col1, col2 = st.columns(2)
    with col1:
        S_initial = st.number_input(
            "الخلايا الحساسة (S)",
            min_value=0.1,
            max_value=50.0,
            value=4.0,
            step=0.5,
            help="عدد الخلايا الحساسة للعلاج في بداية المحاكاة",
        )
        R_initial = st.number_input(
            "الخلايا المقاومة (R)",
            min_value=0.1,
            max_value=50.0,
            value=2.0,
            step=0.5,
            help="عدد الخلايا المقاومة للعلاج في بداية المحاكاة",
        )
    with col2:
        D_initial = st.number_input(
            "الخلايا الساكنة (D)",
            min_value=0.1,
            max_value=50.0,
            value=4.0,
            step=0.5,
            help="عدد الخلايا الساكنة في بداية المحاكاة",
        )
        K_capacity = st.number_input(
            "سعة الورم القصوى (K)",
            min_value=5.0,
            max_value=50.0,
            value=15.0,
            step=1.0,
            help="الحجم الأقصى الذي يمكن للورم بلوغه",
        )

    st.markdown("### معاملات النمو")
    col1, col2 = st.columns(2)
    with col1:
        G_S = st.number_input(
            "معدل نمو S", min_value=0.001, max_value=0.1, value=0.0250, step=0.001, format="%.4f"
        )
        G_R = st.number_input(
            "معدل نمو R", min_value=0.001, max_value=0.1, value=0.0150, step=0.001, format="%.4f"
        )
    with col2:
        G_D = st.number_input(
            "معدل نمو D", min_value=0.0001, max_value=0.01, value=0.0020, step=0.0001, format="%.4f"
        )
        T_rate = st.number_input(
            "معدل تحول S→R", min_value=0.0001, max_value=0.01, value=0.0015, step=0.0001, format="%.4f"
        )

    st.markdown("### معاملات العلاج")
    col1, col2 = st.columns(2)
    with col1:
        dose_amount = st.number_input(
            "جرعة الدواء",
            min_value=0.0,
            max_value=0.2,
            value=0.04,
            step=0.005,
            format="%.3f",
            help="كمية الدواء في كل جرعة",
        )
        EC50 = st.number_input(
            "نصف الجرعة الفعالة (EC50)",
            min_value=0.001,
            max_value=0.2,
            value=0.04,
            step=0.001,
            format="%.3f",
        )
    with col2:
        n_hill = st.number_input(
            "معامل هيل", min_value=0.5, max_value=5.0, value=2.0, step=0.1, help="يحدد حدة استجابة الخلايا للدواء"
        )
        L_R = st.number_input(
            "تأثير الغذاء على R", min_value=0.0, max_value=0.5, value=0.10, step=0.01, format="%.2f"
        )

    st.markdown("### معاملات المناعة")
    col1, col2 = st.columns(2)
    with col1:
        ME = st.number_input(
            "تجنيد المناعة", min_value=0.0, max_value=0.05, value=0.015, step=0.001, format="%.3f"
        )
        C_G_I = st.number_input(
            "تثبيط المناعة بالكيمائي", min_value=0.0, max_value=0.3, value=0.12, step=0.01, format="%.2f"
        )
    with col2:
        N_G_I = st.number_input(
            "تحفيز المناعة بالغذاء", min_value=0.0, max_value=0.1, value=0.03, step=0.005, format="%.3f"
        )
        G_T_G_I = st.number_input(
            "تحفيز المناعة بحجم الورم", min_value=0.0, max_value=0.02, value=0.004, step=0.001, format="%.3f"
        )

    st.markdown("### إعدادات المحاكاة")
    col1, col2 = st.columns(2)
    with col1:
        simulation_days = st.slider("مدة المحاكاة (أيام)", min_value=10, max_value=120, value=30, step=5)
    with col2:
        pink_intensity = st.slider(
            "🌸 شدة البيئة الوردية",
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="0 = معطل، 1 = فعال، 2 = مكثف",
        )

    st.markdown("### أيام الجرعات")
    dose_days_input = st.text_input(
        "أيام الجرعات (مفصولة بفواصل)",
        value="1, 8, 15, 22",
        help="أدخل أرقام الأيام التي سيتم فيها إعطاء العلاج، مفصولة بفواصل",
    )

    st.markdown("---")
    run_button = st.button("▶️ تشغيل المحاكاة", use_container_width=True, type="primary")


if run_button:
    try:
        dose_days = [int(x.strip()) for x in dose_days_input.split(",") if x.strip()]
        dose_days = sorted({d for d in dose_days if 1 <= d <= simulation_days})

        sim.G_S = G_S
        sim.G_R = G_R
        sim.G_D = G_D
        sim.T = T_rate
        sim.K = K_capacity
        sim.EC50 = EC50
        sim.n_hill = n_hill
        sim.L_R = L_R
        sim.ME = ME
        sim.C_G_I = C_G_I
        sim.N_G_I = N_G_I
        sim.G_T_G_I = G_T_G_I

        sim.S_initial = S_initial
        sim.R_initial = R_initial
        sim.D_initial = D_initial

        sim.simulation_days = simulation_days
        sim.dose_days = dose_days
        sim.dose_amount = dose_amount
        sim.pink_intensity = pink_intensity

        with st.spinner("🔄 جاري تشغيل المحاكاة..."):
            results = sim.run_simulation()

        df = pd.DataFrame(results)

        st.markdown("## 📈 نتائج المحاكاة")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "📊 الحجم النهائي للورم",
                f"{df['total'].iloc[-1]:.2f}",
                delta=f"{((df['total'].iloc[-1] - df['total'].iloc[0]) / df['total'].iloc[0] * 100):.1f}%",
            )
        with col2:
            st.metric("🧬 نسبة المقاومة النهائية", f"{(df['R'].iloc[-1] / df['total'].iloc[-1] * 100):.1f}%")
        with col3:
            st.metric("🛡️ متوسط المناعة", f"{df['I'].mean():.2f}")
        with col4:
            dose_count = int(df["is_dose_day"].sum())
            st.metric(
                "💊 أيام الجرعات",
                f"{dose_count}",
                delta=f"{pink_intensity:.1f} 🌸" if pink_intensity > 0 else "بدون بيئة وردية",
            )

        st.markdown("---")
        st.markdown("### 📉 تطور الورم")

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("تطور الخلايا", "حجم الورم الكلي", "نسبة المقاومة", "الجهاز المناعي"),
            vertical_spacing=0.15,
            horizontal_spacing=0.15,
        )

        fig.add_trace(go.Scatter(x=df["day"], y=df["S"], name="S (حساسة)", line=dict(color="#00cc96", width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["day"], y=df["R"], name="R (مقاومة)", line=dict(color="#ef553b", width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["day"], y=df["D"], name="D (ساكنة)", line=dict(color="#636efa", width=2, dash="dash")), row=1, col=1)

        dose_days_df = df[df["is_dose_day"]]
        if not dose_days_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=dose_days_df["day"],
                    y=dose_days_df["total"],
                    mode="markers",
                    name="💊 جرعة",
                    marker=dict(symbol="star", size=12, color="#ff7f0e"),
                ),
                row=1,
                col=1,
            )

        fig.add_trace(go.Scatter(x=df["day"], y=df["total"], name="الحجم الكلي", line=dict(color="#ff7f0e", width=3)), row=1, col=2)
        fig.add_hline(y=K_capacity, line_dash="dash", line_color="red", row=1, col=2, annotation_text="K (السعة القصوى)")

        resistance_ratio = df["R"] / df["total"] * 100
        fig.add_trace(go.Scatter(x=df["day"], y=resistance_ratio, name="نسبة المقاومة %", line=dict(color="#ef553b", width=2)), row=2, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="gray", row=2, col=1, annotation_text="50%")

        fig.add_trace(go.Scatter(x=df["day"], y=df["I"], name="المناعة", line=dict(color="#00cc96", width=2)), row=2, col=2)

        fig.update_layout(height=600, showlegend=True, template="plotly_white")
        for row in (1, 2):
            for col in (1, 2):
                fig.update_xaxes(title_text="اليوم", row=row, col=col)

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 عرض الجدول الكامل للنتائج"):
            display_df = df.copy()
            display_df["💊 جرعة"] = display_df["is_dose_day"].apply(lambda x: "✅" if x else "")
            display_df = display_df.drop(columns=["is_dose_day"])
            st.dataframe(
                display_df,
                column_config={
                    "day": "اليوم",
                    "S": "الخلايا الحساسة",
                    "R": "الخلايا المقاومة",
                    "D": "الخلايا الساكنة",
                    "total": "الحجم الكلي",
                    "I": "المناعة",
                    "💊 جرعة": "جرعة",
                    "chemo_effect": "تأثير الكيمائي",
                    "hypoxia": "نقص الأكسجين",
                    "resistance": "مقاومة العلاج",
                },
                use_container_width=True,
                height=400,
            )

        st.markdown("### 📊 تحليل النتائج")
        col1, col2 = st.columns(2)

        initial_total = df["total"].iloc[0]
        final_total = df["total"].iloc[-1]
        change_pct = (final_total - initial_total) / initial_total * 100
        final_resistance = df["R"].iloc[-1] / df["total"].iloc[-1] * 100

        with col1:
            st.markdown("**تغيرات الورم:**")
            if change_pct < -30:
                st.success(f"✅ حسب النموذج: تقلص كبير بنسبة {abs(change_pct):.1f}%")
            elif change_pct < -10:
                st.info(f"📈 حسب النموذج: تقلص بنسبة {abs(change_pct):.1f}%")
            elif change_pct < 10:
                st.warning(f"⚖️ حسب النموذج: تغير محدود ({change_pct:.1f}%)")
            else:
                st.error(f"⚠️ حسب النموذج: زيادة بنسبة {change_pct:.1f}%")

            if final_resistance < 20:
                st.success(f"✅ مقاومة نموذجية منخفضة ({final_resistance:.1f}%)")
            elif final_resistance < 50:
                st.info(f"📈 مقاومة نموذجية متوسطة ({final_resistance:.1f}%)")
            else:
                st.error(f"⚠️ مقاومة نموذجية مرتفعة ({final_resistance:.1f}%)")

        with col2:
            st.markdown("**ملاحظة تفسيرية:**")
            st.info("النتائج ناتجة عن النموذج الرياضي فقط، ولا ينبغي استخدامها لاتخاذ قرار علاجي أو تعديل جرعة دواء حقيقية.")
            if pink_intensity > 0:
                st.success(f"🌸 البيئة الوردية مفعلة في النموذج (شدة {pink_intensity:.1f})")

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        with col1:
            csv_data = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 تحميل CSV",
                data=csv_data,
                file_name=f"نتائج_المحاكاة_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col2:
            json_data = df.to_json(orient="records", indent=2, force_ascii=False).encode("utf-8")
            st.download_button(
                "📥 تحميل JSON",
                data=json_data,
                file_name=f"نتائج_المحاكاة_{timestamp}.json",
                mime="application/json",
                use_container_width=True,
            )

        with col3:
            html_content = f"""
            <html lang="ar" dir="rtl">
            <head><meta charset="UTF-8"><title>نتائج المحاكاة</title></head>
            <body>
                <h1>نظام سهيل للاختبارات العلاجية</h1>
                <h2>نتائج المحاكاة - {datetime.now().strftime('%Y-%m-%d %H:%M')}</h2>
                {df[["day", "S", "R", "D", "total", "I"]].to_html(index=False)}
                <p>نسبة التغير: {change_pct:.1f}%</p>
                <p>نسبة المقاومة النهائية: {final_resistance:.1f}%</p>
                <p><strong>تنبيه:</strong> هذه النتائج لأغراض بحثية/تعليمية فقط.</p>
            </body>
            </html>
            """
            st.download_button(
                "📥 تحميل HTML",
                data=html_content.encode("utf-8"),
                file_name=f"نتائج_المحاكاة_{timestamp}.html",
                mime="text/html",
                use_container_width=True,
            )

        st.caption("💡 افتح ملف HTML في المتصفح ثم استخدم طباعة → حفظ كـ PDF.")

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تشغيل المحاكاة: {str(e)}")
        st.info("تأكد من أن أيام الجرعات مدخلة بشكل صحيح، مثال: 1, 8, 15, 22")

else:
    st.info("👈 قم بتعديل المعاملات في الشريط الجانبي، ثم اضغط على 'تشغيل المحاكاة'")
    st.markdown(
        """
        ### 📖 دليل سريع للاستخدام

        1. أدخل معاملات النموذج في الشريط الجانبي.
        2. حدد أيام الجرعات مثل: `1, 8, 15, 22`.
        3. فعّل البيئة الوردية إذا كانت جزءاً من التجربة النموذجية.
        4. اضغط **تشغيل المحاكاة**.
        5. راجع الرسوم والجدول ثم حمّل النتائج.

        ### 🧬 المؤشرات

        | المؤشر | المعنى داخل النموذج |
        |---|---|
        | **S** | الخلايا الحساسة للعلاج |
        | **R** | الخلايا المقاومة للعلاج |
        | **D** | الخلايا الساكنة |
        | **المناعة** | متغير يمثل الاستجابة المناعية في النموذج |
        | **نسبة المقاومة** | نسبة R من الحجم الكلي للنموذج |
        """
    )

st.markdown("---")
st.caption("© 2026 نظام سهيل للاختبارات العلاجية - نسخة بحثية/تعليمية")
