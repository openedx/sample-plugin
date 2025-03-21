# A Sample Plugin

This repository contains a sample plugin for the Open edX project that aims to
provide examples for the various different plugin interfaces in the Open edX
platform.

The `frontend` folder makes use of the frontend-plugin-framework and slots to
add new components and functionality to multiple open edx frotends.

The `backend` folder will contain a python django app that can that can be
installed alongside edx-platform and makes use of the events and filters
capabilities to modify and work with existing functionality.

The `tutor` folder contains a tutor plugin that will install and setup both the
backend and frontend plugins in a deployment of tutor.

# Local Development for the Frontend Plugin w/Tutor

When developing with tutor, it's useful to use tutor to start up the rest of
the stack and then startup the specific MFE you want to develop on your local
machine.  We just need to tell tutor to not start the specific MFE as a part of
the tutor-mfe plugin.

```
# Example using the `learner-dashboard` MFE
# Tell tutor to start this MFE in dev mode
tutor dev start learner-dashbard
tutor dev launch

# Go to the `profile` MFE folder locally.
# TODO Edits needed to load our plugin locally.

# Start up the service
npm ci
npm start dev
```
