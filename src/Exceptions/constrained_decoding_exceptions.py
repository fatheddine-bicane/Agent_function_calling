class ModelExceedTokensLimitException(Exception):
    def __init__(self, max_new_tokens: int):
        self.message = f"Circuit breaker hit! Model forced to stop at {max_new_tokens} tokens."
        super().__init__(self.message)
