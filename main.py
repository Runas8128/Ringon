from util.myBot import MyBot

if __name__ == '__main__':
    bot = MyBot(is_testing=True, testCogs=['DeckList'])
    bot.run()
