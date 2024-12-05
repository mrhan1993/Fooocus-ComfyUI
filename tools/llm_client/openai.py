from openai import OpenAI

from tools.logger import common_logger


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initializes the OpenAI API client.

        :param api_key: OpenAI API key.
        :param model: Model to use for the queries (default: "gpt-4o").
        """
        self.model = model
        self.__client = OpenAI(
            api_key=api_key,
            base_url=None
        )

    def query(self, prompt: str, system_prompt: str, max_tokens: int = 4096) -> str:
        """
        Sends a query to the OpenAI API and returns the response as a string.

        :param prompt: The input prompt to send to the model.
        :param system_prompt: The system prompt to send to the model.
        :param max_tokens: Maximum tokens to include in the response (default: 4096).
        :return: The response from the model as a string.
        """
        try:
            response = self.__client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            common_logger.error(f"[OpenAI] Error in chat completion: {e}, model: {self.model}")
            return ""

    def describe_image(self, image: str, level: str = "auto") -> str:
        """
        Describes an image using the OpenAI API.
        :param image: Either a URL of the image or the base64 encoded image data.
        :param level: By controlling the detail parameter, which has three options, low, high, or auto
                    docs here: https://platform.openai.com/docs/guides/vision#low-or-high-fidelity-image-understanding
        :return: image detail
        """
        prompt = "analyze the image in detail, including the overall description, style, subject details, background, and other parts that are not easy to notice."
        system_prompt = "generate a prompt for midjourney based on the user-provided text without including parameter information"
        try:
            response = self.__client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image,
                                "detail": level
                            }
                        }
                    ]}
                ],
                max_tokens=4096
            )
            image_prompt = self.query(response['choices'][0]['message']['content'], system_prompt=system_prompt)
            return image_prompt
        except Exception as e:
            common_logger.error(f"[OpenAI] Error in describe image: {e}, model: {self.model}")
            return ""