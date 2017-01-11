<h1>google_api_functions</h1>
<p>
  Functions providing a layer of abstraction to make it easier to use Google APIs.
  The code in this repository is mostly just modified from tutorials and documentation
  provided by Google. Some things had to be changed so everything would work with Python 3.
  <br>
  Below, I document how to use the APIs in general. The documentation is mostly just
  quoting and paraphrasing the given references, but I thought it would be convenient to
  centralize all of this information in one place.
</p>

<h2>Authorization</h2>
In order to access authorized data like user data, Google API’s use 
<a href="https://tools.ietf.org/html/rfc6749">OAuth2</a>,
an authorization framework to enable third party applications
to obtain access to an HTTP service. The scope parameter controls what resources 
and operations an access token permits.
<ol>
  <li>Client application requests an access token from Google Authorization Server</li>
  <li>Authorization server sends access token to the application</li>
  <li>Application sends the access token to the Google API you’re trying to use</li>
</ol>
More information is available at 
<a href="https://developers.google.com/identity/protocols/OAuth2">
  Using Oauth 2.0 to Access Google APIs.</a>
One resource I found really useful to understand the authorization protocol was 
<a href="https://developers.google.com/api-client-library/python/guide/aaa_oauth">
  Oauth2.0 Explained</a>
<br>
In the google_api_functions module, I provide the get_credentials function,
which works as follows:
<br>
It is insecure for an application to get a user’s username and password, 
as this gives the application total access to their Google account. 
The application only needs access to a limited set of data, so it should only get 
a key to access that data. A key is held in a Credentials object. The steps 
needed to get a Credentials object are in a Flow object. 
Because keys can change over time, a Storage object is used to store/retrieve keys. 
In the authorization process, you setup and run a flow, which produces credentials 
that are then stored in the Storage. Then, the credentials can be retrieved as 
needed and applied to an httplib2.Http() object, so that HTTP requests 
will be authorized with the credentials.



