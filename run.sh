set -a
. deploys/prod.env
set +a

case $1 in
  rebuild)
    docker-compose build search_api
  ;;

  start)
    ./run.sh stop
    ./run.sh rebuild
    docker-compose up postgres redis elasticsearch search_api
  ;;
  load_es_index)
    curl  -XPUT http://localhost:9200/movies -H 'Content-Type: application/json' -d @es.schema.json
  ;;
  start_etl)
    docker-compose up etl
  ;;
  stop)
    docker-compose down -v --remove-orphans
  ;;
  *)
    echo "Use 'start' command"
esac
