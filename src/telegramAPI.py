import requests
import json
import time
import queue
import logging
import threading

# user defined libraries
from monitor import Monitor


def tryRepeat(tries, wait_s):

    def wrap(func):
        def promptWrapper(*args):
            counter = 0
            ret_val = None

            if "return" in func.__annotations__:
                ret_val = func.__annotations__["return"]()

            while counter < tries:
                try:
                    ret_val = func(*args)
                    break
                except Exception:
                    print(f"[ERROR] Failed to execute {func}")
                    counter += 1
                    time.sleep(wait_s)

            return ret_val

        return promptWrapper
    return wrap


class TelegramAPI:

    def __init__(self, configPath="botConfig.json", onMessage=None) -> None:
        logging.info('telegramBot initializing')

        self.monitor = Monitor()

        self.onMessage = onMessage
        self.rxQueue = queue.Queue()

        self.messenger = "telegram"
        self.updateId = 0
        self.prevId = 0
        self.run = True
        with open(configPath, "r") as fJson:
            config = json.load(fJson)
            self.token = config["token"]
            self.botAddr = config["botAddr"] + self.token
        self.__flushMessages()

        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def __del__(self):
        self.stop()

    def stop(self):
        self.run = False
        self.thread.join()

    def __flushMessages(self):
        logging.info('telegramBot __findLastUpdateId')
        responses = requests.get(self.botAddr + "/getUpdates").json()

        for response in responses["result"]:
            self.updateId = response["update_id"]

    @tryRepeat(6, 60)
    def sendMessage(self, message, chatID):
        print(f"send message: {message} chatID: {chatID}")
        logging.info('telegramBot sendMessage')

        payload_chatId = f"/sendMessage?chat_id={chatID}"
        payload_message = f"&parse_mode=Markdown&text={message}"
        payload = payload_chatId + payload_message

        response = requests.get(self.botAddr + payload)
        return response.json()

    @tryRepeat(6, 60)
    def respondMessage(self, messageReplyID, reply, chatID):
        logging.info('telegramBot sendMessage')

        payload_chatId = f"/sendMessage?chat_id={chatID}"
        payload_message = f"&parse_mode=Markdown&text={reply}"
        payload_reply_to = f"&reply_to_message_id={messageReplyID}"
        payload = payload_chatId + payload_message + payload_reply_to

        response = requests.get(self.botAddr + payload)
        return response.json()

    def __setMaxOffset(self):
        requests.get(self.botAddr + f"/getUpdates?offset={self.updateId+1}")

    @tryRepeat(1, 60)
    def __getUpdates(self) -> list:
        logging.info('telegramBot getUpdate')

        querry = self.botAddr + "/getUpdates"

        # convert json of updates to list so it can be used as iterator

        response = requests.get(querry).json()
        if response["ok"]:
            return response["result"]
        else:
            return []

    def __getUsername(self, updateMsg):
        logging.info('telegramBot __getUsername')
        if "username" in updateMsg["from"]:
            return updateMsg["from"]["username"]
        else:
            return updateMsg["from"]["first_name"]

    def __isItNewID(self):
        if self.updateId > self.prevId:
            self.prevId = self.updateId
            return True
        return False

    def __filter(self, message, msgType="text"):
        logging.info('telegramBot processUpdate')

        msgKey = 'message'
        if msgKey not in message.keys() and "edited_message" in message.keys():
            msgKey = "edited_message"

        if msgKey not in message.keys():
            pass
        if msgKey in message.keys():
            if msgType in message[msgKey].keys():
                self.updateId = message["update_id"]
                return message
        return None

    def loop(self):
        while (self.run):
            for update in self.__getUpdates():
                self.__filter(update, "text")
                self.__setMaxOffset()
                if self.__isItNewID():
                    if self.onMessage:
                        self.onMessage(update)
                    else:
                        self.rxQueue.put(update)
                        self.monitor.addStatus(
                            "telegram", {
                                "rxQueueSize": self.rxQueue.qsize()})

    def getMessage(self):
        retMessage = self.rxQueue.get()
        self.monitor.addStatus("telegram",
                               {"rxQueueSize": self.rxQueue.qsize()})
        return retMessage


class TelegramBot:

    def __init__(self, onMessage):

        self.onMessage = onMessage
        self.api = TelegramAPI(
            "src/botConfig.json",
            lambda message: self.process(message))

    def process(self, message):
        response = None
        try:
            chatId = message["message"]["chat"]["id"]
            messageId = message["message"]["message_id"]

        except Exception as e:
            print(f"Following message caused exception: {message}\nException: {e}")
            return

        print(f"receiving message: {message}")
        response = self.onMessage(message)
        if response:
            self.api.respondMessage(messageId, response, chatId)

def respond(message):
    if message["message"]["chat"]["type"] == "private":
        return "Message was received"


if __name__ == "__main__":

    TB = TelegramBot(lambda message: respond(message))

    while (True):
        pass
