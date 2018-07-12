
[HOW TO DEPLOY]
https://www.techlila.com/how-to-deploy-php-app-on-heroku-cloud-platform/

[MISSING COMPONENTS]
https://medium.com/@winnieliang/how-to-run-a-simple-html-css-javascript-application-on-heroku-4e664c541b0b

I’ll assume the Heroku app is all set up and the final step is the deployment process. Here’s the simple but yet “not going to argue with you” solution:

Head to root directory of the repo that contains index.html which dictates the main HTML page.
Run touch composer.json to create a file called composer.json.
Add the following line: {} inside.
Run touch index.php to create a file called index.php.
Add the line: <?php include_once("index.html"); ?> inside.
Now update the repo on Github if it’s connected to your account or Heroku command git push heroku master . Wait for the automatic deploy to work its magic and tada!
Now you have access to your Heroku website up and running on ****.herokuapp.com
