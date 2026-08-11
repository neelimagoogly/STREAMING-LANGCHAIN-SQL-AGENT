# import random

# import streamlit as st
# from dotenv import load_dotenv
# from langchain_core.language_models.chat_models import BaseChatModel
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# from querymancer.agent import (
#     ask,
#     ask_stream,
#     create_history,
# )
# from querymancer.config import Config
# from querymancer.models import create_llm
# from querymancer.optimizations import DynamicComplexityRouter, optimize_query_execution
# from querymancer.tools import with_sql_cursor




# load_dotenv()

# LOADING_MESSAGES = [
#     "Consulting the ancient tomes of SQL wisdom...",
#     "Casting query spells on your database...",
#     "Summoning data from the digital realms...",
#     "Deciphering your request into database runes...",
#     "Brewing a potion of perfect query syntax...",
#     "Channeling the power of database magic...",
#     "Translating your words into the language of tables...",
#     "Waving my SQL wand to fetch your results...",
#     "Performing database divination...",
#     "Aligning the database stars for optimal results...",
#     "Consulting with the database spirits...",
#     "Transforming natural language into database incantations...",
#     "Peering into the crystal ball of your database...",
#     "Opening a portal to your data dimension...",
#     "Enchanting your request with SQL magic...",
#     "Invoking the ancient art of query optimization...",
#     "Reading between the tables to find your answer...",
#     "Conjuring insights from your database depths...",
#     "Weaving a tapestry of joins and filters...",
#     "Preparing a feast of data for your consideration...",
# ]


# def get_model(query: str = None) -> BaseChatModel:
#     """Get appropriate LLM based on query complexity.

#     Args:
#         query: The user's natural language query (if provided)

#     Returns:
#         BaseChatModel: Configured language model for the query
#     """
#     if not query:
#         # Default model if no query provided
#         return create_llm(Config.MODEL)

#     # Initialize the complexity router
#     complexity_router = DynamicComplexityRouter()

#     # Determine the appropriate model based on query complexity
#     return complexity_router.get_appropriate_model(query)


# def load_css(css_file):
#     with open(css_file, "r") as f:
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# st.set_page_config(
#     page_title="Querymancer",
#     page_icon="🧙‍♂️",
# )

# # Apply CSS styling
# try:
#     load_css("assets/style.css")
# except FileNotFoundError:
#     st.write("CSS file not found, using default styling")

# # Initialize session state for chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = create_history()

# # Header and description
# st.header("Querymancer")
# st.subheader("Talk to your database using natural language")

# # Display DB tables
# with st.expander("Database Tables"):
#     with with_sql_cursor() as cursor:
#         # Get list of tables
#         cursor.execute(
#             "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
#         )
#         tables = [row[0] for row in cursor.fetchall()]

#         st.write("### Available Tables")
#         for table in tables:
#             cursor.execute(f"SELECT COUNT(*) FROM {table}")
#             count = cursor.fetchone()[0]
#             st.write(f"- {table} ({count} rows)")

# # Chat interface
# for message in st.session_state.messages:
#     if type(message) is SystemMessage:
#         continue
#     is_user = type(message) is HumanMessage
#     avatar = "🐧" if is_user else "🧙‍♂️"
#     with st.chat_message("user" if is_user else "ai", avatar=avatar):
#         st.markdown(message.content)

# # Get user input
# if prompt := st.chat_input("Type your message..."):
#     with st.chat_message("user", avatar="🐧"):
#         st.session_state.messages.append(HumanMessage(prompt))
#         st.markdown(prompt)
#     with st.chat_message("ai", avatar="🧙‍♂️"):
#         message_placeholder = st.empty()
#         message_placeholder.status(random.choice(LOADING_MESSAGES), state="running")

#         # Optimize query execution using our pipeline
#         optimized_query, model, optimized_history, model_params = optimize_query_execution(
#             prompt, st.session_state.messages
#         )

#         # Generate response using the agent
#         response = ask(optimized_query, optimized_history, model, max_iterations=10)

#         # Update message placeholder with response
#         message_placeholder.markdown(response)

#     # Add response to chat history
#     st.session_state.messages.append(AIMessage(response))


import random

import streamlit as st
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from querymancer.agent import ask_stream, create_history
from querymancer.config import Config
from querymancer.models import create_llm
from querymancer.optimizations import (
    DynamicComplexityRouter,
    optimize_query_execution,
)
from querymancer.tools import with_sql_cursor


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Loading messages
# ---------------------------------------------------------

LOADING_MESSAGES = [
    "Consulting the ancient tomes of SQL wisdom...",
    "Casting query spells on your database...",
    "Summoning data from the digital realms...",
    "Deciphering your request into database runes...",
    "Brewing a potion of perfect query syntax...",
    "Channeling the power of database magic...",
    "Translating your words into the language of tables...",
    "Waving my SQL wand to fetch your results...",
    "Performing database divination...",
    "Aligning the database stars for optimal results...",
    "Consulting with the database spirits...",
    "Transforming natural language into database incantations...",
    "Peering into the crystal ball of your database...",
    "Opening a portal to your data dimension...",
    "Enchanting your request with SQL magic...",
    "Invoking the ancient art of query optimization...",
    "Reading between the tables to find your answer...",
    "Conjuring insights from your database depths...",
    "Weaving a tapestry of joins and filters...",
    "Preparing a feast of data for your consideration...",
]


# ---------------------------------------------------------
# Model selection
# ---------------------------------------------------------

def get_model(query: str = None) -> BaseChatModel:
    """
    Get the appropriate LLM based on query complexity.

    Args:
        query: User's natural-language query.

    Returns:
        Configured BaseChatModel.
    """

    if not query:
        return create_llm(Config.MODEL)

    complexity_router = DynamicComplexityRouter()

    return complexity_router.get_appropriate_model(query)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

def load_css(css_file):
    """
    Load custom CSS if available.
    """

    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Querymancer",
    page_icon="🧙‍♂️",
    layout="wide",
)


# ---------------------------------------------------------
# Apply CSS
# ---------------------------------------------------------

try:
    load_css("assets/style.css")
except FileNotFoundError:
    pass


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = create_history()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.header("Querymancer")
st.subheader("Talk to your database using natural language")


# ---------------------------------------------------------
# Database tables
# ---------------------------------------------------------

with st.expander("🗄️ Database Tables"):

    try:

        with with_sql_cursor() as cursor:

            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name;
                """
            )

            tables = [
                row[0]
                for row in cursor.fetchall()
            ]

            if not tables:

                st.warning(
                    "No user-created tables were found "
                    "in the SQLite database."
                )

            else:

                st.write("### Available Tables")

                for table in tables:

                    try:

                        # Quote table name safely for SQLite.
                        safe_table = table.replace('"', '""')

                        cursor.execute(
                            f'SELECT COUNT(*) FROM "{safe_table}"'
                        )

                        count = cursor.fetchone()[0]

                        st.write(
                            f"- **{table}** — {count} rows"
                        )

                    except Exception as e:

                        st.write(
                            f"- **{table}** — "
                            f"Unable to determine row count: {e}"
                        )

    except Exception as e:

        st.error(
            f"Unable to inspect the database: {e}"
        )


# ---------------------------------------------------------
# Display existing chat history
# ---------------------------------------------------------

for message in st.session_state.messages:

    # Don't display the system prompt.
    if isinstance(message, SystemMessage):
        continue

    is_user = isinstance(message, HumanMessage)

    avatar = "🐧" if is_user else "🧙‍♂️"

    with st.chat_message(
        "user" if is_user else "ai",
        avatar=avatar,
    ):

        st.markdown(message.content)


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

if prompt := st.chat_input(
    "Ask something about your database..."
):

    # -----------------------------------------------------
    # Display user's message
    # -----------------------------------------------------

    with st.chat_message(
        "user",
        avatar="🐧",
    ):

        st.session_state.messages.append(
            HumanMessage(content=prompt)
        )

        st.markdown(prompt)


    # -----------------------------------------------------
    # AI response
    # -----------------------------------------------------

    with st.chat_message(
        "ai",
        avatar="🧙‍♂️",
    ):

        # -------------------------------------------------
        # Main response placeholder
        # -------------------------------------------------

        message_placeholder = st.empty()

        message_placeholder.info(
            random.choice(LOADING_MESSAGES)
        )


        # -------------------------------------------------
        # Agent Events
        # -------------------------------------------------

        with st.expander(
            "🔍 Agent Events",
            expanded=True,
        ):

            event_placeholder = st.empty()

            events = []

            def render_events():
                """
                Render the accumulated agent events.
                """

                if not events:

                    event_placeholder.info(
                        "Waiting for agent events..."
                    )

                    return

                event_placeholder.markdown(
                    "\n\n".join(
                        [
                            (
                                f"**{event['icon']} "
                                f"{event['title']}**  \n"
                                f"{event['message']}"
                            )
                            for event in events
                        ]
                    )
                )


            render_events()


        # -------------------------------------------------
        # Generated SQL
        # -------------------------------------------------

        with st.expander(
            "🧾 Generated SQL",
            expanded=True,
        ):

            sql_placeholder = st.empty()

            sql_placeholder.code(
                "-- Waiting for SQL generation...",
                language="sql",
            )


        # -------------------------------------------------
        # SQL Result
        # -------------------------------------------------

        with st.expander(
            "📊 SQL Result",
            expanded=False,
        ):

            result_placeholder = st.empty()

            result_placeholder.info(
                "Waiting for SQL execution..."
            )


        # -------------------------------------------------
        # Final Answer
        # -------------------------------------------------

        with st.expander(
            "💬 Final Answer",
            expanded=True,
        ):

            answer_placeholder = st.empty()

            answer_placeholder.info(
                "Waiting for final answer..."
            )


        # -------------------------------------------------
        # Run Querymancer
        # -------------------------------------------------

        response = ""

        try:

            # -------------------------------------------------
            # Query optimization and model selection
            # -------------------------------------------------

            (
                optimized_query,
                model,
                optimized_history,
                model_params,
            ) = optimize_query_execution(
                prompt,
                st.session_state.messages,
            )


            # -------------------------------------------------
            # Stream agent events
            # -------------------------------------------------

            for event in ask_stream(
                optimized_query,
                optimized_history,
                model,
                max_iterations=10,
            ):

                event_type = event.get("type")


                # =============================================
                # Agent started
                # =============================================

                if event_type == "agent_start":

                    events.append(
                        {
                            "icon": "🚀",
                            "title": "Agent Started",
                            "message": event.get(
                                "message",
                                "Querymancer started.",
                            ),
                        }
                    )

                    render_events()


                # =============================================
                # Agent thinking
                # =============================================

                elif event_type == "agent_thinking":

                    iteration = event.get(
                        "iteration",
                        "?",
                    )

                    events.append(
                        {
                            "icon": "🧠",
                            "title": (
                                f"Agent Analysis "
                                f"(Iteration {iteration})"
                            ),
                            "message": event.get(
                                "message",
                                "Analyzing request.",
                            ),
                        }
                    )

                    render_events()


                # =============================================
                # Tool started
                # =============================================

                elif event_type == "tool_start":

                    tool_name = event.get(
                        "tool",
                        "unknown",
                    )

                    tool_args = event.get(
                        "args",
                        {},
                    )

                    events.append(
                        {
                            "icon": "🔧",
                            "title": (
                                f"Tool: {tool_name}"
                            ),
                            "message": (
                                "Executing database "
                                "operation.\n\n"
                                f"Arguments:\n"
                                f"```json\n"
                                f"{tool_args}\n"
                                f"```"
                            ),
                        }
                    )

                    render_events()


                # =============================================
                # Generated SQL
                # =============================================

                elif event_type == "generated_sql":

                    sql = event.get(
                        "sql",
                        "",
                    )

                    sql_placeholder.code(
                        sql,
                        language="sql",
                    )

                    events.append(
                        {
                            "icon": "🧾",
                            "title": "SQL Generated",
                            "message": (
                                "The agent generated "
                                "the following SQL query."
                            ),
                        }
                    )

                    render_events()


                # =============================================
                # Tool result
                # =============================================

                elif event_type == "tool_result":

                    tool_name = event.get(
                        "tool",
                        "unknown",
                    )

                    result = event.get(
                        "result",
                        "",
                    )

                    # Show SQL execution results
                    # separately from other tool results.
                    if tool_name == "execute_sql":

                        result_placeholder.code(
                            str(result),
                            language="text",
                        )

                        events.append(
                            {
                                "icon": "✅",
                                "title": "SQL Executed",
                                "message": (
                                    "SQL executed successfully."
                                ),
                            }
                        )

                    else:

                        events.append(
                            {
                                "icon": "📋",
                                "title": (
                                    f"{tool_name} Result"
                                ),
                                "message": str(result),
                            }
                        )

                    render_events()


                # =============================================
                # Final answer
                # =============================================

                elif event_type == "final_answer":

                    response = event.get(
                        "content",
                        "",
                    )

                    # Remove loading message.
                    message_placeholder.empty()

                    # Display final answer.
                    answer_placeholder.markdown(
                        response
                    )


                # =============================================
                # Error
                # =============================================

                elif event_type == "error":

                    error_message = event.get(
                        "message",
                        "Unknown error.",
                    )

                    events.append(
                        {
                            "icon": "❌",
                            "title": "Agent Error",
                            "message": error_message,
                        }
                    )

                    render_events()

                    message_placeholder.empty()

                    answer_placeholder.error(
                        error_message
                    )

                    response = (
                        f"Query execution failed: "
                        f"{error_message}"
                    )


        except Exception as e:

            message_placeholder.empty()

            error_message = str(e)

            events.append(
                {
                    "icon": "❌",
                    "title": "Query Execution Error",
                    "message": error_message,
                }
            )

            render_events()

            answer_placeholder.error(
                error_message
            )

            response = (
                f"Unable to process the query: "
                f"{error_message}"
            )


        # -------------------------------------------------
        # Save final answer to chat history
        # -------------------------------------------------

        st.session_state.messages.append(
            AIMessage(content=response)
        )

