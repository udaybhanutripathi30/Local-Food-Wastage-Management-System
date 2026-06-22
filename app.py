import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
conn = psycopg2.connect(
    host="ep-calm-silence-adx8ea9v-pooler.c-2.us-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_TNYJF7lG0okE",
    port="5432",
    sslmode="require"
)
st.markdown("""
<style>

/* REMOVE RADIO BUTTON (red/blue circle) */
section[data-testid="stSidebar"] div[role="radiogroup"] input {
    display: none !important;
}

/* REMOVE DEFAULT SELECTOR ICON SPACE */
section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
    display: none !important;
}

/* NORMAL ITEM */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 10px 14px;
    margin: 5px 10px;
    border-radius: 10px;
    color: #374151 !important;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* HOVER */
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: #eff6ff !important;
    color: #2563eb !important;
    cursor: pointer;
}

/* ACTIVE SELECTED PAGE */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background-color: #dbeafe !important;
    color: #2563eb !important;
    font-weight: 600;
    border-left: 4px solid #2563eb;
}

/* FORCE ACTIVE TEXT BLUE */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {
    color: #2563eb !important;
}

</style>
""", unsafe_allow_html=True)
# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Food Waste Management",
    page_icon="🍽️",
    layout="wide"
)
# SIDEBAR
st.sidebar.title("🍽️ Food Waste")

page = st.sidebar.radio(
    "",
    [
        "Overview",
        "Food Listings & Availability",
        "Claims & Distribution",
        "Analysis & Insights"
    ]
)
cities = pd.read_sql(
    "SELECT DISTINCT city FROM providers_data",
    conn
)
providers = pd.read_sql(
    "SELECT DISTINCT name  FROM providers_data",
    conn
)

receivers = pd.read_sql(
    "SELECT DISTINCT name FROM receivers_data",
    conn
)

food_types = pd.read_sql(
    "SELECT DISTINCT food_type FROM food_listings_data",
    conn
)

meal_types = pd.read_sql(
    "SELECT DISTINCT meal_type FROM food_listings_data",
    conn
)

city_filter = st.sidebar.selectbox(
    "Select City",
    ["All"] + cities["city"].tolist()
)
provider_filter = st.sidebar.selectbox(
    "Select Provider",
    ["All"] + providers["name"].tolist()
)

receiver_filter = st.sidebar.selectbox(
    "Select Receiver",
    ["All"] + receivers["name"].tolist()
)

food_filter = st.sidebar.selectbox(
    "Select Food Type",
    ["All"] + food_types["food_type"].tolist()
)

meal_filter = st.sidebar.selectbox(
    "Select Meal Type",
    ["All"] + meal_types["meal_type"].tolist()
)
# Filter SQL 
filter_sql = ""

if city_filter != "All":
    filter_sql += f"""
    AND provider_id IN (
        SELECT provider_id
        FROM providers_data
        WHERE city = '{city_filter}'
    )
    """

if food_filter != "All":
    filter_sql += f" AND food_type = '{food_filter}'"

if meal_filter != "All":
    filter_sql += f" AND meal_type = '{meal_filter}'"

if provider_filter != "All":
    filter_sql += f"""
    AND provider_id IN (
        SELECT provider_id
        FROM providers_data
        WHERE name = '{provider_filter}'
    )
    """

if receiver_filter != "All":
    filter_sql += f"""
    AND receiver_id IN (
        SELECT receiver_id
        FROM receivers_data
        WHERE name = '{receiver_filter}'
    )
    """
food_filter_sql= ""
if food_filter != "All":
    filter_sql += f" AND food_type = '{food_filter}'"

if meal_filter != "All":
    filter_sql += f" AND meal_type = '{meal_filter}'"

provider_filter_sql = ""

if city_filter != "All":
    provider_filter_sql += f" AND city = '{city_filter}'"

if provider_filter != "All":
    provider_filter_sql += f" AND name = '{provider_filter}'"

receiver_filter_sql = ""
if city_filter != "All":
    provider_filter_sql += f" AND city = '{city_filter}'"
if receiver_filter != "All":
    receiver_filter_sql += f" AND name = '{receiver_filter}'"

# OVERVIEW PAGE
if page == "Overview":

    st.title("🏠 Food Waste Management Dashboard")
    st.divider()
    st.header("Quick Overview")
    # KPIs
    
    providers = pd.read_sql(
        f"""SELECT distinct COUNT(*) AS total FROM providers_data
        WHERE 1=1
        {provider_filter_sql}""",
        conn
    )

    receivers = pd.read_sql(
        "SELECT distinct COUNT(*) AS total FROM receivers_data",
        conn
    )

    claims = pd.read_sql(
        "SELECT COUNT(*) AS total FROM claims_data",
        conn
    )

    completion_rate = pd.read_sql(
        """
        SELECT ROUND(
            COUNT(CASE WHEN status='Completed' THEN 1 END) * 100.0
            / COUNT(*),
            2
        ) AS completion_rate
        FROM claims_data
        """,
        conn
    )

    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Total Providers", providers["total"][0])
    with k2:
        st.metric("Total Receivers", receivers["total"][0])
    with k3:
        st.metric("Total Claims", claims["total"][0])
    with k4:
        st.metric(
            "Completion Rate",
            f"{completion_rate['completion_rate'][0]}%"
        )

    # TOP ROW
    col1, col2 = st.columns([1,1])

    with col1:

        city_provider = pd.read_sql(f"""
            SELECT city,
                   COUNT(*) AS total
            FROM providers_data
            GROUP BY city
            ORDER BY total DESC
            LIMIT 10
        """, conn)

        st.subheader("Top 10 Provider Cities")

        fig = px.scatter(
            city_provider,
            x="total",
            y="city",
            size="total",
            color="total",
            color_continuous_scale=[
                "#42a5f5",
                "#1e88e5",
                "#1565c0",
                "#0d47a1"
            ]
        )

        fig.update_layout(
            width=600,
            height=400,
            coloraxis_showscale=False,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=False)

    with col2:

        receiver_qty = pd.read_sql(f"""
            SELECT r.name,
                SUM(f.quantity) AS total_claimed
            FROM receivers_data r
            JOIN claims_data c
            ON r.receiver_id = c.receiver_id
            JOIN food_listings_data f
            ON c.food_id = f.food_id
            GROUP BY r.receiver_id, r.name
            ORDER BY total_claimed DESC
            LIMIT 10
        """, conn)

        st.subheader("Top 10 Receivers by Quantity Claimed")

        fig_receiver = px.bar(
            receiver_qty,
            x="total_claimed",
            y="name",
            orientation="h",
            color="total_claimed",
            color_continuous_scale=[
                "#64b5f6",
                "#42a5f5",
                "#1e88e5",
                "#1565c0",
                "#0d47a1"
            ]
        )

        fig_receiver.update_layout(
            coloraxis_showscale=False,
            template="plotly_white"
        )

        st.plotly_chart(
            fig_receiver,
            use_container_width=False,
            key="receiver_chart"
        )
        fig.update_layout(
            width=600,
            height=400,
            coloraxis_showscale=False,
            template="plotly_white"
        )
    # BOTTOM ROW
    col3, col4 = st.columns(2)

    with col3:

        sankey_df = pd.read_sql(f"""
            SELECT
                p.type as provider_type,
                r.type as receiver_type,
                COUNT(c.claim_id) AS total_claims
            FROM claims_data c
            JOIN food_listings_data f
                ON c.food_id = f.food_id
            JOIN providers_data p
                ON f.provider_id = p.provider_id
            JOIN receivers_data r
                ON c.receiver_id = r.receiver_id
            GROUP BY p.type, r.type
        """, conn)

        st.subheader("Provider Type → Receiver Type Flow (Claims)")

        source_labels = sankey_df["provider_type"].unique().tolist()
        target_labels = sankey_df["receiver_type"].unique().tolist()

        labels = source_labels + target_labels

        source = [
            labels.index(x)
            for x in sankey_df["provider_type"]
        ]

        target = [
            labels.index(x)
            for x in sankey_df["receiver_type"]
        ]

        value = sankey_df["total_claims"]

        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        label=labels,
                        pad=15,
                        thickness=20,
                        color=[
                            "#0d47a1",
                            "#1565c0",
                            "#1e88e5",
                            "#42a5f5",
                            "#64b5f6",
                            "#90caf9",
                            "#bbdefb",
                            "#1976d2"
                        ]
                    ),
                    link=dict(
                        source=source,
                        target=target,
                        value=value
                    )
                )
            ]
        )

        fig.update_layout(
            height=400,
            template="plotly_white"
        )
        fig.update_layout(
        font=dict(color="black", size=12)
        )
        fig.update_traces(
        textfont=dict(color="black")
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="provider_receiver_sankey"
        )
    with col4:

        if city_filter == "All":

            quantity = pd.read_sql("""
                SELECT location,
                       SUM(quantity) AS total_quantity
                FROM food_listings_data
                GROUP BY location
                ORDER BY total_quantity DESC
                LIMIT 10
            """, conn)

        else:

            quantity = pd.read_sql(f"""
                SELECT f.location,
                       SUM(f.quantity) AS total_quantity
                FROM food_listings_data f
                JOIN providers_data p
                ON f.provider_id = p.provider_id
                WHERE p.city = '{city_filter}'
                GROUP BY f.location
                ORDER BY total_quantity DESC
                LIMIT 10
            """, conn)

        st.subheader("Top 10 Locations by Quantity")

        fig = px.bar(
            quantity,
            x="location",
            y="total_quantity",
            color="total_quantity",
            color_continuous_scale=[
                "#64b5f6",
                "#42a5f5",
                "#1e88e5",
                "#1565c0",
                "#0d47a1"
            ]
        )

        fig.update_layout(
            width=600,
            height=400,
            coloraxis_showscale=False,
            template="plotly_white",
            margin=dict(l=30, r=30, t=60, b=30)
        )

        st.plotly_chart(fig, use_container_width=False)

    st.divider()

#Food listing and availability -- Page 2
if page == "Food Listings & Availability":

    st.header("🥗 Food Listings & Availability")

    # ===================== KPIs =====================

    total_qty = pd.read_sql(f"""
        SELECT SUM(quantity) AS total_quantity
        FROM food_listings_data
        where 1=1
        {food_filter_sql}
    """, conn)

    top_city = pd.read_sql(f"""
        SELECT p.city,
               COUNT(*) AS total_food_listing
        FROM food_listings_data f
        JOIN providers_data p
        ON f.provider_id = p.provider_id
        GROUP BY p.city
        ORDER BY total_food_listing DESC
        LIMIT 1
    """, conn)

    top_food = pd.read_sql(f"""
        SELECT food_type,
               COUNT(*) AS total_listing
        FROM food_listings_data

        GROUP BY food_type
        ORDER BY total_listing DESC
        LIMIT 1
    """, conn)

    total_listings = pd.read_sql("""
        SELECT COUNT(*) AS total
        FROM food_listings_data
    """, conn)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Total Listings", int(total_listings["total"][0]))

    with k2:
        st.metric("Total Quantity", int(total_qty["total_quantity"][0]))

    with k3:
        st.metric("Top City", top_city["city"][0])

    with k4:
        st.metric("Top Food Type", top_food["food_type"][0])

    st.divider()

    # ===================== CHARTS =====================

    c1, c2 = st.columns(2)

# ===================== CHARTS =====================

    c1, c2 = st.columns(2)

    with c1:

        provider_qty = pd.read_sql(f"""
            SELECT p.name,
                SUM(f.quantity) AS total_available_food
            FROM providers_data p
            JOIN food_listings_data f
            ON p.provider_id = f.provider_id
            GROUP BY p.provider_id, p.name
            ORDER BY total_available_food DESC
            LIMIT 10
        """, conn)

        st.subheader("Top 10 Provider vs Available Quantity")

        fig_provider = px.bar(
            provider_qty,
            x="total_available_food",
            y="name",
            orientation="h",
            color="total_available_food",
            color_continuous_scale=[
                "#64b5f6",
                "#42a5f5",
                "#1e88e5",
                "#1565c0",
                "#0d47a1"
            ]
        )

        fig_provider.update_layout(
            width=500,
            height=400,
            coloraxis_showscale=False,
            template="plotly_white"
        )

        st.plotly_chart(
            fig_provider,
            use_container_width=False,
            key="provider_quantity_chart"
        )

    with c2:

        city_listing = pd.read_sql(f"""
            SELECT p.city,
                COUNT(*) AS total_food_listing
            FROM food_listings_data f
            JOIN providers_data p
            ON f.provider_id = p.provider_id
            WHERE 1=1
            {food_filter_sql}
            GROUP BY p.city
            ORDER BY total_food_listing DESC
            LIMIT 10
        """, conn)

        st.subheader("Top 10 City vs Food Listings")

        fig_city = px.bar(
            city_listing,
            x="city",
            y="total_food_listing",
            color="total_food_listing",
            color_continuous_scale=[
                "#64b5f6",
                "#42a5f5",
                "#1e88e5",
                "#1565c0",
                "#0d47a1"
            ]
        )

        fig_city.update_layout(
            width=500,
            height=400,
            coloraxis_showscale=False,
            template="plotly_white"
        )

        st.plotly_chart(
            fig_city,
            use_container_width=False,
            key="city_listing_chart"
        )
    
    c3, c4 = st.columns(2)

    with c3:

     food_type_dist = pd.read_sql("""
        SELECT food_type,
               COUNT(*) AS total_listing
        FROM food_listings_data
        GROUP BY food_type
        ORDER BY total_listing DESC
    """, conn)
     st.subheader("Food Type Distribution")

     fig1 = px.pie(
        food_type_dist,
        names="food_type",
        color_discrete_sequence=px.colors.sequential.Blues_r,
     )
     fig1.update_layout(
     height=300,
     margin=dict(l=0, r=0, t=30, b=0),
     showlegend=False
     )
     fig1.update_traces(
     textposition="inside",
     textinfo="percent+label"
     )
     st.plotly_chart(fig1, use_container_width=True)

    with c4:

     meal_type_dist = pd.read_sql(f"""
        SELECT meal_type,
               COUNT(*) AS total_listing
        FROM food_listings_data
        WHERE 1=1
        {food_filter_sql}
        GROUP BY meal_type
    """, conn)

     st.subheader("Meal Type Distribution")
     fig2 = px.pie(
        meal_type_dist,
        names="meal_type",
        values="total_listing",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
     fig2.update_layout(
     height=300,
     margin=dict(l=0, r=0, t=30, b=0),
     showlegend=False
     )
     fig2.update_traces(
     textposition="inside",
     textinfo="percent+label"
     )
     st.plotly_chart(fig2, use_container_width=True)
     st.divider()

    # ===================== FILTERS =====================

    st.subheader("Filter Food Listings")

    col1, col2 = st.columns(2)

    food_types = pd.read_sql(
        "SELECT DISTINCT food_type FROM food_listings_data",
        conn
    )

    meal_types = pd.read_sql(
        "SELECT DISTINCT meal_type FROM food_listings_data",
        conn
    )

    with col1:
        food_filter = st.selectbox(
            "Food Type",
            ["All"] + food_types["food_type"].tolist()
        )

    with col2:
        meal_filter = st.selectbox(
            "Meal Type",
            ["All"] + meal_types["meal_type"].tolist()
        )

    query = """
    SELECT *
    FROM food_listings_data
    WHERE 1=1
    """

    if food_filter != "All":
        query += f" AND food_type = '{food_filter}'"

    if meal_filter != "All":
        query += f" AND meal_type = '{meal_filter}'"

    if city_filter != "All":
        query += f"""
        AND f.provider_id IN (
            SELECT provider_id
            FROM providers_data
            WHERE city = '{city_filter}'
        )
        """

    filtered_df = pd.read_sql(query, conn)

    st.subheader("Food Listings Table")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
# Claims & distribution Page--3
if page == "Claims & Distribution":

    st.header("🚚 Claims & Distribution")

    # ===================== KPIs =====================

    total_claims = pd.read_sql("""
        SELECT COUNT(*) AS total
        FROM claims_data
    """, conn)

    completed_claims = pd.read_sql("""
        SELECT COUNT(*) AS total
        FROM claims_data
        WHERE status = 'Completed'
    """, conn)

    pending_claims = pd.read_sql("""
        SELECT COUNT(*) AS total
        FROM claims_data
        WHERE status = 'Pending'
    """, conn)

    cancelled_claims = pd.read_sql("""
        SELECT COUNT(*) AS total
        FROM claims_data
        WHERE status = 'Cancelled'
    """, conn)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Total Claims", int(total_claims["total"][0]))

    with k2:
        st.metric("Completed", int(completed_claims["total"][0]))

    with k3:
        st.metric("Pending", int(pending_claims["total"][0]))

    with k4:
        st.metric("Cancelled", int(cancelled_claims["total"][0]))

    st.divider()

    # ===================== CHARTS =====================

    c1, c2 = st.columns(2)

    with c1:

        claim_status = pd.read_sql("""
            SELECT status,
                   COUNT(*) AS total
            FROM claims_data
            GROUP BY status
        """, conn)
        st.subheader("Claim Status DIstribution")
        fig1 = px.pie(
            claim_status,
            names="status",
            values="total",
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )

        fig1.update_layout(
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig1, use_container_width=True)

    with c2:

        food_claims = pd.read_sql("""
            SELECT f.food_name,
                   COUNT(c.claim_id) AS total_claims
            FROM claims_data c
            JOIN food_listings_data f
            ON c.food_id = f.food_id
            GROUP BY f.food_name
            ORDER BY total_claims
            LIMIT 10
        """, conn)
        st.subheader("Top 10 Most Claimed Food Items")
        fig2 = px.bar(
            food_claims,
            x="total_claims",
            y="food_name",
            orientation="h",
            color="total_claims",
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:

        provider_claims = pd.read_sql("""
            SELECT p.name,
                   COUNT(c.claim_id) AS total_food_claims
            FROM providers_data p
            JOIN food_listings_data f
            ON p.provider_id = f.provider_id
            JOIN claims_data c
            ON c.food_id = f.food_id
            WHERE c.status = 'Completed'
            GROUP BY p.provider_id,p.name
            ORDER BY total_food_claims DESC
            LIMIT 10
        """, conn)
        st.subheader("Top Providers by Successful Claims")
        fig3 = px.bar(
            provider_claims,
            x="name",
            y="total_food_claims",
            color="total_food_claims",
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        claim_percentage = pd.read_sql("""
            SELECT status,
                   ROUND(
                       COUNT(*) * 100.0 /
                       (SELECT COUNT(*) FROM claims_data),
                       2
                   ) AS percentage
            FROM claims_data
            GROUP BY status
        """, conn)
        st.subheader("Claim Status Percentage")
        fig4 = px.treemap(
            claim_percentage,
            path=["status"],
            values="percentage",
            color="percentage",
            color_continuous_scale="Blues",
        )
        fig4.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white"
        )
        fig4.update_layout(
        height=400,
        width=500,
        showlegend=True
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # ===================== CLAIMS TABLE =====================

    st.subheader("Claims Details")

    claims_table = pd.read_sql("""
        SELECT *
        FROM claims_data
    """, conn)

    st.dataframe(
        claims_table,
        use_container_width=True
    )
#Analysis & Insight -- Page 4
if page == "Analysis & Insights":

    st.header("📊 Analysis & Insights")

    # ================= KPIs =================

    avg_receiver = pd.read_sql("""
        SELECT AVG(total_claimed) AS avg_quantity_per_receiver
        FROM (
            SELECT c.receiver_id,
                   SUM(f.quantity) AS total_claimed
            FROM claims_data c
            JOIN food_listings_data f
            ON c.food_id = f.food_id
            GROUP BY c.receiver_id
        ) t
    """, conn)

    meal_type = pd.read_sql("""
        SELECT meal_type,
               SUM(quantity) AS total_food_claimed
        FROM food_listings_data
        GROUP BY meal_type
        ORDER BY total_food_claimed DESC
        LIMIT 1
    """, conn)

    top_provider = pd.read_sql("""
        SELECT p.name,
               SUM(f.quantity) AS total_food_donated
        FROM providers_data p
        JOIN food_listings_data f
        ON p.provider_id = f.provider_id
        GROUP BY p.provider_id,p.name
        ORDER BY total_food_donated DESC
        LIMIT 1
    """, conn)

    top_receiver = pd.read_sql("""
            SELECT
            r.name AS receiver_name,
            SUM(f.quantity) AS total_quantity_received
        FROM receivers_data r
        JOIN claims_data c
            ON r.receiver_id = c.receiver_id
        JOIN food_listings_data f
            ON c.food_id = f.food_id
        GROUP BY r.receiver_id, r.name
        ORDER BY total_quantity_received DESC
        LIMIT 1;
    """, conn)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "Avg Qty per Receiver",
            round(avg_receiver["avg_quantity_per_receiver"][0],2)
        )

    with k2:
        st.metric(
            "Most Claimed Meal",
            meal_type["meal_type"][0]
        )

    with k3:
        st.metric(
            "Top Donor",
            top_provider["name"][0]
        )

    with k4:
        st.metric(
            "Top Receiver",
            top_receiver["receiver_name"][0])

    st.divider()

    # ================= CHARTS =================

    c1, c2 = st.columns(2)

    with c1:

        provider_donation = pd.read_sql("""
            SELECT p.name,
                SUM(f.quantity) AS total_food_donated
            FROM providers_data p
            JOIN food_listings_data f
            ON p.provider_id = f.provider_id
            GROUP BY p.provider_id,p.name
            ORDER BY total_food_donated DESC
            LIMIT 10
        """, conn)

        fig1 = px.scatter(
            provider_donation,
            x="total_food_donated",
            y="name",
            size="total_food_donated",
            color="total_food_donated",
            color_continuous_scale="Blues"
        )

        for i, row in provider_donation.iterrows():
            fig1.add_shape(
                type="line",
                x0=0,
                y0=i,
                x1=row["total_food_donated"],
                y1=i,
                line=dict(color="lightblue", width=2)
            )

        fig1.update_layout(
            title="Top 10 Providers by Food Donation",
            coloraxis_showscale=False,
            template="plotly_white"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with c2:

        meal_claim = pd.read_sql("""
            SELECT meal_type,
                SUM(quantity) AS total_food_claimed
            FROM food_listings_data
            GROUP BY meal_type
        """, conn)

        fig2 = px.sunburst(
            meal_claim,
            path=["meal_type"],
            values="total_food_claimed",
            color="total_food_claimed",
            color_continuous_scale="Blues"
        )

        fig2.update_layout(
            title="Meal Type Distribution",
            template="plotly_white"
        )

        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:

        receiver_claim = pd.read_sql("""
            SELECT c.receiver_id,
                SUM(f.quantity) AS total_claimed
            FROM claims_data c
            JOIN food_listings_data f
            ON c.food_id = f.food_id
            GROUP BY c.receiver_id
            ORDER BY total_claimed DESC
            LIMIT 10
        """, conn)

        fig3 = px.scatter(
            receiver_claim,
            x="receiver_id",
            y="total_claimed",
            size="total_claimed",
            color="total_claimed",
            color_continuous_scale="Blues",
            size_max=50
        )

        fig3.update_layout(
            title="Top Receivers by Quantity Claimed",
            coloraxis_showscale=False,
            template="plotly_white"
        )

        st.plotly_chart(fig3, use_container_width=True)

    with c4:

        fig4 = px.icicle(
            provider_donation,
            path=["name"],
            values="total_food_donated",
            color="total_food_donated",
            color_continuous_scale="Blues"
        )

        fig4.update_layout(
            title="Provider Contribution Hierarchy",
            template="plotly_white"
        )

        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    st.subheader("Conclusion")
    
    st.info("""
The platform has successfully redistributed 25,974 food units, with Barry Group emerging as the top provider and Matthew Hub as the top receiver. 
New Carol leads all cities in total food distribution, while Vegetarian is the most donated food type and Snacks is the most shared meal category. 
On the lower end, Reyes and Son recorded the lowest quantity donated, while Joshua Hooper claimed the lowest quantity. Overall, the data highlights strong community participation and the platform's effectiveness in reducing food waste and improving food accessibility.
""")