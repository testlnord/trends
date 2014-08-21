
CREATE TABLE IF NOT EXISTS techs (
  id SERIAL PRIMARY KEY ,
  info json);

CREATE TABLE IF NOT EXISTS sources (
  name varchar(10),
  config json
);

CREATE TABLE IF NOT EXISTS rawdata(
  source varchar,
  tech_id integer references techs(id),
  time timestamp,
  value integer
);

CREATE TABLE IF NOT EXISTS reports_1(
  source varchar,
  tech_id integer references techs(id),
  time timestamp,
  value real
);

CREATE TABLE IF NOT EXISTS reports_2(
  tech_id integer references techs(id),
  time timestamp,
  value real
);

