from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)


# loading the data
def load_data():
    """
        Load all blog posts from the data.json file.

        Returns:
            dict: A dictionary of blog posts where each key is a post ID.
        """
    with open("data.json", "r") as data_file:
        return json.load(data_file)


# saving the data
def save_data(posts):
    """
        Save blog posts to the data.json file.

        Args:
            posts (dict): A dictionary of blog posts to be saved.
        """
    with open("data.json", "w") as data_file:
        json.dump(posts, data_file, indent=4)


@app.route("/")
def index():
    """
        Display all blog posts on the homepage with optional search and sort functionality.

        Query Parameters:
            search (str): A keyword to filter posts by title or author.
            sort_by (str): The field to sort posts by ('title', 'author', or 'content').
            order (str): The sort order ('asc' for ascending, 'desc' for descending).

        Returns:
            Rendered HTML page showing a list of blog posts.
        """
    blog_posts = load_data()

    posts = []
    for post_id, post in blog_posts.items():
        post_with_id = post.copy()
        post_with_id['id'] = post_id
        posts.append(post_with_id)

    search_query = request.args.get("search", "").lower()
    sort_by = request.args.get("sort_by", "title")
    order = request.args.get("order", "asc")

    if search_query:
        filtered_posts = []
        for post in posts:
            title = post['title'].lower()
            author = post['author'].lower()
            if search_query in title.lower() or search_query in author.lower():
                filtered_posts.append(post)
        posts = filtered_posts

    def get_sort_value(all_posts):
        return all_posts[sort_by].lower()

    reverse_order = order == "desc"
    if sort_by in ['title', 'author', 'content']:
        posts.sort(key=get_sort_value, reverse=reverse_order)


    return render_template("index.html", posts=posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    """
        Handle the creation of a new blog post.

        GET: Show a form to create a new post.
        POST: Save the new post and redirect to the homepage.

        Returns:
            Rendered HTML page or redirect response.
        """
    if request.method == "POST":
        author = request.form["author"]
        title = request.form["title"]
        content = request.form["content"]

        blog_posts = load_data()
        max_id = 0
        for id_num in blog_posts.keys():
            num_val = int(id_num.split("_")[1])
            if num_val > max_id:
                max_id = num_val
        new_id = f"id_{max_id + 1}"

        blog_posts[new_id] = {
            "author": author,
            "title": title,
            "content": content
        }
        save_data(blog_posts)

        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/delete/<post_id>", methods=["GET", "POST"])
def delete(post_id):
    """
        Delete a blog post by its ID.

        Args:
            post_id (str): The ID of the post to delete.

        Returns:
            Redirect to the homepage after deletion.
        """
    posts = load_data()

    if post_id in posts:
        del posts[post_id]

        save_data(posts)

    return redirect(url_for("index"))


@app.route("/update/<post_id>", methods=["GET", "POST"])
def update(post_id):
    """
        Update an existing blog post by its ID.

        GET: Show a form to edit the post.
        POST: Save the updated post and redirect to the homepage.

        Args:
            post_id (str): The ID of the post to update.

        Returns:
            Rendered HTML page or redirect response.
        """

    all_posts = load_data()

    if request.method == "POST":
        author = request.form.get("author")
        title = request.form.get("title")
        content = request.form.get("content")

        if post_id in all_posts:
            all_posts[post_id] = {
                "author": author,
                "title": title,
                "content": content
            }
            save_data(all_posts)

            return redirect(url_for("index"))
    post = all_posts.get(post_id)

    return render_template("update.html", post=post, post_id=post_id)


if __name__ == "__main__":
    app.run(port=5000, debug=True)