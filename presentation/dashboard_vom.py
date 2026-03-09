# vom/presentation/dashboard_vom.py

import streamlit as st

from application.services.cluster_service import ClusterService
from domain.monitoring.issue import IssueSeverity

st.set_page_config(
    page_title="Infrastructure Monitoring",
    layout="wide"
)

st.title("Infrastructure Monitoring Dashboard")

cluster_service = ClusterService()

# --------------------------------------------------
# Session state
# --------------------------------------------------

if "cluster" not in st.session_state:
    st.session_state.cluster = None

# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab1, = st.tabs(["VOM Cluster"])

with tab1:

    st.header("Veritas Cluster Monitoring")

    cluster_sid = st.sidebar.selectbox(
        "Cluster SID",
        cluster_service.config.get_all_sids()
    )

    # --------------------------------------------------
    # Refresh Button
    # --------------------------------------------------

    if st.button("Refresh Cluster") and cluster_sid is not None:

        with st.spinner("Collecting cluster data..."):

            st.session_state.cluster = cluster_service.collect_cluster(cluster_sid)

    cluster = st.session_state.cluster

    if not cluster:
        st.info("Click 'Refresh Cluster' to load cluster data.")
        st.stop()

    summary = cluster.summary()

    # --------------------------------------------------
    # Summary metrics
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Cluster", summary["sid"])
    col2.metric("Health", summary["health"])
    col3.metric("Nodes", summary["node_count"])
    col4.metric("Service Groups", summary["service_group_count"])

    st.divider()

    # --------------------------------------------------
    # Issues
    # --------------------------------------------------

    st.subheader("Cluster Issues")

    if not cluster.issues:
        st.success("No issues detected")

    else:
        for issue in cluster.issues:

            if issue.severity == IssueSeverity.CRITICAL:
                st.error(issue.message)
            else:
                st.warning(issue.message)

    st.divider()

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    st.subheader("Cluster Nodes")

    node_rows = []

    for node in cluster.nodes:

        node_rows.append(
            {
                "Node": node.name,
                "Role": node.role.value,
                "State": node.state.value,
                "Active": node.is_active
            }
        )

    st.dataframe(node_rows, use_container_width=True)

    st.divider()

    #---------------------------------------------------
    # topology
    #---------------------------------------------------
    
    # st.divider()
    # st.subheader("Cluster Topology")

    # # Build node → service group mapping
    # node_sg_map = {}

    # for node in cluster.nodes:
    #     node_sg_map[node.name] = []

    # for sg in cluster.service_groups:
    #     for node, state in sg.node_states.items():
    #         if state.value == "ONLINE":
    #             node_sg_map.setdefault(node, []).append(sg.name)

    # # Display topology
    # for node in cluster.nodes:

    #     running_sgs = node_sg_map.get(node.name, [])

    #     status_icon = "🟢 ACTIVE" if node.is_active else "🟡 STANDBY"

    #     st.markdown(f"### {node.name} ({status_icon})")

    #     if running_sgs:
    #         for sg in running_sgs:
    #             st.markdown(f"• {sg}")
    #     else:
    #         st.markdown("_No service groups running_")

    # --------------------------------------------------
    # Disk Groups
    # --------------------------------------------------

    st.subheader("Disk Groups")

    dg_rows = []

    for dg in cluster.diskgroups:

        dg_rows.append(
            {
                "Disk Group": dg.name,
                "State": dg.state.value,
                "Node": dg.node,
                #"Volumes": dg.volume_count,
                #"Total Size (GB)": dg.total_size_gb
            }
        )

    st.dataframe(dg_rows, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # Volumes
    # --------------------------------------------------

    st.subheader("Volumes")

    vol_rows = []

    for vol in cluster.volumes:

        vol_rows.append(
        {
            "Volume": vol.name,
            "Disk Group": vol.diskgroup,
            "Size (GB)": vol.size_gb,
            "Layout": vol.layout.value,
            "Mounted": vol.mounted,
            "Mount Point": vol.mount_point,
            "Node": vol.node
        }
        )

    st.dataframe(vol_rows, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # Service Groups
    # --------------------------------------------------

    st.subheader("Service Groups")

    sg_rows = []

    for sg in cluster.service_groups:

        row = {
            "Service Group": sg.name
        }

        active_node = None

        for node, state in sg.node_states.items():

            row[node] = state.value

            if state.value == "ONLINE":
                active_node = node

        row["Active Node"] = active_node

        sg_rows.append(row)

    st.dataframe(sg_rows, width="stretch")

    # --------------------------------------------------
    # Filesystems
    # --------------------------------------------------

    st.subheader("Filesystems")

    fs_rows = []

    for fs in cluster.filesystems:

        fs_rows.append(
            {
                "Mount": fs.mount_point,
                "Used %": fs.percent_used,
                "Size (GB)": fs.size_gb,
                "Used (GB)": fs.used_gb,
                "Available (GB)": fs.available_gb
            }
        )

    st.dataframe(fs_rows, use_container_width=True)
