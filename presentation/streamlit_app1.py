import streamlit as st
import pandas as pd

from shared.config_loader2 import ConfigLoader
from infrastructure.linux.linux_metrics_factory import create_linux_metrics_client
from application.host_service import HostService


# -----------------------------------
# Page Config
# -----------------------------------

st.set_page_config(
    page_title="Host Monitoring Dashboard",
    layout="wide"
)

st.title("🖥 Linux Host Monitoring Dashboard")


# -----------------------------------
# Initialize Services
# -----------------------------------

config = ConfigLoader()

host_service = HostService(
    config_loader=config,
    metrics_client_factory=create_linux_metrics_client,
    max_workers=config.get_max_workers()
)


# -----------------------------------
# Refresh Button
# -----------------------------------

if st.button("🔄 Refresh Metrics"):
    st.cache_data.clear()


# -----------------------------------
# Collect Data
# -----------------------------------

@st.cache_data(ttl=30)
def load_hosts():
    return host_service.collect_all()


hosts = load_hosts()


# -----------------------------------
# Convert to DataFrame
# -----------------------------------

data = []

for h in hosts:
    data.append({
        "Host": h.name,
        "IP": h.ip,
        "Status": h.status.value,
        "CPU %": h.cpu_usage,
        "Memory %": h.memory_usage,
        "Health": h.overall_health().value
    })

df = pd.DataFrame(data)


# -----------------------------------
# Summary Metrics
# -----------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Hosts", len(hosts))

with col2:
    st.metric(
        "Down Hosts",
        len(host_service.down_hosts(hosts))
    )

with col3:
    avg_cpu = round(df["CPU %"].mean(), 2)
    st.metric("Average CPU", f"{avg_cpu} %")


# -----------------------------------
# Host Table
# -----------------------------------

st.subheader("All Hosts")

st.dataframe(
    df,
    use_container_width=True
)


# -----------------------------------
# Top CPU Hosts
# -----------------------------------

st.subheader("🔥 Top CPU Hosts")

top_cpu = host_service.top_cpu(hosts)

cpu_data = [{
    "Host": h.name,
    "CPU %": h.cpu_usage
} for h in top_cpu]

st.table(cpu_data)


# -----------------------------------
# Top Memory Hosts
# -----------------------------------

st.subheader("🧠 Top Memory Hosts")

top_mem = host_service.top_memory(hosts)

mem_data = [{
    "Host": h.name,
    "Memory %": h.memory_usage
} for h in top_mem]

st.table(mem_data)


# -----------------------------------
# Down Hosts
# -----------------------------------

st.subheader("❌ Down Hosts")

down_hosts = host_service.down_hosts(hosts)

if down_hosts:
    st.table([{
        "Host": h.name,
        "IP": h.ip
    } for h in down_hosts])
else:
    st.success("All hosts are UP ✅")