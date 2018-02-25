# Housing Affordability 2018

Synthesize complex information to understand the state of housing market and promote a vision for long-term affordability.


### Setup

You'll need docker to get going. The easiest way is to download the Docker application from https://www.docker.com/community-edition#/download. Select the Mac or Windows download options.

After you install docker, you'll need to launch it. It will run in the background, and have a nice little icon (mac users, in the upper right task bar, windows users, in the lower right).

### Running

To run this application, open the directory in your shell, and run `docker-compose up`. This will download the necessary docker images, and then run the server.

### Data Migrations

All data migrations will run automatically when you run the application and will check to see if their data has already been added to Elasticsearch. If not, they will run the import, otherwise they won't. To add a new data source, write a python script that takes in some data and adds it to an Elasticsearch index. Put this file in the data-migrations folder. The name of the file before the .py should be the name of the index it will add its data to. The file jchs-data-2017.py is an example of a data migration for the JCHS 2017 State of the Nation's Housing Appendix Tables.
