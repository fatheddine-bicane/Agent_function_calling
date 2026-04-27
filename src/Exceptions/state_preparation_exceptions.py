class MultipleFunctionDefinitionException(Exception):
    def __init__(self):
        self.message = "Function definition file cannot contain more than one definition"
        super().__init__(self.message)
