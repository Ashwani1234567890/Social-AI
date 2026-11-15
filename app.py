import streamlit as st
from agents import run_social_media_agents

st.set_page_config(
    page_title="SocialAI",
    page_icon="🤖",
    layout="wide"
)


if "posts" not in st.session_state:
    st.session_state.posts=[]

if "quality_report" not in st.session_state:
    st.session_state.quality_report=""

if "research" not in st.session_state:
    st.session_state.research=""

st.title("SocialAI")
st.caption("Your AI-powered social media manager")

st.divider()

st.subheader("Create campaign")

with st.form("campaign_form"):

    business=st.text_input(
        "Business name",
        placeholder="Fitlife"
    )
    industry=st.text_input(
        'Industry',
        placeholder="Fitness and Lifestyle"
    )
    topic=st.text_input(
        "Campaign topic",
        placeholder="Importance of regular exercise"
    )

    col1,col2=st.columns(2)

    with col1:
        platform=st.selectbox(
            "Platform",
            ["Instagram","Linkedin","X"]
        )

    with col2:
        number_of_posts=st.selectbox(
            "Number of posts",
            [1,5,3]
        )

    generate=st.form_submit_button(
        "Generate content",
        type="primary",
        use_container_width=True
    )

    if generate:
        if not business or not industry or not topic:
            st.error("Please fill all the business activites")

        else:

            try:
                with st.spinner(
                    "Research Agent->Content Agent->Quality Assurance"
                ):
                    result=run_social_media_agents(
                        business=business,
                        industry=industry,
                        platform=platform,
                        topic=topic,
                        number_of_posts=number_of_posts
                    )
                st.session_state["posts"]=[
                    {**post,"status":"Pending"}
                    for post in result['posts']
                ]

                st.session_state.quality_report=result["quality_report"]
                st.session_state.research=result['research']

                st.success("AI workflow complete")

            except Exception as e:
                st.error(f"Agent execution error:{e}")


if st.session_state.research:
    st.divider()
    st.subheader("Research Agent Report")

    with st.expander("View research"):
        st.write(st.session_state.research)


if st.session_state.quality_report:
    st.subheader("Quality Control Report")
    st.markdown(st.session_state.quality_report)

if st.session_state.posts:

    st.divider()
    st.header("📝 Generated Posts")

    for i, post in enumerate(st.session_state.posts):

        with st.container(border=True):

            st.subheader(f"Post {i + 1}: {post['title']}")

            st.caption(
                f"Platform: {post['platform']} | "
                f"Status: {post['status']}"
            )

            st.markdown(f"**Hook:** {post['hook']}")

            st.write(post["caption"])

            st.write(
                "**Hashtags:**",
                " ".join(post["hashtags"])
            )

            st.write(f"**CTA:** {post['cta']}")

            col1, col2 = st.columns(2)

            if post["status"] == "Pending":

                with col1:
                    if st.button(
                        "✅ Approve",
                        key=f"approve_{i}",
                        use_container_width=True
                    ):
                        st.session_state.posts[i]["status"] = "Approved"
                        st.rerun()

                with col2:
                    if st.button(
                        "❌ Reject",
                        key=f"reject_{i}",
                        use_container_width=True
                    ):
                        st.session_state.posts[i]["status"] = "Rejected"
                        st.rerun()

            elif post["status"] == "Approved":

                with col1:
                    if st.button(
                        "📤 Simulate Publishing",
                        key=f"publish_{i}",
                        use_container_width=True
                    ):
                        st.session_state.posts[i]["status"] = "Published"
                        st.rerun()

            elif post["status"] == "Published":

                st.success("Successfully simulated publication!")

            else:

                st.warning("Post rejected.")

st.divider()

st.subheader("📊 Campaign Dashboard")

posts = st.session_state.posts

total = len(posts)
approved = sum(p["status"] == "Approved" for p in posts)
published = sum(p["status"] == "Published" for p in posts)
rejected = sum(p["status"] == "Rejected" for p in posts)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Generated", total)
c2.metric("Approved", approved)
c3.metric("Published", published)
c4.metric("Rejected", rejected)



