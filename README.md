# SimpleReactAppScaffold
Simple scaffold with a bunch of simple features to get a basic idea going. Currently includes:
- create-react-app with typescript
- python flask API backend
- SQlite database to store users and text based data

Simple user auth is done directly with the backend (no oauth) for simplicity. Sessions are managed with uuids and passwords stored and hashed with salt.

Config:
- package.json: hostname and if hosting on a subdirectory
- constants.py: backend constants/config
- constants.tsx: hostname and frontend config

Requirements:
- npm install universal-cookie
- others