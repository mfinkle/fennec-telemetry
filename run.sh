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
  echo "Usage: $0 -j job -f filter [OPTIONS]"
  printf "Options:\n"
  printf "\t -h,  show this dialog\n"
  printf "\t -j,  job name\n"
  printf "\t -f,  filter name\n"
  printf "\t -m,  number of mappers (defaults to $DEFAULT_NUM_MAPPERS)\n"
  printf "\t -r,  number of reducers (defaults to $DEFAULT_NUM_REDUCERS)\n"
  printf "\t -p,  force to redownload data from S3 (takes longer)\n"
  printf "\t -s,  show the command to be run, without actually running\n"
  exit 1
}

function set_defaults {
  NUM_MAPPERS=$DEFAULT_NUM_MAPPERS
  NUM_REDUCERS=$DEFAULT_NUM_REDUCERS

  if [ -d "/mnt/telemetry/cache/saved_session" ]; then
    PULL="--local-only"
  else
    PULL=""
  fi
}

function set_parameters {
  set_defaults

  TEMP=`getopt j:f:m::r::phs $@`
  eval set -- "$TEMP"

  while true ; do
    case "$1" in
      -j)
        JOB_NAME=$2
        shift 2
        ;;
      -f)
        FILTER_NAME=$2
        shift 2
        ;;
      -m)
        NUM_MAPPERS=$2
        shift 2
        ;;
      -r)
        NUM_REDUCERS=$2
        shift 2
        ;;
      -p)
        PULL=""
        shift
        ;;
      -h)
        show_usage
        ;;
      -s)
        SIMULATE=true
        shift
        ;;
      --) shift ; break ;;
      *) echo "Internal error: $1" ; exit 1 ;;
    esac
  done

  if [ ! -n "$JOB_NAME" -o ! -n "$FILTER_NAME" ]; then
    show_usage
  fi

  OUTPUT_FILE="/mnt/telemetry/"$JOB_NAME"_"$FILTER_NAME"_results.out"

  echo "JOB_NAME = $JOB_NAME"
  echo "FILTER_NAME = $FILTER_NAME"
  echo "NUM_MAPPERS = $NUM_MAPPERS"
  echo "NUM_REDUCERS = $NUM_REDUCERS"
  echo "PULL = $PULL"
}

function run_job {
  COMMAND="python -m mapreduce.job ../fennec-telemetry/jobs/$JOB_NAME.py \
    --input-filter ../fennec-telemetry/filters/$FILTER_NAME.json \
    --num-mappers $NUM_MAPPERS \
    --num-reducers $NUM_REDUCERS \
    --data-dir /mnt/telemetry/work \
    --work-dir /mnt/telemetry/work \
    --output $OUTPUT_FILE \
    --bucket \"telemetry-published-v1\" \
    $PULL"

  if [ $SIMULATE ]; then
    printf "\n------> Simluating job\n"
    echo $COMMAND
  else
    printf "\n------> Starting job\n"
    setup_directories
    cd ~/telemetry-server
    eval $COMMAND
    printf "\n------> Results in $OUTPUT_FILE\n"
    cat $OUTPUT_FILE
  fi
}

set_parameters $@ &&
run_job
