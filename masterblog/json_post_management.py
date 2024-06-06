"""
Data structure should be saved in a JSON file, which will be used as a storage file. 
Storage file will contain this data structure, and whenever you need to 
read, update, add or delete a blog post, change it directly.
"""

import os
import json

# Default path configuration
script_base_dir = os.path.dirname(__file__)
folder_to_save = os.path.join(script_base_dir, "data")
if not os.path.exists(folder_to_save):
    os.makedirs(folder_to_save)


class JsonBlog:
    """This class represents a JSON-based blog management system.

    It provides methods to read, update, add, and delete blog posts from a JSON file.

    Attributes:
        path (str): The path to the JSON file.
        blogs (list): A list of blog post dictionaries.

    """

    # Class default saving path
    _file_path = os.path.join(folder_to_save, "blogs.json")

    def __init__(self, file_path: str = None) -> None:
        """Initialize the JsonBlog object.

        Args:
            file_path (str, optional): The path to the JSON file. Defaults to None.

        """
        self.path = file_path if file_path else self._file_path
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as handle:
                json.dump([], handle, indent=4)
        self.blogs = self.read_blog_data()

    def _set_id(self):
        """Set the ID for a new blog post.

        Returns:
            int: The ID for the new blog post.

        """
        if self.blogs:
            max_id = max(item.get("id") for item in self.blogs)
            return max_id + 1
        return 1

    def read_blog_data(self):
        """Read the blog data from the JSON file.

        Returns:
            list: A list of blog post dictionaries.

        """
        try:
            with open(self.path, "r", encoding="utf-8") as blog_data:
                blogs = json.load(blog_data)
            return blogs
        except FileNotFoundError:
            print(f"{self.path} does not exist")
            return None
        except json.JSONDecodeError:
            print("JSON Decoder error")
            return None

    def save_the_blog(self):
        """Save the blog data to the JSON file."""
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.blogs, handle, indent=4)

    def append_to_blogs(self, data: dict):
        """Append a new blog post to the list of blogs.

        Args:
            data (dict): The blog post data.

        """
        data["id"] = self._set_id()
        self.blogs.append(data)
        self.save_the_blog()
