import re


class MessageManagementSystem:

    waiting_functions = dict()

    @classmethod
    async def on_message(cls, message, user):

        success = False
        for pattern in cls.waiting_functions:
            if re.search(pattern, message.content):
                functions = cls.waiting_functions[pattern]

                completed = []
                for function in functions:

                    result = await function(user=user, message=message)

                    if result:
                        completed.append(function)

                    success |= bool(result)
        return success

    @classmethod
    def subscribe_message(cls, message_pattern, function):

        if message_pattern not in cls.waiting_functions:
            cls.waiting_functions[message_pattern] = []

        cls.waiting_functions[message_pattern].append(function)

    @classmethod
    def unsubscribe_message(cls, message_pattern, function):

        cls.waiting_functions[message_pattern].remove(function)

        if len(cls.waiting_functions[message_pattern]) == 0:
            del cls.waiting_functions[message_pattern]



