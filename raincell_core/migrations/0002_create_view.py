# Generated by Django 3.2.13 on 2022-06-08 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raincell_core', '0001_initial'),
    ]

    # Create function returning Vector Tiles, to be used with pg_tileserv
    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE
            FUNCTION public.rain_cells_for_date(
                        z integer, x integer, y integer,
                        ref_date date default '2021-10-04')
            RETURNS bytea
            AS $$
                WITH
                bounds AS (
                  SELECT ST_TileEnvelope(z, x, y) AS geom
                ),
                rain_cells AS (
                    SELECT cell_id, ST_envelope(ST_buffer(location, 0.025/2)) AS geom, json_agg(quantiles50) AS quantiles50
                    FROM (
                        SELECT
                            cell_id,
                            location,
                            recorded_day,
                            json_build_object(
                                recorded_day,
                                json_agg(
                                    quantile50
                                )
                            ) as quantiles50
                        FROM raincell_core_cellrecord
                        WHERE recorded_day BETWEEN ref_date  - '2 days'::interval AND ref_date
                        GROUP BY cell_id, location, recorded_day
                        ORDER BY recorded_day DESC
            
                    ) s
                    GROUP BY cell_id, location
                ),
                mvtgeom AS (
                  SELECT t.cell_id, ST_AsMVTGeom(ST_Transform(t.geom, 3857), bounds.geom) AS geom,
                    t.quantiles50
                  FROM rain_cells t, bounds
                  WHERE ST_Intersects(t.geom, ST_Transform(bounds.geom, 4326))
                )
                SELECT ST_AsMVT(mvtgeom, 'public.rain_cells_for_date') FROM mvtgeom;
            $$
            LANGUAGE 'sql'
            STABLE
            PARALLEL SAFE;
            
            COMMENT ON FUNCTION public.rain_cells_for_date IS 'Aggregates values on the 2 days preceding the given date (included). Returns MVT';
            
            
            CREATE OR REPLACE
            FUNCTION public.rain_cells_today(
                        z integer, x integer, y integer)
            RETURNS bytea
            AS $$
                SELECT public.rain_cells_for_date(x,y,z,now()::date)
            $$
            LANGUAGE 'sql'
            STABLE
            PARALLEL SAFE;
            
            COMMENT ON FUNCTION public.rain_cells_today IS 'Aggregates values on the last 2 days. Returns MVT';
            """,

        )
    ]
