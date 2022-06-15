# Generated by Django 3.2.13 on 2022-06-10 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raincell_core', '0007_auto_20220610_1046'),
    ]

    operations = [
        migrations.RunSQL(
        """
        DROP VIEW raincell_grid;
        CREATE OR REPLACE VIEW raincell_grid AS SELECT raincell_core_cell.id,
            st_envelope(st_buffer(raincell_core_cell.location, (0.025 / 2::numeric)::double precision)) AS geom
           FROM raincell_core_cell;
        """
        ),
        migrations.RunSQL(
            """
            CREATE OR REPLACE
            FUNCTION public.rain_cells_for_date(
                        z integer, x integer, y integer,
                        ref_date date default '2021-10-04')
            RETURNS bytea
            AS $$
			DECLARE
				result bytea;
			BEGIN
                WITH
                bounds AS (
                  SELECT ST_TileEnvelope(z, x, y) AS geom
                ),
				aggregated_records AS (
					SELECT cell_id, json_agg(quantiles50) AS quantiles50
					FROM (
						SELECT
							cell_id,
							recorded_day,
							json_build_object(
								recorded_day,
								json_agg(
									quantile50
								)
							) as quantiles50
						FROM raincell_core_rainrecord
						WHERE recorded_day BETWEEN ref_date::date  - '2 days'::interval AND ref_date
						GROUP BY cell_id, recorded_day
						ORDER BY recorded_day DESC
					) s
					GROUP BY cell_id
				), 
                rain_cells_aggregated_records AS (
					SELECT r.*, g.*
					FROM aggregated_records AS r RIGHT JOIN raincell_grid AS g
						ON r.cell_id=g.id
                ),
                mvtgeom AS (
                  SELECT t.id, ST_AsMVTGeom(ST_Transform(t.geom, 3857), bounds.geom) AS geom,
                    t.quantiles50
                  FROM rain_cells_aggregated_records t, bounds
                  WHERE ST_Intersects(t.geom, ST_Transform(bounds.geom, 4326))
                )
				SELECT ST_AsMVT(mvtgeom, 'default')
				INTO result
				FROM mvtgeom;

				RETURN result;
			END;
			$$
            LANGUAGE 'plpgsql'
            STABLE
            PARALLEL SAFE;
            
            COMMENT ON FUNCTION public.rain_cells_for_date IS 'Aggregates values on the 2 days preceding the given date (included). Returns MVT';
            
            
            CREATE OR REPLACE
            FUNCTION public.rain_cells_today(
                        z integer, x integer, y integer)
            RETURNS bytea
            AS $$
                SELECT public.rain_cells_for_date(z,x,y,now()::date)
            $$
            LANGUAGE 'sql'
            STABLE
            PARALLEL SAFE;
            
            COMMENT ON FUNCTION public.rain_cells_today IS 'Aggregates values on the last 2 days. Returns MVT';
            """,
        )
    ]
