"""Module rendering progression analytics bars and circular donut tracking milestone gauges."""

import matplotlib.pyplot as plt
import streamlit as st


def render_analytics_dashboard(analytics_logs: list, caloric_target: int, completed_count: int) -> None:
    """Renders progression dashboards utilizing a horizontal fill line bar and custom pie rings."""
    st.write("#### 🎯 Daily Calorie Logging Progression")
    
    progress_percentage = min(1.0, completed_count / max(1, caloric_target))
    st.progress(progress_percentage)
    st.caption(f"You have tracked **{completed_count}** out of an allocated **{caloric_target}** kcal target guideline limit (**{progress_percentage*100:.1f}%** reached).")
    
    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.write("📈 **Weight Tracking Timeline Logs**")
        if not analytics_logs:
            st.info("No timeline logs checked in across this active initialization tracker frame.")
        else:
            dates = [row[0] for row in analytics_logs]
            targets = [row[1] for row in analytics_logs]
            
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(dates, targets, marker='o', linestyle='-', color='#ff7f0e', linewidth=2)
            ax.set_title("Weight Metrics Adjustments History", fontsize=10, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.5)
            plt.xticks(rotation=45, ha='right', fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with col_right:
        st.write("🍩 **Macro Profile Target Milestone Gauge**")
        fig, ax = plt.subplots(figsize=(4, 4))
        remaining = max(0, caloric_target - completed_count)
        
        sizes = [completed_count, remaining]
        colors = ['#d62728', '#e0e0e0'] if completed_count > 0 or remaining > 0 else ['#e0e0e0', '#e0e0e0']
        
        wedges, texts = ax.pie(
            sizes, colors=colors, startangle=90, counterclock=False,
            wedgeprops=dict(width=0.3, edgecolor='white')
        )
        
        pct_text = f"{(completed_count / max(1, caloric_target)) * 100:.0f}%"
        ax.text(0, 0, f"{completed_count}/{caloric_target}\nkcal\n({pct_text})", ha='center', va='center', fontsize=12, fontweight='bold', color='#333333')
        ax.axis('equal')  
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
