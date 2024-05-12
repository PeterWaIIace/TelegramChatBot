from telegramAPI import TelegramBot
from llmprocessor import Processor
from contexter import Contexter
from historian import Historian


def answer2Telegram(answer, chatID):
    answerTlgrm = {
        "message": {
            "from": {
                "first_name": processor.name}, "chat": {
                "id": chatID}, "text": answer}}
    return answerTlgrm


if __name__ == "__main__":

    processor = Processor()
    JohnMnemonic = Contexter()
    historian = Historian(JohnMnemonic)

    def respond(message):

        first_name = message["message"]["from"]["first_name"]
        text = message["message"]["text"]
        chatID = message["message"]["chat"]["id"]

        if "reply_to_message" in message['message'].keys():
           text += f" (reply to {message['message']['reply_to_message']['from']['first_name']})"
        answer = ""

        print(f"message:{text}")
        if message["message"]["chat"]["type"] == "private":
            history = historian.getPast(chatID)
            answer = processor.ask(first_name, text, history)
        elif message["message"]["chat"]["type"] in [
                "supergroup", "group"] and processor.name.lower() in text.lower():
            history = historian.getPast(chatID)
            answer = processor.ask(first_name, text, history)

        print(f"answer:{answer}")
        JohnMnemonic.memorise(f"{chatID}.json", message)

        if answer:
            JohnMnemonic.memorise(
                f"{chatID}.json", answer2Telegram(
                    answer, chatID))

        return answer

    TelegramBot(lambda message: respond(message))
