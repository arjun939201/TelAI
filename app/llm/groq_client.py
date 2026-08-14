
"""Single Groq generation wrapper.

All language validation and repair happens locally and must not call this again.
"""
async def generate(client, messages, **kwargs):
    response=await client.chat.completions.create(messages=messages, **kwargs)
    return response.choices[0].message.content or ""
