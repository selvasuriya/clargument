from paraivari.parser import parseControl as parse
import sys

quotes = ('A man is not complete until he is married. Then he is finished.',
    'As I said before, I never repeat myself.',
    'Behind a successful man is an exhausted woman.',
    'Black holes really suck...',
    'Facts are stubborn things.'
)

lucks = ('You will soon get promoted.',
    'Now is the time to think about building your new house.',
    'There is a chance for meeting an important person in your life.',
    'Use pearl to increase your chance for a lucky drop..!',
    'Don\'t buy any vehicles, this is a bad time!'
)

class QuoteModel:
    def get_quote(self, n):
        try:
            value = quotes[n]
        except IndexError as err:
            value = "Not found!"
        return value

    def show_luck(self, n):
        try:
            value = lucks[n]
        except IndexError as err:
            value = "No Luck!"
        return value

class QuoteTerminalView:
    def show(self, quote):
        print(f"And the quote is: \"{quote}\"")

    def luckyDrop(self, luck):
        print(f"Let's see your luck today: \"{luck}\"")

    def error(self, msg):
        print(f"Error: \"{msg}\"")

    def select_quote(self):
        return input("Which quote number would you like to see? ")

class QuoteTerminalController:
    def __init__(self):
        self.model = QuoteModel()
        self.view = QuoteTerminalView()

    def run(self):
        valid_input = False
        while not valid_input:
            n = self.view.select_quote()
            try:
                n = int(n)
                quote = self.model.get_quote(n)
                self.view.show(quote)
            except ValueError as err:
                self.view.error(f"Incorrect index '{n}'")
            else:
                valid_input = True

    def showQuote(self, args):
        # fetch data
        n = args["q"].value[0]

        # validate data
        try:
            n = int(n)

            # get result from model
            quote = self.model.get_quote(n)

            # show result with a view
            self.view.show(quote)

        except ValueError as err:
            self.view.error(f"Incorrect index '{n}'")


    def showLuck(self, args):
        n = args["l"].value[0]

        try:
            n = int(n)
            luck = self.model.show_luck(n)
            self.view.luckyDrop(luck)
        except ValueError as err:
            self.view.error(f"Incorrect index '{n}'")
        

if __name__ == "__main__":

    controller = QuoteTerminalController()
    #while True:
        #controller.run()
    
    config_data = {
        "thedirectcommand": {
            "argument_value_properties": {"q":[1], "l":[1]},
            "overloading": [
                            {
                    "local": ["q"],
                    "func": controller.showQuote
                },
                {
                    "local": ["l"],
                    "func": controller.showLuck
                }
            ]
        }
    }
    args = sys.argv[1:]

    parse(args, config_data)

