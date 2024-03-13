CREATE TABLE locations(
    location_name varchar(1000) not null,
    latitude float8 not null,
    longitude float8 not null,
    primary key (location_name)
);
