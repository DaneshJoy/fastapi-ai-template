# import google.generativeai as genai
from openai import OpenAI
from config import Settings

settings = Settings()

client = OpenAI(api_key=settings.OPENAI_API_KEY)
from config import Settings

settings = Settings()


class LLMService:
    def __init__(self):
        # genai.configure(api_key=settings.GEMINI_API_KEY)
        # self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.model = "gpt-4.1-mini"

    def generate_response(self, query: str, search_results: list[dict]):

        context_text = "\n\n".join(
            [
                f"Source {i+1} ({result['url']}):\n{result['content']}"
                for i, result in enumerate(search_results)
            ]
        )

        # full_prompt = f"""
        # Context from web search:
        # {context_text}
        #
        # Query: {query}
        #
        # Please provide a comprehensive, detailed, well-cited accurate response using the above context.
        # Think and reason deeply. Ensure it answers the query the user is asking. Do not use your knowledge until it is absolutely necessary.
        # """
        #
        # response = self.model.generate_content(full_prompt, stream=True)
        #
        # for chunk in response:
        #     yield chunk.text

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a smart and thorough AI assistant. Use the context provided to answer the user’s query as accurately as possible. "
                    "Cite the sources clearly if used. Only rely on your own knowledge when absolutely necessary."
                ),
            },
            {
                "role": "user",
                "content": f"Context from web search:\n{context_text}\n\nQuery: {query}",
            },
        ]

        response = client.chat.completions.create(model=self.model,
            messages=messages,
            stream=True)

        for chunk in response:
            # if "choices" in chunk and chunk.choices[0].get("delta", {}).content:
            yield chunk.choices[0].delta.content
