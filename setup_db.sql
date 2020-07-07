create schema stations;

grant usage on schema "stations" to "docker";
grant all privileges  on all tables in schema "stations" to "docker";

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA "stations" TO "docker";

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA "stations" TO "docker";

create extension postgis;

CREATE EXTENSION postgis SCHEMA stations;

UPDATE pg_extension
  SET extrelocatable = TRUE
    WHERE extname = 'postgis';

ALTER EXTENSION postgis
  SET SCHEMA stations;


create table stations.station
(
    id             bytea not null
        constraint station_pkey
            primary key,
    data_source    varchar(500),
    operator       varchar(500),
    payment        varchar(500),
    authentication varchar(500),
    coordinates    stations.geometry(Point),
    raw_data       varchar
);

alter table stations.station
    owner to docker;

create index ix_station_id
    on stations.station (id);

create index idx_station_coordinates
    on stations.station (coordinates);

create table stations.address
(
    station_id bytea not null
        constraint address_pkey
            primary key
        constraint address_station_id_fkey
            references stations.station
            on update cascade on delete cascade,
    street     varchar(500),
    town       varchar(500),
    postcode   varchar(500),
    district   varchar(500),
    state      varchar(500),
    country    varchar(500)
);

alter table stations.address
    owner to docker;

create index ix_address_station_id
    on stations.address (station_id);

create table stations.charging
(
    station_id       bytea not null
        constraint charging_pkey
            primary key
        constraint charging_station_id_fkey
            references stations.station
            on update cascade on delete cascade,
    capacity         integer,
    kw_list          double precision[],
    ampere_list      double precision[],
    volt_list        double precision[],
    socket_type_list character varying[],
    dc_support       boolean,
    total_kw         double precision,
    max_kw           double precision
);

alter table stations.charging
    owner to docker;

create index ix_charging_station_id
    on stations.charging (station_id);


ALTER TABLE stations.station
  ALTER COLUMN coordinates
    TYPE geometry(Point, 4326)
    USING ST_SetSRID(coordinates, 4326);
