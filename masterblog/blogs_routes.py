"""Blogs related BluePrint"""

from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from json_post_management import JsonBlog, os
from post_forms import BlogForm

script_base_dir = os.path.dirname(__file__)
folder_to_save = os.path.join(script_base_dir, "data")
if not os.path.exists(folder_to_save):
    os.makedirs(folder_to_save)

FILE_PATH = os.path.join(folder_to_save, "blogs.json")

posts = Blueprint("blog", __name__, url_prefix="/blogs", template_folder="templates")


@posts.route("/")
def home():
    """Home Page"""
    return render_template("index.html", page_name="index")


@posts.route("/blog_add", methods=["GET", "POST"])
def blog_add():
    """
    Blog Add route.
    This route will handle both GET and POST requests.
    For a GET request, it will render the form to add a new blog.
    For a POST request, it will validate the form and add a new blog to the JSON file.
    """
    form = BlogForm(file_path=FILE_PATH)
    if form.validate_on_submit():
        blog = {
            "title": form.title.data.strip().title(),
            "author": form.author.data.strip().title(),
            "content": form.content.data.strip(),
        }
        the_blogs = JsonBlog(file_path=FILE_PATH)
        the_blogs.append_to_blogs(data=blog)
        the_blogs.save_the_blog()
        flash(message="Form Submitted successfuly")
        return redirect(url_for("blog.blogs_all"))
    return render_template("blog_add.html", page_name="Add Blog", form=form)


@posts.route("/blogs", methods=["GET"])
def blogs_all():
    """Displays All Blogs Entries"""
    the_blogs = JsonBlog(file_path=FILE_PATH)
    blogs = the_blogs.blogs
    return render_template("blogs_all.html", page_name="All Blogs", blogs=blogs)


@posts.route("/blogs/<int:idx>")
def get_blog(idx: int):
    """Only display the blog by given ID"""
    the_blogs = JsonBlog(file_path=FILE_PATH)
    data = the_blogs.blogs
    blog = next((adict for adict in data if adict.get("id") == idx), None)
    if not blog:
        flash("Invalid Blog ID")
        abort(404, description="404 Blog Not Found")
    return render_template("blog_get.html", page_name="The Blog", blog=blog)


@posts.route("/blogs/update/<int:idx>", methods=["GET", "POST"])
def blog_update(idx: int):
    """Only update the blog by given ID"""
    the_blogs = JsonBlog(file_path=FILE_PATH)
    lst = the_blogs.blogs
    blog = next((adict for adict in lst if adict.get("id") == idx), None)
    if not blog:
        flash("Invalid Blog ID for update")
        abort(404, description="404 Blog Not Found")
    form = BlogForm()
    if request.method == "POST":
        blog["author"] = form.author.data.strip().title()
        blog["title"] = form.title.data.strip().title()
        blog["content"] = form.content.data.strip().title()
        the_blogs.save_the_blog()
        flash("Form updated successfully")
        return redirect(url_for("blog.blogs_all"))
    form.author.data = blog.get("author")
    form.title.data = blog.get("title")
    form.content.data = blog.get("content")
    return render_template("blog_update.html", page_name="Update Blog", form=form)


@posts.route("/blogs/delete/<int:idx>")
def blog_delete(idx: int):
    """Only delete the blog by given ID"""
    the_blog = JsonBlog(file_path=FILE_PATH)
    blogs = the_blog.blogs
    blog = next((adict for adict in blogs if adict.get("id") == idx), None)
    if not blog:
        flash("Invalid Blog ID for delete")
        abort(404, description="404 Blog Not Found")
    blogs.remove(blog)
    the_blog.save_the_blog()
    flash("Blog deleted successfully")
    return redirect(url_for("blog.blogs_all"))


@posts.route("/blogs/like/<int:idx>")
def blog_like(idx: int):
    """Adds LIKE attribute to chosen blog dictionary"""
    the_blog = JsonBlog(file_path=FILE_PATH)
    blogs = the_blog.blogs
    blog = next((adict for adict in blogs if adict.get("id") == idx), None)
    if not blog:
        flash("Invalid Blog ID to like")
        abort(404, description="404 Blog Not Found")
    if "like" not in blog:
        blog["like"] = 0
    blog["like"] += 1
    the_blog.save_the_blog()
    return render_template("blog_get.html", page_name="The Blog", blog=blog)


@posts.errorhandler(404)
def page_not_found(error):
    """Handles page not found errors"""
    return render_template("errors.html", message=error.description), 404


@posts.errorhandler(500)
def internal_server_error(error):
    """Handles internal server error"""
    return render_template("500.html", message=error.description), 500
