# Cloud computing bill management system restapi 

The bill management system will be used to track the bills and vendor specific management system.
There is no UI forms in the project and is meant to be reference for a backend application



**We will be using python based flask module for developing web rest api. Prior knowledge to flask development is needed**


## How does it work????

There are certain requirements to be met 

1. You need to install database server postgres for the application to work.

2. Install from requirments.txt  to add the dependency to the project

3. prior knowledge of sqlmarshmallow working is required since we will be using ORMS dor database communication

### Continuous integreation using Circle CI
 we will be using conytinuous integration by circle ci platform. Make your github account linked with it.

1. You need to enable 3rd party access on your github account for circle ci to work

2. Import your github project in circle ci account to build test and workflows
3. yaml file is include , make appropriate changes accorting to your environment. We have used ubuntu docker and postgres image.
