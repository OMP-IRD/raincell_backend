# Raincell Backend
This is the backend application for the raincell demonstration portal.
It defines:
- the import functions, to import raincell data into the postgis database
- the API endpoinds to expose this data
- the postgresql functions that allow to expose the raincell data as MVT, using pg_tileserv

## Run the app

### Dev environment
This is a geodjango application, placed under app/ subfolder.

- install geodjango requirements. For instance on debian:
```bash
apt-get install -y --no-install-recommends \
        binutils \
        libproj-dev \
        gdal-bin \
        postgresql \
        postgis
```
- it uses docker to start complementary apps (postgis, pg_tileserv). 
You will need to install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/). 
- Install dependencies:
`pip install -r /src/requirements.txt`
- Start the docker compo
```bash
docker-compose -f docker-compose-dev.yml up -d
```
- Apply the django model to the brand new DB:
```bash
./src/manage.py makemigrations
```
- Start the development server
```bash
./src/manage.py runserver
```
- Test the API. You can use the [swagger UI](http://localhost:8000/api/schema/swagger-ui/)


## Docker build
```bash
docker build -t pigeosolutions/raincell_backend:latest .
```

## Run with docker
- Start the docker dev compo to run the dependencies
```bash
docker-compose -f docker-compose-dev.yml up -d
```
- Start the django app:
```
docker run --rm -p 8001:8000 --name raincell_backend \
            -v $(pwd)/sample_data:/sample_data \
            -e POSTGRES_HOST=$(hostname -I | grep -o "^[0-9.]*") \
            -e POSTGRES_PORT=5432  \
            pigeosolutions/raincell_backend:latest
```
- Import data. You can either import the sample dataset directly using the DB dump, or import your data using the app's import commands. 
  - Using the DB dump, for a quick setup:
    The database's port is binded to localhost, so if you have psql client installed on your computer, you can run
    ```
    gunzip < sample_data/cameroun/raincell_samples.sql.gz | psql -U postgres -d raincell -h localhost -p 5432 
    ```
  - Using the app's import tools:
    - Import the mask netcdf file (defines the grid cells to be served)
    ```bash
    # Import the geospatial grid cells, using the netcdf mask
    docker exec raincell_backend /app/manage.py raincell_generate_cells /sample_data/cameroun/Raincell_masque_Cameroun.nc
    ```
    
    - Import some raincell netcdf data. You can either use `manage.py raincell_import_file` command, to import just one file, 
    or `manage.py raincell_batch_import` to import all files from a folder. For instance
    ```bash
    # Batch import
    docker exec raincell_backend /app/manage.py raincell_batch_import /sample_data/cameroun/samples/
    # or single file import
    #docker exec raincell_backend /app/manage.py raincell_import_file /sample_data/cameroun/samples/20211003_2355_Raincell_Cameroun_InvRainResol-2.5km.nc.aux.xml
    ```

    - alternatively, you can generate some fake data (but you will still need to have generated the cells, see the previous step):
    ```bash
    # Batch import
    docker exec raincell_backend /app/manage.py raincell_generate_fake_data --verbose --overwrite_existing 2022-05-01 2022-06-14
    ```

It will expose the following services:
- API on http://localhost:8001/api/v1 and its related swagger UI on http://localhost:8001/api/schema/swagger-ui/
- MVT services on http://localhost:7800/tiles/. The interesting service here being the **rain_cells_for_date** function:
it exposes the raincell grid, with data from last 2 days


## About Raincell
Raincell is a project piloted by OMP-IRD, aiming to determine near real-time rain data, based on cell-towers' data. 
More about Raincell: 
TODO: link to informational website
