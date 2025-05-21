# from langchain.chat_models import ChatOpenAI
# from langchain.schema import SystemMessage, HumanMessage

# # 1. Instantiate a chat model (defaults to OpenAI's gpt-3.5-turbo chat endpoint)
# chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# # 2. Build a sequence of messages with roles
# messages = [
#     SystemMessage(content="You are a helpful assistant."),
#     HumanMessage(content="Can you explain the difference between a list and a tuple in Python?")
# ]

# # 3. Invoke the model
# response = chat(messages)

# # 4. The response is an AIMessage; print its content
# print(response.content)
