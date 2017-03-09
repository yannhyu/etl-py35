# etl-design for python3.5

to scale up:
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
airflow@mllxv-yu:~/workspace/etl-design$ docker-compose-1.9.0 up -d
Creating network "etldesign_default" with the default driver
Creating etldesign_redis_1
Creating etldesign_monitor_1
Creating etldesign_web_1
Creating etldesign_worker_1
airflow@mllxv-yu:~/workspace/etl-design$ docker-compose-1.9.0 scale worker=3
Creating and starting etldesign_worker_2 ... done
Creating and starting etldesign_worker_3 ... done

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# for jupyter notebook, use etl

psql:
(1) \COPY [ some db table] TO '/tmp/some_tbl.csv' WITH (FORMAT CSV, HEADER)
(2) create table in new db
(3) \COPY [ new table in new db] FROM '/tmp/some_tbl.csv' DELIMITER ',' CSV HEADER

