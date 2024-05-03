# CSC5201 Final Project
## Xavier Robbins 
---

This GitHub holds the Twitter copy-cat built for my final project of CSC5201. The application provides functionality to post, look at your feed, explore all posts created by all users on the platform, and follow or unfollow users. The application is built in flask with a MySQL database run remotely in a separate docker container. The overall application and associated containers are composed with docker compose and then hosted through digital ocean on a droplet server. The application provides several endpoints representing different portions of the application, described below. 

---

**Route :** /
  - Index for the application, allowing the user to login to their account or register for a new one. 

**Route :** /register 
  - Allows the user to register for an account with an email, username, and password of their choosing. 

**Route :** /login
  - Allows the user to login to an existing account with their username and password. 

**Route :** /logout *Login Required!*
  - Allows the user to logout of their account, interacted with through buttons on the UI, returns user to login page. 

**Route :** /new_post *Login Required!*
  - Allows the user to create a new post, which is associated with their account. 

**Route :** /my_profile *Login Required!*
  - Displays the user profile, allowing them to see the posts they have created. 

**Route :** /profile/<username> *Login Required!*
  - Displays another user's profile, allows the current user to follow or unfollow this user. 

**Route :** /feed *Login Required!*
  - Displays the user's feed, showing all posts from themselves and the users they are following. 

**Route :** /explore *Login Required!*
  - Displays the explore page of the application, showing all posts from all users on the app. 

**Route :** /follow/<username> *Login Required!*
  - Allows the user to follow another user, explored throught the `/profile/<username>` endpoint when the user is not following the user account displayed on this endpoint. 

**Route :** /unfollow/<username> *Login Required!*
  - Allows the user to unfollow a user, exposed through the `profile/<username>` endpoint when the user is following the user account displayed on this endpoint. 

---



