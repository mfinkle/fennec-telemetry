DEFAULT_NUM_MAPPERS=16
DEFAULT_NUM_REDUCERS=4

function setup_directories {
  if [ ! -e '/mnt/telemetry' ]; then
    sudo mkdir /mnt/telemetry
    sudo chown ubuntu:ubuntu /mnt/telemetry
    mkdir /mnt/telemetry/work
  fi
}

function show_usage {
  echo "Usage: ./run -j job -f filter [OPTIONS]"
  printf "Options:\n"
  printf "\t\t -m: number of mappers (defaults to $DEFAULT_NUM_MAPPERS)\n"
  printf "\t\t -n: number of reducers (defaults to $DEFAULT_NUM_REDUCERS)\n"
}

function set_parameters {
  if (( $# < 4 )); then
    show_usage
    exit 1
  fi

  NUM_MAPPERS=$DEFAULT_NUM_MAPPERS
  NUM_REDUCERS=$DEFAULT_NUM_REDUCERS

  TEMP=`getopt j:f:m::r:: $@`
  eval set -- "$TEMP"

  while true ; do
    case "$1" in
      -j)
        JOB_NAME=$2 ;
        shift 2;;
      -f)
        FILTER_NAME=$2 ;
        shift 2;;
      -m)
        NUM_MAPPERS=$2 ;
        shift 2;;
      -r)
        NUM_REDUCERS=$2 ;
        shift 2;;
      -l)
        LOCAL=true ;
        shift ;;
      --) shift ; break ;;
      *) echo "Internal error: $1" ; exit 1 ;;
    esac
  done

  OUTPUT_FILE="/mnt/telemetry/$JOB_NAME_$FILTER_NAME_results.out"

  echo "JOB_NAME = $JOB_NAME"
  echo "FILTER_NAME = $FILTER_NAME"
  echo "NUM_MAPPERS = $NUM_MAPPERS"
  echo "NUM_REDUCERS = $NUM_REDUCERS"
  echo "LOCAL = $LOCAL"
}

function run_job {
  printf "\n------> Starting job\n"
  cd ~/telemetry-server
  python -m mapreduce.job ../fennec-telemetry/jobs/$JOB_NAME.py \
    --input-filter ../fennec-telemetry/filters/$FILTER_NAME.json \
    --num-mappers $NUM_MAPPERS \
    --num-reducers $NUM_REDUCERS \
    --data-dir /mnt/telemetry/work \
    --work-dir /mnt/telemetry/work \
    --output $OUTPUT_FILE \
    --bucket "telemetry-published-v1"

  printf "\n------> Results in $OUTPUT_FILE\n"
  cat $OUTPUT_FILE
}

set_parameters $@ &&
setup_directories &&
run_job
