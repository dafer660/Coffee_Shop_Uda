export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'ferreiratech.eu.auth0.com', // the auth0 domain prefix
    audience: 'ferreiratech', // the audience set for the auth0 app
    clientId: '4dNGxe7ibww71BoxWxeh1qjTD7Eb2FNV', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application.
  }
};
