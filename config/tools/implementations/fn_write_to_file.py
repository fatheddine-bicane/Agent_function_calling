import os

def fn_write_to_file(file_path: str, content: str, append: bool = False) -> bool:
    """
    Writes or appends a given string of text to a specified local file path.
    """
    try:
        # Map the boolean flag to Python's built-in file modes
        file_mode = 'a' if append else 'w'

        # Extract the directory path and create it if it does not exist
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Open the file and write the content
        with open(file_path, file_mode, encoding="utf-8") as file:
            file.write(content)

        return True

    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")
        return False
