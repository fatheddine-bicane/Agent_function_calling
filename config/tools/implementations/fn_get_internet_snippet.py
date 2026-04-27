from ddgs import DDGS

def fn_get_internet_snippet(topic: str) -> str:
    """
    Searches the internet for a given topic and returns a text snippet
    from the top search result.
    """
    try:
        # initialize the DuckDuckGo search client
        with DDGS() as ddgs:
            # fetch the first result for the given topic
            results = list(ddgs.text(topic, max_results=1))

            if results:
                # return the 'body' of the result, which contains the snippet
                return results[0].get("body", "No snippet available for this result.")
            else:
                return "No results found for this topic."

    except Exception as e:
        return f"An error occurred during the search: {e}"
