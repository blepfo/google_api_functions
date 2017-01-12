# google_api_functions

Code to make it easier to use Google APIs.
The code in this repository is mostly just modified from tutorials and documentation
provided by Google. Some things had to be changed so everything would work with Python 3.
 
Below, I document how to use the APIs in general. If anything in the Usage section
doesn't make sense, be sure to read through that information.
The documentation is mostly just quoting and paraphrasing the given references, 
but I thought it would be convenient to centralize all of this information in one place.

## Usage
Somewhere in your project folder, create an `app_details.json` that has the following format:
```
{
  "APPLICATION_NAME" : "App Name",
  "CLIENT_SECRET_FILE" : "path/to/file",
  "SCOPES" : "path/to/file",
  "CREDENTIALS_PATH" : "path/to/file"
}
```
Note that the file for SCOPES should have each scope on a single line with no extra spaces.
You can then call `get_api_object(path_to_app_details.json)`. 
This will return an instance of the `Google_API` class, which contains functions intended
to simplify use of the Google APIs. When the object is constructed, an OAuth2.0 flow is
automatically initiated to get credentials. Once credentials are saved on your machine,
you can easily call the provided functions to get service objects for different APIs.

## Authorization
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
[Using Oauth 2.0 to Access Google APIs](https://developers.google.com/identity/protocols/OAuth2").

One resource I found really useful to understand the authorization protocol was 
[Oauth2.0 Explained](https://developers.google.com/api-client-library/python/guide/aaa_oauth)

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

More information to be added soon!

