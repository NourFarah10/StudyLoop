# StudyLoop

#### Video Demo: <https://youtu.be/8q27D-EDdgE>

#### Description:

StudyLoop is a web-based educational community platform designed to help students connect with other students who are studying the same courses, share knowledge, ask questions, discuss topics, and exchange useful learning resources.

The idea behind StudyLoop came from a common problem faced by students: when learning a course independently, it can be difficult to find other people who are studying the same material. StudyLoop provides a dedicated environment where students can discover communities based on courses or subjects and participate in discussions with other learners.

The application was developed using Python, Flask, SQLite, HTML, CSS, JavaScript, and Bootstrap. I developed the project independently and worked on both the backend and frontend of the application.

## Features

### User Authentication

StudyLoop allows users to create accounts and securely log in to the application. User passwords are stored as password hashes rather than plain-text passwords.

Users can log in and log out of their accounts, and protected pages require authentication before they can be accessed.

### Communities

The main feature of StudyLoop is its community system.

Users can:

- Search for communities.
- View communities they have joined.
- Create new communities.
- Join existing communities.
- Leave communities.
- View community information.
- Edit communities they created.

When a user creates a community, they automatically become a member of that community.

Each community contains information such as its name, description, category, creator, and optional cover image.

### Community Search

StudyLoop includes a community search system that allows users to search for communities by name.

The search functionality is implemented using a Flask API endpoint and JavaScript can request community data dynamically without requiring the entire page to be reloaded.

Search results also indicate whether the current user has already joined a community.

### Posts

Members of a community can create posts.

Posts contain:

- A title.
- Text content.
- A category/tag.
- Optional images or videos.
- The author.
- The creation date.

Posts can be categorized as Question, Discussion, Notes, Resource, or Project.

Users can edit and delete their own posts.

### Image and Video Uploads

StudyLoop supports uploading media files to posts.

Supported image formats include:

- JPG
- JPEG
- PNG
- WebP
- GIF

Supported video formats include:

- MP4
- WebM
- MOV

Multiple media files can be attached to a single post.

Uploaded files are given unique filenames using UUIDs before being stored on the server. The application stores the file information in the `post_media` database table while the actual files are stored in the application's upload directory.

When editing a post, users can remove existing media or add additional images and videos.

### Comments

Users can comment on posts inside communities. This allows students to discuss questions and respond to other students' posts.

### Post Reactions

Users can react to posts using different reactions such as:

- Like
- Love
- Care
- Haha
- Wow
- Sad
- Angry

The application keeps track of the total number of reactions and the number of each individual reaction type.

It also determines the current user's reaction to each post so the interface can display the appropriate state.

### Profiles

Users have profiles containing information associated with their accounts, including profile images.

Profile images can be displayed alongside posts and throughout the application.

## Technologies

StudyLoop was developed using the following technologies:

### Backend

- Python
- Flask
- SQLite
- Werkzeug

Flask is responsible for routing, request handling, sessions, authentication, rendering templates, and API endpoints.

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap

HTML and Jinja templates are used to structure the pages and dynamically display information received from Flask.

CSS is used to customize the appearance of the application, while JavaScript provides client-side interactions such as media previews and dynamic community searching.

### Database

StudyLoop uses SQLite as its database.

The database contains tables for users, communities, community membership, posts, comments, reactions, and post media.

Relationships between tables allow the application to connect users with communities, posts, comments, reactions, and uploaded media.

## Project Structure

### `app.py`

`app.py` is the main Flask application. It initializes the Flask application, configures the application, registers the different blueprints, and starts the application.

### `helpers.py`

This file contains helper functionality shared across the application. One important helper is the `login_required` decorator, which protects routes that require the user to be authenticated.

### `database/db.py`

This file contains the database connection functionality used by the application. Routes use the database helper to obtain a connection to the SQLite database.

### `schema.sql`

`schema.sql` contains the SQL statements used to create the application's database tables and define their relationships.

The database includes tables such as:

- `users`
- `communities`
- `community_members`
- `posts`
- `comments`
- `post_reactions`
- `post_media`

### `routes/community.py`

`community.py` contains the routes related to communities.

It handles functionality such as:

- Community searching.
- Displaying communities.
- Creating communities.
- Editing communities.
- Joining communities.
- Leaving communities.
- Displaying posts inside a community.

### `routes/post.py`

`post.py` contains the routes responsible for post management.

It handles:

- Creating posts.
- Editing posts.
- Deleting posts.
- Uploading post media.
- Removing post media.

It also contains helper functions for saving and deleting uploaded media files.

### `templates/`

The `templates` directory contains the Jinja HTML templates used by Flask.

The templates are organized into different sections of the application, including authentication, communities, posts, profiles, and other pages.

### `static/`

The `static` directory contains frontend resources such as:

- CSS files.
- JavaScript files.
- Images.
- Uploaded files.

The CSS files provide the application's visual design, while JavaScript files provide client-side functionality.

## Database Design

The database was designed around the relationships between users, communities, and posts.

A user can join multiple communities, and a community can contain multiple users. This many-to-many relationship is implemented using the `community_members` table.

Posts belong to a specific community and are created by a specific user.

Comments belong to posts and are created by users.

Post reactions connect users to posts while storing the type of reaction.

Post media is stored separately from the `posts` table so that a post can contain multiple images or videos.

This separation makes it possible to support multiple media files per post instead of limiting every post to a single attachment.

## Design Decisions

One important design decision was separating communities from community membership. Instead of storing a list of users directly inside a community, the application uses the `community_members` table. This makes it possible for users to belong to multiple communities while maintaining a normalized relational database structure.

Another design decision was storing post media in a separate `post_media` table. A post can contain multiple images and videos, so storing media directly in the `posts` table would make the database structure less flexible.

For uploaded files, unique UUID-based filenames are generated before saving files to the server. This prevents filename collisions when different users upload files with the same original filename.

The application also separates its Flask routes into blueprints. For example, community functionality is handled by the community blueprint while post functionality is handled by the post blueprint. This keeps the project organized and makes the application easier to maintain as it grows.

I also chose to use SQLite because it is lightweight, simple to configure, and appropriate for the scope of this project. It allowed me to focus on implementing the application's functionality without requiring a separate database server during development.

## Security and Validation

StudyLoop validates important form fields before inserting data into the database.

Authentication-protected routes use the `login_required` decorator so that users cannot access certain functionality without logging in.

Users can only edit or delete their own posts, and only the creator of a community can edit that community.

Uploaded media is checked against a list of supported file extensions before being saved.

User passwords are stored using password hashing rather than storing the original password.

## What I Learned

Developing StudyLoop gave me practical experience building a complete web application rather than isolated programming exercises.

Through this project, I practiced working with Flask routes, sessions, authentication, SQL databases, relational database design, Jinja templates, HTML forms, JavaScript, file uploads, API endpoints, and frontend/backend communication.

I also learned the importance of organizing a larger application into separate modules and designing database relationships before implementing features.

The project also helped me understand how individual features such as authentication, communities, posts, comments, reactions, and media uploads can work together as one complete application.

## Future Improvements

There are several features that could be added to StudyLoop in the future.

Possible improvements include:

- Notifications for comments and reactions.
- Direct messaging between users.
- Following other users.
- Community moderators and administrators.
- Community privacy settings.
- More advanced community search and filtering.
- Post pagination.
- Improved media storage and processing.
- Real-time notifications.
- Mobile applications for Android and iOS.
- Recommendation systems that suggest communities based on the user's courses and interests.

## Conclusion

StudyLoop was created as a platform where students can learn together rather than studying completely alone. It combines course-based communities with posts, discussions, comments, reactions, and media sharing to create a collaborative learning environment.

The project allowed me to apply concepts learned throughout CS50x to a complete application and gave me experience designing, implementing, debugging, and organizing a real-world software project.