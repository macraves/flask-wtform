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


class CorruptBlogFile(Exception):
    """Raised when saving would overwrite a corrupt or unreadable data file."""


class JsonBlog:
    """This class represents a JSON-based blog management system.

    It provides methods to read, update, add, and delete blog posts from a JSON file.

    Attributes:
        path (str): The path to the JSON file.
        blogs (list): A list of blog post dictionaries.
        corrupt (bool): True if the file could not be read as a list of posts.

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
        self.corrupt = False
        self.blogs = self.read_blog_data()
        self._next_id = self._load_next_id()

    @property
    def _counter_path(self):
        """str: Path of the sidecar file that stores the next free ID."""
        return self.path + ".next_id"

    def _load_next_id(self):
        """Work out the next free ID so deleted IDs are never reused.

        Returns:
            int: The larger of the stored counter and highest existing ID + 1.

        """
        next_id = 1
        if self.blogs:
            next_id = max(item.get("id") for item in self.blogs) + 1
        try:
            with open(self._counter_path, "r", encoding="utf-8") as handle:
                next_id = max(next_id, int(handle.read().strip()))
        except (OSError, ValueError):
            pass
        return next_id

    def _set_id(self):
        """Set the ID for a new blog post.

        Returns:
            int: The ID for the new blog post.

        """
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def read_blog_data(self):
        """Read the blog data from the JSON file.

        Returns:
            list: A list of blog post dictionaries; empty (and ``corrupt`` is
            set) if the file is missing, unreadable or not a list.

        """
        try:
            with open(self.path, "r", encoding="utf-8") as blog_data:
                blogs = json.load(blog_data)
            if not isinstance(blogs, list):
                raise ValueError("blog data is not a list")
            return blogs
        except (OSError, ValueError):
            print(f"{self.path} is missing or corrupt")
            self.corrupt = True
            return []

    def save_the_blog(self):
        """Save the blog data to the JSON file.

        Raises:
            CorruptBlogFile: If the file was corrupt when read; it is not overwritten.

        """
        if self.corrupt:
            raise CorruptBlogFile(f"{self.path} is corrupt; refusing to overwrite")
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.blogs, handle, indent=4)
        with open(self._counter_path, "w", encoding="utf-8") as handle:
            handle.write(str(self._next_id))

    def append_to_blogs(self, data: dict):
        """Append a new blog post to the list of blogs.

        Args:
            data (dict): The blog post data.

        """
        data["id"] = self._set_id()
        self.blogs.append(data)
        self.save_the_blog()
