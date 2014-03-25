fennec-telemetry
================

MapReduce jobs to be run on mozilla/telemetry-server for grabbing fennec telemetry.

To run a MapReduce job:

1. Visit http://telemetry-dash.mozilla.org/ and launch a worker with your public SSH key
1. Login to machine with SSH command given (wait about 5 mins for keys to propogate)
1. Clone this repo in the home directory and run the job:
```shell
$ git clone https://github.com/gerfuls/fennec-telemetry.git
# with my_job.py and my_filter.json as files in jobs/ and filters/
$ ./fennec-telemetry/run.sh -j my_job -f my_filter
```
1. Wait
1. Get results!

See all options: `./fennec-telemetry/run.sh -h`

Make a pull request if you would like to add a new job or filter!

## Useful Links
- [AustralisTelemetry](https://github.com/bwinton/AustralisTelemetry)
- [mreid's blog](http://mreid-moz.github.io/blog/2013/11/06/current-state-of-telemetry-analysis/)
- [MapReduce Docs](https://github.com/mozilla/telemetry-server/blob/master/docs/MapReduce.md)
