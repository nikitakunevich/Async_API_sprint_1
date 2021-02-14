
ENV_FILE="deploys/prod.env"

case $1 in
  rebuild)
    COMMAND="docker-compose build search_api"
  ;;
  start)
    COMMAND="./run.sh stop; ./run.sh rebuild; docker-compose up postgres redis elasticsearch search_api"
  ;;
  load_es_index)
    COMMAND="curl  -XPUT http://localhost:9200/movies -H 'Content-Type: application/json' -d @es.movies.schema.json \
      && curl  -XPUT http://localhost:9200/persons -H 'Content-Type: application/json' -d @es.persons.schema.json \
      && curl  -XPUT http://localhost:9200/genres -H 'Content-Type: application/json' -d @es.genres.schema.json"
  ;;
  start_etl)
    COMMAND="docker-compose up etl"
  ;;
  start-local)
    COMMAND="cd src; python3 main.py"
  ;;
  start-environment)
    COMMAND="./run.sh stop; docker-compose up -d postgres redis elasticsearch etl"
  ;;
  stop)
    COMMAND="docker-compose down -v --remove-orphans"
  ;;
  *)
    echo "Use 'start' command"
esac

shift

case $1 in
  -env|--env-file)
    ENV_FILE=$2
  ;;
esac

echo "ENV FILE - $ENV_FILE"
set -a
. $ENV_FILE
set +a

echo $COMMAND
bash -c "$COMMAND"
