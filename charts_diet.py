"""Module rendering progression analytics bars and circular donut tracking milestone gauges."""

import matplotlib.pyplot as plt
import streamlit as st


def render_analytics_dashboard(analytics_logs: list, caloric_target: int, completed_count: int, macro_data: dict) -> None:
    """Renders progression dashboards including target milestone gauges and a macro distribution chart."""
    st.write("#### 🎯 Daily Calorie Logging Progression")
    
    progress_percentage = min(1.0, completed_count / max(1, caloric_target))
    st.progress(progress_percentage)
    st.caption(f"You have tracked **{completed_count}** out of an allocated **{caloric_target}** kcal target guideline limit (**{progress_percentage*100:.1f}%** reached).")
    
    st.markdown("---")
    col_left, col_mid, col_right = st.columns(3) # Expanded to 3 structural grid columns
    
    with col_left:
        st.write("📈 **Weight Tracking Timeline**")
        if not analytics_logs:
            st.info("No timeline logs checked in across this active tracking session.")
        else:
            dates = [row[0] for row in analytics_logs]
            targets = [row[1] for row in analytics_logs]
            
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.plot(dates, targets, marker='o', linestyle='-', color='#ff7f0e', linewidth=2)
            ax.set_title("Weight Metrics Adjustment History", fontsize=10, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.5)
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with col_mid:
        st.write("🍩 **Target Milestone Gauge**")
        fig, ax = plt.subplots(figsize=(4, 4))
        remaining = max(0, caloric_target - completed_count)
        
        sizes = [completed_count, remaining]
        colors = ['#d62728', '#e0e0e0'] if completed_count > 0 or remaining > 0 else ['#e0e0e0', '#e0e0e0']
        
        ax.pie(
            sizes, colors=colors, startangle=90, counterclock=False,
            wedgeprops=dict(width=0.3, edgecolor='white')
        )
        
        pct_text = f"{(completed_count / max(1, caloric_target)) * 100:.0f}%"
        ax.text(0, 0, f"{completed_count}/{caloric_target}\nkcal\n({pct_text})", ha='center', va='center', fontsize=11, fontweight='bold', color='#333333')
        ax.axis('equal')  
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_right:
        st.write("📊 **Macronutrient Split Ratio**")
        
        # ─── NEW: INTERACTIVE PIE CHART DISPLAYING PROTEIN, CARBS, AND FATS RATIO ───
        p, c, f = macro_data["protein"], macro_data["carbs"], macro_data["fats"]
        
        if p == 0 and c == 0 and f == 0:
            st.info("Edit your logged meal macros below and add values like 'P:30g, C:50g, F:15g' to visualize splits!")
        else:
            labels = [f"Protein ({p}g)", f"Carbs ({c}g)", f"Fats ({f}g)"]
            sizes = [p * 4, c * 4, f * 9] # Standard nutritional energy weight mapping: 4kcal/g for P/C, 9kcal/g for F
            colors = ['#1f77b4', '#9467bd', '#bcbd22']
            
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(
                sizes, 
                labels=labels, 
                colors=colors, 
                autopct='%1.1f%%', 
                startangle=140,
                textprops={'fontsize': 9}
            )
            ax.axis('equal')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
