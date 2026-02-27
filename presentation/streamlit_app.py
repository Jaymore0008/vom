# vom/presentation/streamlit_app.py

import streamlit as st
import pandas as pd
import time

from application.cluster_service import ClusterService
from shared.config_loader import ConfigLoader


# --------------------------------------------------
# Page config
# --------------------------------------------------

st.set_page_config(
    page_title="VOM Dashboard",
    page_icon="🖥️",
    layout="wide"
)


# --------------------------------------------------
# Services
# --------------------------------------------------

config = ConfigLoader()
cluster_service = ClusterService()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("Veritas Operations Manager (VOM) Dashboard")


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Controls")

sid_list = config.get_all_sids()

selected_sid = st.sidebar.selectbox(
    "Select SID",
    sid_list
)

refresh = st.sidebar.button("🔄 Refresh")

auto_refresh = st.sidebar.checkbox("Auto Refresh (10s)", value=False)


# Auto refresh logic
if auto_refresh:
    time.sleep(10)
    st.rerun()


# --------------------------------------------------
# Load cluster
# --------------------------------------------------

@st.cache_data(ttl=10)
def load_cluster(sid):
    return cluster_service.get_cluster(sid)


cluster = load_cluster(selected_sid)


# --------------------------------------------------
# Overview panel
# --------------------------------------------------

st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("SID", cluster.sid)

col2.metric(
    "Active Node",
    cluster.active_node if cluster.active_node else "UNKNOWN"
)

col3.metric(
    "Service Groups",
    len(cluster.service_groups)
)

col4.metric(
    "Filesystems",
    len(cluster.filesystems)
)


# --------------------------------------------------
# Node status table
# --------------------------------------------------

st.subheader("Node Status")

node_df = pd.DataFrame(
    [node.to_dict() for node in cluster.nodes]
)

st.dataframe(
    node_df,
    use_container_width=True
)


# --------------------------------------------------
# Health indicator
# --------------------------------------------------

health = cluster.health().value

if health == "HEALTHY":
    st.success("Cluster Health: HEALTHY")

elif health == "WARNING":
    st.warning("Cluster Health: WARNING")

else:
    st.error("Cluster Health: CRITICAL")


# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab_sg, tab_vol, tab_fs, tab_dg = st.tabs([
    "Service Groups",
    "Volumes",
    "Filesystems",
    "Diskgroups"
])


# --------------------------------------------------
# Service Groups tab
# --------------------------------------------------

with tab_sg:

    st.subheader("Service Groups")

    data = []

    for sg in cluster.service_groups:

        for node, state in sg.node_states.items():

            data.append({
                "Service Group": sg.name,
                "Node": node,
                "State": state,
                "Health": sg.health()
            })

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True
    )


# --------------------------------------------------
# Volumes tab
# --------------------------------------------------

with tab_vol:

    st.subheader("Volumes")

    df = pd.DataFrame(
        [v.to_dict() for v in cluster.volumes]
    )

    st.dataframe(
        df,
        use_container_width=True
    )


# --------------------------------------------------
# Filesystems tab
# --------------------------------------------------

with tab_fs:

    st.subheader("Filesystems")

    df = pd.DataFrame(
        [fs.to_dict() for fs in cluster.filesystems]
    )

    st.dataframe(
        df,
        use_container_width=True
    )


# --------------------------------------------------
# Diskgroups tab
# --------------------------------------------------

with tab_dg:

    st.subheader("Diskgroups")

    df = pd.DataFrame(
        [dg.to_dict() for dg in cluster.diskgroups]
    )

    st.dataframe(
        df,
        use_container_width=True
    )


# --------------------------------------------------
# Issues panel
# --------------------------------------------------

st.subheader("Issues")

if cluster.issues:

    df = pd.DataFrame(
        [issue.to_dict() for issue in cluster.issues]
    )

    st.dataframe(df, use_container_width=True)

else:

    st.success("No issues detected")


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption("VOM Dashboard • Powered by Veritas CLI • Streamlit")
