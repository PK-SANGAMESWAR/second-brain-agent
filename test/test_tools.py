# test_tools.py
import ollama

response = ollama.chat(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                }
            }
        }
    }]
)

print(response["message"])
# Should show tool_calls with get_weather and city=Paris
# If you see tool_calls → you're good to go ✅
# If you see plain text → model doesn't support tools, switch models