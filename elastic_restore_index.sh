#!/bin/bash

#Восстанавливаем индекс elastic
sudo docker-compose exec -T elasticcinema01 backup/restore_current_index.sh
