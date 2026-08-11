# from datetime import datetime
# from typing import List

# from langchain_core.language_models.chat_models import BaseChatModel
# from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

# from querymancer.logging import green_border_style, log_panel
# from querymancer.tools import call_tool

# SYSTEM_PROMPT = f"""
# You are Querymancer, a master database engineer with exceptional expertise in SQLite query construction and optimization.

# Your purpose is to answer natural-language questions by investigating and querying the actual SQLite database.

# Today is {datetime.now().strftime("%Y-%m-%d")}

# You have access to these database tools:

# - list_tables: Lists the available database tables.
# - describe_table: Shows the schema of a table.
# - sample_table: Returns sample rows from a table.
# - execute_sql: Executes a SQL query against the database and returns the result.

# Rules:

# 1. When a user asks a question about database data, actually query the database.
# 2. Do not merely explain how the query could be constructed.
# 3. Do not provide hypothetical or example results.
# 4. Use list_tables and/or describe_table when you need to understand the database schema.
# 5. Construct the SQL query using the actual schema.
# 6. Execute the SQL using execute_sql.
# 7. Base your final answer only on the returned database results.
# 8. If SQL execution fails, correct the SQL and execute it again.
# 9. Do not fabricate database values.
# 10. After obtaining the result, provide a concise Markdown answer to the user.
# 11. Do not expose your internal reasoning or planning.

# For example, for:
# "What is the name of the customer with the most placed orders?"

# you should inspect the relevant tables, determine the relationship between customers and orders, execute the appropriate SQL query, and answer using the actual returned result.

# Do not stop after generating SQL. The SQL must be executed before answering.

# Your responses should be formatted as Markdown.
# """.strip()
# def create_history() -> List[BaseMessage]:
#     return [SystemMessage(content=SYSTEM_PROMPT)]


# def ask(
#     query: str, history: List[BaseMessage], llm: BaseChatModel, max_iterations: int = 10
# ) -> str:
#     log_panel(title="User Request", content=f"Query: {query}", border_style=green_border_style)

#     n_iterations = 0
#     messages = history.copy()
#     messages.append(HumanMessage(content=query))

#     while n_iterations < max_iterations:
#         response = llm.invoke(messages)
#         messages.append(response)
#         if not response.tool_calls:
#             return response.content
#         for tool_call in response.tool_calls:
#             response = call_tool(tool_call)
#             messages.append(response)
#         n_iterations += 1

#     raise RuntimeError(
#         "Maximum number of iterations reached. Please try again with a different query."
#     )

from datetime import datetime
from typing import Any, Dict, Generator, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from querymancer.logging import green_border_style, log_panel
from querymancer.tools import call_tool


SYSTEM_PROMPT = f"""
You are Querymancer, a master database engineer with exceptional expertise
in SQLite query construction and optimization.

Your purpose is to answer natural-language questions by investigating and
querying the actual SQLite database.

Today is {datetime.now().strftime("%Y-%m-%d")}

You have access to these database tools:

- list_tables: Lists available database tables.
- describe_table: Shows the schema of a table.
- sample_table: Returns sample rows from a table.
- execute_sql: Executes SQL against the database.

IMPORTANT RULES:

1. When a user asks a database question, actually query the database.
2. Do not merely explain how a query could be constructed.
3. Do not provide hypothetical results.
4. Use the database tools when necessary.
5. Construct SQL using the actual database schema.
6. Execute SQL using execute_sql.
7. Base the final answer only on actual database results.
8. If SQL execution fails, correct the SQL and execute it again.
9. Never invent database values.
10. Never hard-code customer names, products, order counts, etc.
11. The answer must always come from the current database contents.
12. Do not expose internal reasoning or chain-of-thought.
13. After obtaining the database result, provide a concise Markdown answer.

Do not stop after generating SQL.
The SQL must actually be executed before answering.
""".strip()


def create_history() -> List[BaseMessage]:
    return [SystemMessage(content=SYSTEM_PROMPT)]


def ask_stream(
    query: str,
    history: List[BaseMessage],
    llm: BaseChatModel,
    max_iterations: int = 10,
) -> Generator[Dict[str, Any], None, None]:

    log_panel(
        title="User Request",
        content=f"Query: {query}",
        border_style=green_border_style,
    )

    messages = history.copy()
    messages.append(HumanMessage(content=query))

    yield {
        "type": "agent_start",
        "message": "Querymancer started processing the request.",
    }

    n_iterations = 0

    while n_iterations < max_iterations:

        yield {
            "type": "agent_thinking",
            "iteration": n_iterations + 1,
            "message": "Analyzing the request.",
        }

        response = llm.invoke(messages)

        messages.append(response)

        # Model has finished.
        if not response.tool_calls:

            yield {
                "type": "final_answer",
                "content": response.content,
            }

            return

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})

            yield {
                "type": "tool_start",
                "tool": tool_name,
                "args": tool_args,
            }

            # Capture actual generated SQL.
            if tool_name == "execute_sql":

                sql_query = tool_args.get("sql_query", "")

                yield {
                    "type": "generated_sql",
                    "sql": sql_query,
                }

            # Execute tool.
            tool_response = call_tool(tool_call)

            yield {
                "type": "tool_result",
                "tool": tool_name,
                "result": tool_response.content,
            }

            messages.append(tool_response)

        n_iterations += 1

    yield {
        "type": "error",
        "message": "Maximum number of agent iterations reached.",
    }


def ask(
    query: str,
    history: List[BaseMessage],
    llm: BaseChatModel,
    max_iterations: int = 10,
) -> str:

    final_answer = ""

    for event in ask_stream(
        query,
        history,
        llm,
        max_iterations,
    ):

        if event["type"] == "final_answer":
            final_answer = event["content"]

    return final_answer