DEFAULT_NUM_MAPPERS=16
DEFAULT_NUM_REDUCERS=4

TODAY=$(date +%Y%m%d)

function setup_directories {
  if [ ! -d "/mnt/telemetry" ]; then
    sudo mkdir "/mnt/telemetry"
    sudo chown ubuntu:ubuntu "/mnt/telemetry"
  fi

  if [ ! -d "/mnt/telemetry/work/cache" ]; then
    mkdir -p "/mnt/telemetry/work/cache"
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
  printf "\t -d,  target submission date (defaults to yesterday)\n"
  printf "\t -p,  force to redownload data from S3 (takes longer)\n"
  printf "\t -s,  show the command to be run, without actually running\n"
  exit 1
}

function set_defaults {
  NUM_MAPPERS=$DEFAULT_NUM_MAPPERS
  NUM_REDUCERS=$DEFAULT_NUM_REDUCERS
  TARGET_DATE=$(date -d 'yesterday' +%Y%m%d)

  if [ -d "/mnt/telemetry/work/cache/saved_session" ]; then
    PULL="--local-only"
  else
    PULL=""
  fi
}

function set_parameters {
  set_defaults

  TEMP=`getopt j:f:d:m::r::phsx $@`
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
      -d)
        TARGET_DATE=$2
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
      -x)
        HEADER_NAME=$JOB_NAME
        shift
        ;;
      --) shift ; break ;;
      *) echo "Internal error: $1" ; exit 1 ;;
    esac
  done

  if [ ! -n "$JOB_NAME" -o ! -n "$FILTER_NAME" ]; then
    show_usage
  fi

  OUTPUT_FILE="/mnt/telemetry/"$JOB_NAME"_"$FILTER_NAME".txt"

  echo "Today is $TODAY, and we're using data from $TARGET_DATE"
  sed -i.bak "s/__TARGET_DATE__/$TARGET_DATE/" ./fennec-telemetry/filters/$FILTER_NAME.json

  echo "JOB_NAME = $JOB_NAME"
  echo "FILTER_NAME = $FILTER_NAME"
  echo "HEADER_NAME = $HEADER_NAME"
  echo "NUM_MAPPERS = $NUM_MAPPERS"
  echo "NUM_REDUCERS = $NUM_REDUCERS"
  echo "PULL = $PULL"
}

function run_job {
  COMMAND="python -m mapreduce.job ../fennec-telemetry/jobs/$JOB_NAME.py \
    --input-filter ../fennec-telemetry/filters/$FILTER_NAME.json \
    --num-mappers $NUM_MAPPERS \
    --num-reducers $NUM_REDUCERS \
    --data-dir /mnt/telemetry/work/cache \
    --work-dir /mnt/telemetry/work \
    --output $OUTPUT_FILE \
    --bucket \"telemetry-published-v2\" \
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
    if [ $HEADER_NAME ]; then
      cp ../fennec-telemetry/headers/$HEADER_NAME.txt /mnt/telemetry/$JOB_NAME.csv
      cat $OUTPUT_FILE >> /mnt/telemetry/$JOB_NAME.csv
    fi
  fi
}

set_parameters $@ &&
run_job
