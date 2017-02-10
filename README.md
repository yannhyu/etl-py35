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


