

class Historian:

    def __init__(self, memory):
        self.memory = memory
        pass

    def getPast(self, chatID):
        history = ""
        messages = self.memory.recall(f"{chatID}.json")
        for message in messages:
            user = message["message"]["from"]["first_name"]
            text = message["message"]["text"]
            history += f"{user}'s message: {text}\n"

        return history
