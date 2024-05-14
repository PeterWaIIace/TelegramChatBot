import os

from monitor import timeit
from gpt4all import GPT4All


class Processor:

    def __init__(self):

        #        openai.api_base = "http://localhost:4891/v1"
        #        openai.api_key = "not needed for a local LLM"

        self.model = GPT4All(
            "llama-2-7b-chat.ggmlv3.q4_0.bin",
            #"orca-mini-13b.ggmlv3.q4_0.bin",
            #"ggml-model-gpt4all-falcon-q4_0.bin",
            model_path="./models")
        self.personality = "You are answering user."
        self.name = "TestBot"

    def setPersonality(self, text, name):
        self.personality = text
        self.name = name

    @timeit
    def ask(self, userName: str, text: str, history: str = "") -> str:

        prompt = self.prompt(userName, text, history)
        answer = self.model.generate(prompt, max_tokens=1000)
        return answer

    def prompt(self, user: str, text: str, history: str = "") -> str:
        personality_paylod = f"Your role: {self.personality}\n"
        bot_name_payload = f"Your name: {self.name}\n"
        # history_payload = f"{history}\n"
        user_name_payload = f"User name: {user}\n"
        user_message = f"{history}\n{user}'s message:{text}\n{self.name}'s message:"
        return personality_paylod + bot_name_payload + user_name_payload + user_message

    def think(self, text):
        pass

    def reflect(self, text):
        pass

    def action(self, text):
        pass


if __name__ == "__main__":

    gpt = Processor()
    assistant = "TestBot"
    personality = f"Respond in json with response in TEXT field and information which should be carried to next prompt in CARRY field"

    gpt.setPersonality(personality, assistant)
    prompt = gpt.prompt("user","How are you doing?","")

    print(f"Asking\n{prompt}")
    response = gpt.model.generate(prompt, max_tokens=1000)
    print(f"==============================================\n{response}")

    prompt = gpt.prompt("user","who are you?","")
    print(f"Asking: {prompt}")
    response = gpt.model.generate(prompt, max_tokens=1000)
    print(f"==============================================\n{response}")
    response = gpt.model.generate(prompt, max_tokens=1000)
    print(f"==============================================\n{response}")
    response = gpt.model.generate(prompt, max_tokens=1000)
    print(f"==============================================\n{response}")
