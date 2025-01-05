import re

from openai import OpenAI
from zhipuai import ZhipuAI

from tools.logger import common_logger
from apis.models.settings import LlmSetting, LlmList


class LlmClient:
    def __init__(self, setting: LlmSetting):
        """
        Initializes the OpenAI API client.
        :param setting: setting for llm
        """
        self.__conf = setting
        try:
            if setting.choice == LlmList.zhipu:
                self.__client = ZhipuAI(api_key=setting.api_key)
            else:
                self.__client = OpenAI(
                    api_key=setting.api_key,
                    base_url=setting.base_url
                )
        except Exception as e:
            common_logger.error(f"[OpenAI] Error in initialization: {e}")

    def query(self, prompt: str, system_prompt: str) -> str:
        """
        Sends a query to the OpenAI API and returns the response as a string.
        :param system_prompt:
        :param prompt: The input prompt to send to the model.
        :return: The response from the model as a string.
        """
        try:
            response = self.__client.chat.completions.create(
                model=self.__conf.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}],
                max_tokens=self.__conf.max_tokens
            )
            if not self.__conf.choice == LlmList.openai:
                return response.choices[0].message.content.strip()
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            common_logger.error(f"[OpenAI] Error in chat completion: {e}, model: {self.__conf.text_model}")
            return ""

    def optimize_prompt(self, prompt: str) -> str:
        """
        Optimizes a prompt using the OpenAI API.
        :param prompt: The input prompt to optimize.
        :return: The optimized prompt as a string.
        """
        return self.query(prompt, system_prompt=self.__conf.prompt_optimize)

    def translate(self, prompt: str) -> str:
        """
        Translates a prompt using the OpenAI API.
        :param prompt: The input prompt to translate.
        :return: The translated prompt as a string.
        """
        try:
            return self.query(prompt, system_prompt=self.__conf.prompt_translate)
        except Exception as e:
            common_logger.error(f"[OpenAI] Error in translate: {e}, model: {self.__conf.text_model}")
            return prompt

    def describe_image(self, image: str) -> str:
        """
        Describes an image using the OpenAI API.
        :param image: Either a URL of the image or the base64 encoded image data. If the image is base64, it should be
                    like this: f\"data:image/jpeg;base64,{base64_image}"
        :return: image detail
        """
        try:
            re.match(r'^(gpt|glm-4v)', self.__conf.text_model.lower()).group()
        except AttributeError:
            common_logger.warning(f"[OpenAI] model {self.__conf.text_model} does not support image description, check openai docs: "
                                  f"https://platform.openai.com/docs/guides/vision#low-or-high-fidelity-image-understanding")
            return ""

        prompt = "analyze the image in detail, including the overall description, style, subject details, background, and other parts that are not easy to notice."
        system_prompt = "generate a prompt for midjourney based on the user-provided text without including parameter information"
        if not image.startswith("http") and not image.startswith("data"):
            image = f"data:image/jpeg;base64,{image}"
        try:
            response = self.__client.chat.completions.create(
                model=self.__conf.image_model,
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image
                            }
                        }
                    ]}
                ],
                max_tokens=4096
            )
            if self.__conf.choice == LlmList.zhipu:
                image_prompt = self.query(response.choices[0].message.content.strip(), system_prompt=system_prompt)
            else:
                image_prompt = self.query(response['choices'][0]['message']['content'], system_prompt=system_prompt)
            return image_prompt
        except Exception as e:
            common_logger.error(f"[OpenAI] Error in describe image: {e}, model: {self.__conf.image_model}")
            return ""
