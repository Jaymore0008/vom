# vom/presentation/dashboard.py

import streamlit as st

from application.services.cluster_service import ClusterService
from application.services.host_service import HostService

st.set_page_config(
    page_title="Infrastructure Monitoring",
    layout="wide"
)

st.title("Infrastructure Monitoring Dashboard")


cluster_service = ClusterService()
host_service = HostService()


# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab1, tab2 = st.tabs(["VOM Cluster", "Linux Infrastructure"])


# ==================================================
# TAB 1 — VOM CLUSTER
# ==================================================

with tab1:

    st.header("Veritas Cluster Monitoring")

    cluster_sid = st.sidebar.selectbox("Cluster SID", cluster_service.config.get_all_sids())

if st.button("Refresh Cluster"):

    if not cluster_sid:
        st.warning("Please select a cluster")
        st.stop()

    with st.spinner("Collecting cluster data..."):

        cluster = cluster_service.collect_cluster(cluster_sid)

        if not cluster:
            st.error("Cluster collection failed")
            st.stop()

        summary = cluster.summary()

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Cluster", summary["sid"])
        col2.metric("Health", summary["health"])
        col3.metric("Nodes", summary["node_count"])
        col4.metric("Service Groups", summary["service_group_count"])

        st.divider()

        # Issues
        st.subheader("Cluster Issues")

        if not cluster.issues:
            st.success("No issues detected")

        else:

            for issue in cluster.issues:

                if issue.severity == "CRITICAL":
                    st.error(issue.message)

                else:
                    st.warning(issue.message)

        st.divider()

        # Service Groups table
        st.subheader("Service Groups")

        sg_rows = []

        for sg in cluster.service_groups:

            for node, state in sg.node_states.items():

                sg_rows.append(
                    {
                        "Service Group": sg.name,
                        "Node": node,
                        "State": state
                    }
                )

        st.dataframe(sg_rows, use_container_width=True)

        st.divider()

        # Filesystems
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


# ==================================================
# TAB 2 — LINUX INFRASTRUCTURE
# ==================================================

with tab2:

    st.header("Linux Infrastructure Monitoring")

    if st.button("Refresh Hosts"):

        with st.spinner("Collecting host metrics..."):

            hosts = host_service.collect_all()

        if not hosts:
            st.warning("No hosts returned")
            st.stop()

        # Summary metrics
        total_hosts = len(hosts)
        down_hosts = len(host_service.down_hosts(hosts))

        col1, col2 = st.columns(2)

        col1.metric("Total Hosts", total_hosts)
        col2.metric("Down Hosts", down_hosts)

        st.divider()

        # Host table
        st.subheader("Host Metrics")

        rows = []

        for host in hosts:

            rows.append(
                {
                    "Host": host.name,
                    "IP": host.ip,
                    "Status": host.status.value,
                    "CPU %": host.cpu_usage,
                    "Memory %": host.memory_usage,
                    "Health": host.overall_health().value
                }
            )

        st.dataframe(rows, use_container_width=True)

        st.divider()

        # Top CPU
        st.subheader("Top CPU Usage")

        top_cpu = host_service.top_cpu(hosts, 5)

        cpu_rows = []

        for host in top_cpu:

            cpu_rows.append(
                {
                    "Host": host.name,
                    "CPU %": host.cpu_usage
                }
            )

        st.dataframe(cpu_rows, use_container_width=True)

        st.divider()

        # Top Memory
        st.subheader("Top Memory Usage")

        top_mem = host_service.top_memory(hosts, 5)

        mem_rows = []

        for host in top_mem:

            mem_rows.append(
                {
                    "Host": host.name,
                    "Memory %": host.memory_usage
                }
            )

        st.dataframe(mem_rows, use_container_width=True)